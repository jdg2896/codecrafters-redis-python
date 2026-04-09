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


async def _handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    print("Client connected:", writer.get_extra_info("peername"))
    while True:
        data = await reader.read(1024)
        if not data:
            break
        if data.startswith(PING):
            print("Received PING from client:", writer.get_extra_info("peername"))
            print("Sending PONG to client:", writer.get_extra_info("peername"))
            writer.write(PONG)
            await writer.drain()
    writer.close()
    await writer.wait_closed()
    print("Client disconnected:", writer.get_extra_info("peername"))


if __name__ == "__main__":
    asyncio.run(main())
