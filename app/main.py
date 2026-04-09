import asyncio

# Constants for Redis protocol
PING = b"*1\r\n$4\r\nPING\r\n"
PONG = b"+PONG\r\n"
ECHO = b"*2\r\n$4\r\nECHO\r\n"
SET = b"*3\r\n$3\r\nSET\r\n"
GET = b"*2\r\n$3\r\nGET\r\n"
OK = b"+OK\r\n"
NIL = b"$-1\r\n"
CRLF = b"\r\n"

# In-memory data store for SET and GET commands
data_store = {}

async def main():
    '''Start the Redis server and handle incoming client connections using the asyncio event loop.'''
    print("Starting Redis server on localhost:6379...")
    server = await asyncio.start_server(_handle_client, "localhost", 6379)

    print("Waiting for client connections...")
    async with server:
        await server.serve_forever()


async def _handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    '''Handle an incoming client connection, read commands from the client, and send responses back to the client.'''
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
    elif data.startswith(SET):
        return "SET", data[len(SET):].strip()
    elif data.startswith(GET):
        return "GET", data[len(GET):].strip()
    else:
        return None


def _handle_command(command: str | tuple | None):
    if command == "PING":
        return PONG
    elif isinstance(command, tuple) and command[0] == "ECHO":
        return command[1] + CRLF
    elif isinstance(command, tuple) and command[0] == "SET":
        key, value = command[1].split(b" ", 1)
        data_store[key] = value
        return OK
    elif isinstance(command, tuple) and command[0] == "GET":
        key = command[1]
        value = data_store.get(key)
        if value is not None:
            return value + CRLF
        else:
            return NIL
    else:
        return b"-ERR unknown command\r\n"


def _get_client_address(writer: asyncio.StreamWriter):
    return writer.get_extra_info("peername")


if __name__ == "__main__":
    asyncio.run(main())
