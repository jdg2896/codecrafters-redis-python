import asyncio
from typing import Awaitable, Callable

from app.config import server_config
from app.constants import CRLF
from app.types import DataStore
from app.utils import send, to_resp_array, to_resp_bulk_string

Dispatch = Callable[[bytes, list[bytes], DataStore], Awaitable[bytes]]


async def _send_and_read_line(
    reader: asyncio.StreamReader,
    writer: asyncio.StreamWriter,
    *parts: bytes,
) -> bytes:
    """Send a RESP command and read back a single CRLF-terminated reply line.

    Suitable for handshake replies like +PONG / +OK that fit on one line.
    """
    await send(writer, to_resp_array([to_resp_bulk_string(p) for p in parts]))
    return await reader.readuntil(CRLF)


async def _read_resp_array(reader: asyncio.StreamReader) -> list[bytes]:
    """Parse one RESP array of bulk strings off the stream.

    Uses readuntil/readexactly so it never over-consumes — leaving subsequent
    commands intact in the buffer for the next call.
    """
    header = await reader.readuntil(CRLF)
    count = int(header[1:-2])
    parts: list[bytes] = []
    for _ in range(count):
        bulk_header = await reader.readuntil(CRLF)
        length = int(bulk_header[1:-2])
        parts.append(await reader.readexactly(length))
        await reader.readexactly(2)  # trailing CRLF
    return parts


async def handshake_with_master(
    replica_of: str, port: int
) -> tuple[asyncio.StreamReader, asyncio.StreamWriter]:
    """Connect to the master and complete PING / REPLCONF / PSYNC handshake.

    Returns the open (reader, writer) so the caller can keep consuming the
    propagation stream. The connection is intentionally NOT closed here.
    """
    print("Start handshake with master server:", replica_of)
    master_host, master_port = replica_of.split()
    reader, writer = await asyncio.open_connection(master_host, int(master_port))

    response = await _send_and_read_line(reader, writer, b"PING")
    print("PING response from master:", response)

    response = await _send_and_read_line(
        reader, writer, b"REPLCONF", b"listening-port", str(port).encode()
    )
    print("REPLCONF listening-port response from master:", response)

    response = await _send_and_read_line(
        reader, writer, b"REPLCONF", b"capa", b"psync2"
    )
    print("REPLCONF capa psync2 response from master:", response)

    # PSYNC response is FULLRESYNC line + RDB payload ($<len>\r\n<bytes>) with no
    # trailing CRLF after the RDB. Read these explicitly so we don't over-consume
    # into the propagation stream that follows.
    await send(
        writer,
        to_resp_array([to_resp_bulk_string(p) for p in (b"PSYNC", b"?", b"-1")]),
    )
    fullresync = await reader.readuntil(CRLF)
    print("PSYNC FULLRESYNC line:", fullresync)
    rdb_header = await reader.readuntil(CRLF)
    rdb_length = int(rdb_header[1:-2])
    await reader.readexactly(rdb_length)
    print("Received RDB of length:", rdb_length)

    return reader, writer


async def process_propagated(
    reader: asyncio.StreamReader,
    data_store: DataStore,
    dispatch: Dispatch,
) -> None:
    """Apply commands propagated from master to the local data store.

    Replicas do not respond to the master for ordinary writes — we drop the
    dispatch return value. (REPLCONF GETACK will be the future exception.)
    """
    while not reader.at_eof():
        try:
            parts = await _read_resp_array(reader)
        except asyncio.IncompleteReadError:
            break
        if not parts:
            continue
        command, args = parts[0].upper(), parts[1:]
        print("Received propagated command from master:", command, args)
        await dispatch(command, args, data_store)


async def propagate(command: bytes, args: list[bytes]) -> None:
    """Forward a write command to every connected replica.

    Replicas that error on send (e.g. dropped connection) are removed from the set.
    """
    payload = to_resp_array([to_resp_bulk_string(p) for p in [command, *args]])
    for replica_writer in list(server_config["replicas"]):
        try:
            await send(replica_writer, payload)
        except OSError:
            server_config["replicas"].discard(replica_writer)
