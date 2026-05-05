import asyncio

from app.config import server_config
from app.utils import send, to_resp_array, to_resp_bulk_string


async def send_command(
    reader: asyncio.StreamReader,
    writer: asyncio.StreamWriter,
    *parts: bytes,
) -> bytes:
    await send(writer, to_resp_array([to_resp_bulk_string(p) for p in parts]))
    return await reader.read(1024)


async def handshake_with_master(replica_of: str, port: int) -> None:
    print("Start handshake with master server:", replica_of)
    master_host, master_port = replica_of.split()
    reader, writer = await asyncio.open_connection(master_host, int(master_port))
    try:
        response = await send_command(reader, writer, b"PING")
        print("PING response from master:", response)

        response = await send_command(
            reader, writer, b"REPLCONF", b"listening-port", str(port).encode()
        )
        print("REPLCONF listening-port response from master:", response)

        response = await send_command(reader, writer, b"REPLCONF", b"capa", b"psync2")
        print("REPLCONF capa psync2 response from master:", response)

        response = await send_command(reader, writer, b"PSYNC", b"?", b"-1")
        print("PSYNC response from master:", response)
    finally:
        writer.close()
        await writer.wait_closed()


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
