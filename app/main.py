# import socket
import asyncio

PING = b"*1\r\n$4\r\nPING\r\n"
PONG = b"+PONG\r\n"

async def main():
    print("Starting Redis server on localhost:6379...")
    server = await asyncio.start_server(_handle_client, "localhost", 6379)

    print("Waiting for client connections...")
    async with server:
        await server.serve_forever()


async def _handle_client(reader, writer):
    data = await reader.read(1024)   # non-blocking
    print(f"Received data: {data!r}")
    if data == PING:
        writer.write(PONG)
        await writer.drain()
    writer.close()


if __name__ == "__main__":
    asyncio.run(main())
