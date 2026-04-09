import asyncio
import time

# Constants for Redis protocol
PONG = b"+PONG\r\n"
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
    '''Parse the incoming data from the client and determine which Redis command is being executed.
    
    If the command is recognized, return a tuple containing the command name and any arguments. 
    
    If the command is not recognized, return None.

    Assuming the received command is in correct RESP format, here's how the command will be parsed:
    
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
    parts = data.split(CRLF)
    command = parts[2] if len(parts) > 2 else None
    args = parts[4::2] 

    if command == b'PING':
        return "PING"
    elif command == b'ECHO':
        return "ECHO", args
    elif command == b'SET':
        return "SET", args
    elif command == b'GET':
        return "GET", args
    else:
        return None


def _handle_command(command: str | tuple | None):
    if command == "PING":
        return PONG
    elif isinstance(command, tuple) and command[0] == "ECHO":
        if len(command[1]) != 1:
            return b"-ERR wrong number of arguments for 'ECHO' command\r\n"
        return _to_bulk_string(command[1][0])
    elif isinstance(command, tuple) and command[0] == "SET":
        key = command[1][0]
        value = command[1][1]
        expiry_unit = command[1][2] if len(command[1]) > 2 else None
        expiry_value = command[1][3] if len(command[1]) > 3 else None

        # Handle optional expiry parameters
        expires_at = _set_expiry(key, expiry_unit, expiry_value)

        data_store[key] = (value, expires_at)

        return OK
    elif isinstance(command, tuple) and command[0] == "GET":
        key = command[1][0]
        value = data_store.get(key)
        if value is not None and (value[1] is None or value[1] > time.time()):
            return _to_bulk_string(value[0])
        else:
            return NIL
    else:
        return b"-ERR unknown command\r\n"


def _set_expiry(key: bytes, expiry_unit: bytes | None, expiry_value: int | None):
    '''Returns the expiry time for a key in the data store. 
    
    The expiry time can be specified in milliseconds (PX) or seconds (EX).'''
    try:
        expires_at = None
        if expiry_unit and expiry_value:
            ms = int(expiry_value)
            if expiry_unit == b'PX':
                expires_at = time.time() + ms / 1000
            elif expiry_unit == b'EX':
                expires_at = time.time() + ms
        
        return expires_at
    except ValueError:
        return b"-ERR invalid expiry time\r\n"


# Helper functions
def _get_client_address(writer: asyncio.StreamWriter):
    return writer.get_extra_info("peername")


def _to_bulk_string(data: bytes):
    return b"$" + str(len(data)).encode() + CRLF + data + CRLF


if __name__ == "__main__":
    asyncio.run(main())
