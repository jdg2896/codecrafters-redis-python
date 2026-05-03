import asyncio

from app.constants import CRLF
from app.types import DataStore
from app.utils import get_client_address
from app.commands import (
    blpop,
    llen,
    lpop,
    lpush,
    ping,
    echo,
    set,
    get,
    rpush,
    lrange,
    type as type_command, # type is a reserved keyword, so we import it as type_command
    xadd,
    xrange,
    xread,
    incr,
)


# In-memory data store for SET and GET commands
data_store: DataStore = {}


async def main():
    '''Start the Redis server and handle incoming client connections using the asyncio event loop.'''
    print("Starting Redis server on localhost:6379...")
    server = await asyncio.start_server(_handle_client, "localhost", 6379)

    print("Waiting for client connections...")
    async with server:
        await server.serve_forever()


async def _handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    '''Handle an incoming client connection, read commands from the client, and send responses back to the client.'''
    client_address = get_client_address(writer)
    print("Client connected:", client_address)
    while True:
        data = await reader.read(1024)
        if not data:
            break

        response = await _handle_command(data, client_address)
        print("Sending response to client:", client_address, "Response:", response)
        writer.write(response)
        await writer.drain()

    writer.close()
    await writer.wait_closed()
    print("Client disconnected:", client_address)


async def _handle_command(data: bytes, client_address: str) -> bytes:
    '''Execute a Redis command from raw RESP data and return the response.

    Parses the RESP-encoded data, looks up the command handler, and returns the response bytes.
    Returns an error response if the data is malformed or the command is unknown.

    Assuming the received command is in correct RESP format, here's how the data will be parsed:
    
    For PING: data.split(CRLF) will yield [b'*1', b'$4', b'PING', b'']
    - parts[0] = *N (array count)
    - parts[1] = $N (command length)
    - parts[2] = command name

    For ECHO and other commands with arguments: data.split(CRLF) will yield [b'*2', b'$4', b'ECHO', b'$N', b'argument', ...]
    - parts[0] = *N (array count)
    - parts[1] = $N (command length)
    - parts[2] = command name
    - parts[3] = $N (argument length)
    - parts[4] = argument
    - ... and so on for additional arguments
    '''
    # Parse the command and arguments from the incoming data
    parts = data.split(CRLF)
    if len(parts) < 3:
        return b"-ERR invalid command\r\n"
    command = parts[2]
    args = parts[4::2]

    print("Received command from client:", client_address, "Command:", command, "Arguments:", args)
    COMMAND_HANDLERS = {
        b'PING': ping.handle,
        b'ECHO': echo.handle,
        b'SET': set.handle,
        b'GET': get.handle,
        b'RPUSH': rpush.handle,
        b'LRANGE': lrange.handle,
        b'LPUSH': lpush.handle,
        b'LLEN': llen.handle,
        b'LPOP': lpop.handle,
        b'BLPOP': blpop.handle,
        b'TYPE': type_command.handle,
        b'XADD': xadd.handle,
        b'XRANGE': xrange.handle,
        b'XREAD': xread.handle,
        b'INCR': incr.handle,
    }
    handler = COMMAND_HANDLERS.get(command)
    if handler:
        result = handler(args, data_store)
        if asyncio.iscoroutine(result):
            return await result
        return result

    return b"-ERR unknown command\r\n"


if __name__ == "__main__":
    asyncio.run(main())
