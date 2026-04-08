from pydoc import cli
import socket  # noqa: F401


def main():
    print("Starting Redis server on localhost:6379...")
    server_socket = socket.create_server(("localhost", 6379), reuse_port=True)

    while True:
        client_socket, client_address = server_socket.accept() # wait for client
        data = client_socket.recv(1024)  # receive data from client

        print(f"Client connected from {client_address}")
        print(f"Received data: {data}")
        if data.startswith(b"*1\r\n$4\r\nPING\r\n"):  # check if command is PING
            print(f"Received PING command: Responding with PONG to client...")
            client_socket.sendall(b"+PONG\r\n")  # send response to client
            client_socket.close()  # close client connection


if __name__ == "__main__":
    main()
