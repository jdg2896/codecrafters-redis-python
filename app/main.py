import asyncio
from calendar import c

from app.constants import CRLF, OK, QUEUED
from app.types import DataStore
from app.utils import get_client_address, to_resp_array, to_resp_error
from app.commands import COMMAND_HANDLERS

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
    connection = {
        "in_multi": False,
        "queue": [],
        "watched_keys": [],
    }  # per-connection state
    print("Client connected:", client_address)
    while True:
        data = await reader.read(1024)
        if not data:
            break

        response = await _handle_command(data, client_address, connection)
        print("Sending response to client:", client_address, "Response:", response)
        writer.write(response)
        await writer.drain()

    writer.close()
    await writer.wait_closed()
    print("Client disconnected:", client_address)


async def _handle_command(data: bytes, client_address: str, connection: dict) -> bytes:
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
        return to_resp_error(b"ERR invalid command")
    command = parts[2]
    args = parts[4::2]

    print("Received command from client:", client_address, "Command:", command, "Arguments:", args)

    if command.upper() == b'MULTI':
        connection["in_multi"] = True
        connection["queue"] = []
        return OK

    if connection["in_multi"]:
        if command.upper() == b'EXEC':
            connection["in_multi"] = False
            results = []
            for queued_cmd, queued_args in connection["queue"]:
                results.append(await _dispatch(queued_cmd, queued_args, data_store))
            connection["queue"] = []
            return to_resp_array(results)
        elif command.upper() == b'DISCARD':
            connection["in_multi"] = False
            connection["queue"] = []
            return OK
        elif command.upper() == b'WATCH':
            return to_resp_error(b"ERR WATCH inside MULTI is not allowed")
        else:
            connection["queue"].append((command, args))
            return QUEUED

    if command.upper() == b'EXEC':
        return to_resp_error(b"ERR EXEC without MULTI")
    
    if command.upper() == b'DISCARD':
        return to_resp_error(b"ERR DISCARD without MULTI")
    
    if command.upper() == b'WATCH':
        watched_keys = connection.get("watched_keys", [])
        watched_keys.extend(args)
        connection["watched_keys"] = watched_keys
        return OK

    return await _dispatch(command, args, data_store)


async def _dispatch(command: bytes, args: list[bytes], data_store: DataStore) -> bytes:
    handler = COMMAND_HANDLERS.get(command)
    if handler:
        result = handler(args, data_store)
        if asyncio.iscoroutine(result):
            return await result
        return result
    return to_resp_error(b"ERR unknown command")


if __name__ == "__main__":
    asyncio.run(main())
