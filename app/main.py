# import socket
import asyncio

PING = b"*1\r\n$4\r\nPING\r\n"
PONG = b"+PONG\r\n"
ECHO = b"*2\r\n$4\r\nECHO\r\n"

async def main():
    print("Starting Redis server on localhost:6379...")
    server = await asyncio.start_server(_handle_client, "localhost", 6379)

    print("Waiting for client connections...")
    async with server:
        await server.serve_forever()


async def _handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    print("Client connected:", _get_client_address(writer))
    while True:
        data = await reader.read(1024)
        if not data:
            break

        command = _parse_command(data)
        print("Received command from client:", _get_client_address(writer), "Command:", command)

        response = _handle_command(command)
        print("Sending response to client:", _get_client_address(writer), "Response:", response)
        writer.write(response)
        await writer.drain()

    writer.close()
    await writer.wait_closed()
    print("Client disconnected:", _get_client_address(writer))


def _parse_command(data: bytes):
    if data.startswith(PING):
        return "PING"
    elif data.startswith(ECHO):
        return "ECHO", data[len(ECHO):].strip()
    else:
        return None


def _handle_command(command: str | tuple | None):
    if command == "PING":
        return PONG
    elif isinstance(command, tuple) and command[0] == "ECHO":
        return command[1] + b"\r\n"
    else:
        return b"-ERR unknown command\r\n"


def _get_client_address(writer: asyncio.StreamWriter):
    return writer.get_extra_info("peername")


if __name__ == "__main__":
    asyncio.run(main())
