import socket  # noqa: F401

PING = b"*1\r\n$4\r\nPING\r\n"
PONG = b"+PONG\r\n"

def main():
    print("Starting Redis server on localhost:6379...")
    server_socket = socket.create_server(("localhost", 6379), reuse_port=True)

    print("Waiting for client connections...")
    client_connection, client_address = server_socket.accept() # wait for client
    data = client_connection.recv(1024)  # receive data from client

    print(f"Client connected from {client_address}")
    print(f"Received data: {data}")
    if data.startswith(PING):
        _send_pong(client_connection)

        while True:
            data = client_connection.recv(1024)  # wait for more data from client
            if not data:
                print(f"Client {client_address} disconnected.")
                break  # client disconnected
            print(f"Received data: {data}")
            if data.startswith(PING):
                _send_pong(client_connection)
            else:
                print(f"Received unknown command: {data}")
                client_connection.sendall(b"-ERR unknown command\r\n")  # send error response to client

        client_connection.close()

def _send_pong(client_connection: socket.socket):
    print(f"Received PING command: Responding with PONG to client...")
    client_connection.sendall(PONG)


if __name__ == "__main__":
    main()
