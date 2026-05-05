import asyncio

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
    finally:
        writer.close()
        await writer.wait_closed()
