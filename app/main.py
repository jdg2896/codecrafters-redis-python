from pydoc import cli
import socket  # noqa: F401


def main():
    print("Starting Redis server on localhost:6379...")
    server_socket = socket.create_server(("localhost", 6379), reuse_port=True)

    while True:
        print("Waiting for client connections...")
        connection, client_address = server_socket.accept() # wait for client
        data = connection.recv(1024)  # receive data from client

        print(f"Client connected from {client_address}")
        print(f"Received data: {data}")
        if data.startswith(b"*1\r\n$4\r\nPING\r\n"):  # check if command is PING
            print(f"Received PING command: Responding with PONG to client...")
            connection.sendall(b"+PONG\r\n")  # send response to client

            while True:
                data = connection.recv(1024)  # wait for more data from client
                if not data:
                    print(f"Client {client_address} disconnected.")
                    break  # client disconnected
                print(f"Received data: {data}")
                if data.startswith(b"*1\r\n$4\r\nPING\r\n"):  # check if command is PING
                    print(f"Received PING command: Responding with PONG to client...")
                    connection.sendall(b"+PONG\r\n")  # send response to client
                else:
                    print(f"Received unknown command: {data}")
                    connection.sendall(b"-ERR unknown command\r\n")  # send error response to client
            connection.close()  # close client connection


if __name__ == "__main__":
    main()
