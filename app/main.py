import argparse
import asyncio

from app import replication, transaction
from app.commands import COMMAND_HANDLERS, WRITE_COMMANDS, psync
from app.config import server_config
from app.constants import CRLF
from app.types import DataStore
from app.utils import get_client_address, send, to_resp_error

# In-memory data store for SET and GET commands
data_store: DataStore = {}


async def main(port: int, replica_of: str | None) -> None:
    """Start Redis server and accept client connections using asyncio event loop."""
    print(f"Starting Redis server on localhost:{port}...")
    server = await asyncio.start_server(_handle_client, "localhost", port)

    print("Server configuration:", {"port": port, "replica_of": replica_of})
    server_config["replica_of"] = replica_of
    if replica_of:
        server_config["role"] = "slave"
        await replication.handshake_with_master(replica_of, port)

    print("Server started. Waiting for client connections...")
    async with server:
        await server.serve_forever()


async def _handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    """Handle incoming client connection, read commands, and respond to client."""
    client_address = get_client_address(writer)
    connection = transaction.new_connection_state()
    connection["writer"] = writer
    print("Client connected:", client_address)
    try:
        while True:
            data = await reader.read(1024)
            if not data:
                break

            response = await _handle_command(data, client_address, connection)
            print("Sending response to client:", client_address, "Response:", response)
            await send(writer, response)
    finally:
        server_config["replicas"].discard(writer)
        writer.close()
        await writer.wait_closed()
        print("Client disconnected:", client_address)


async def _handle_command(data: bytes, client_address: str, connection: dict) -> bytes:
    """Execute a Redis command from raw RESP data and return the response.

    Parses the RESP-encoded data, processes command, and returns the response bytes.
    Returns an error response if the data is malformed or the command is unknown.

    When received command is in correct RESP format, here's how the data is parsed:

    For PING: data.split(CRLF) will yield [b'*1', b'$4', b'PING', b'']
    - parts[0] = *N (array count)
    - parts[1] = $N (command length)
    - parts[2] = command name

    For ECHO and other commands with argument:
    data.split(CRLF) will yield [b'*2', b'$4', b'ECHO', b'$N', b'argument', ...]
    - parts[0] = *N (array count)
    - parts[1] = $N (command length)
    - parts[2] = command name
    - parts[3] = $N (argument length)
    - parts[4] = argument
    - ... and so on for additional arguments
    """
    parts = data.split(CRLF)
    if len(parts) < 3:
        return to_resp_error(b"ERR invalid command")
    command = parts[2]
    args = parts[4::2]

    print(
        "Received command from client:",
        client_address,
        "Command:",
        command,
        "Arguments:",
        args,
    )
    print("Current connection state:", connection)

    response = await transaction.handle(
        command, args, connection, data_store, _dispatch
    )
    if response is not None:
        return response

    if command.upper() == b"PSYNC":
        return psync.handle(args, data_store, connection)

    response = await _dispatch(command, args, data_store)

    if (
        server_config["role"] == "master"
        and command.upper() in WRITE_COMMANDS
        and not connection.get("is_replica", False)
    ):
        await replication.propagate(command, args)

    return response


async def _dispatch(command: bytes, args: list[bytes], data_store: DataStore) -> bytes:
    handler = COMMAND_HANDLERS.get(command)
    if handler:
        result = handler(args, data_store)
        if asyncio.iscoroutine(result):
            return await result
        return result
    return to_resp_error(b"ERR unknown command")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=6379)
    parser.add_argument("--replicaof", type=str, default=None)
    args = parser.parse_args()
    asyncio.run(main(args.port, args.replicaof))
