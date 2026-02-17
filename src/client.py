import socket
import os

SERVER_HOST = "0.0.0.0"   # change if remote
SERVER_PORT = 2121
USERNAME = "pramananda"
FILE_PATH = "./demo-code/main.py"


def recv_line(sock):
    data = b""
    while not data.endswith(b"\r\n"):
        chunk = sock.recv(1)
        if not chunk:
            break
        data += chunk
    return data.decode().strip()


def main():
    if not os.path.exists(FILE_PATH):
        print("File not found")
        return

    filesize = os.path.getsize(FILE_PATH)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((SERVER_HOST, SERVER_PORT))

    # Server greeting
    print(recv_line(sock))

    # Send USER
    sock.sendall(f"USER {USERNAME}\r\n".encode())
    print(recv_line(sock))

    # Send FILE command
    sock.sendall(f"FILE {os.path.basename(FILE_PATH)} {filesize}\r\n".encode())
    print(recv_line(sock))

    # Send file bytes
    with open(FILE_PATH, "rb") as f:
        while chunk := f.read(4096):
            sock.sendall(chunk)

    # Transfer complete
    print(recv_line(sock))

    # Quit
    sock.sendall(b"QUIT\r\n")
    print(recv_line(sock))

    sock.close()


if __name__ == "__main__":
    main()
