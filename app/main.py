import socket  # noqa: F401


def main():
    print("Starting Redis server on localhost:6379...")
    server_socket = socket.create_server(("localhost", 6379), reuse_port=True)
    client_socket, client_address = server_socket.accept() # wait for client

    print(f"Client connected from {client_address}")
    print(f"Sending PONG response to client...")
    client_socket.sendmsg([b"+PONG\r\n"])  # send response to client
    client_socket.close()


if __name__ == "__main__":
    main()
