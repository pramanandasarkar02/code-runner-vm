import hashlib
from datetime import datetime
import os
import socket
import subprocess

HOST = "0.0.0.0"
PORT = 2121
FTP_ROOT = "./tmp"

os.makedirs(FTP_ROOT, exist_ok=True)


def create_hash_dir(username: str) -> str:
    unique = username + datetime.now().isoformat()
    hash_name = hashlib.md5(unique.encode()).hexdigest()
    dir_path = os.path.join(FTP_ROOT, hash_name)
    os.makedirs(dir_path, exist_ok=True)
    return dir_path

def run_code(file_path):
    baseName = os.path.basename(file_path)
    ext = baseName.split(".")[-1]

    result = None
    error = None

    if ext == "py":
        result = subprocess.run(["python", file_path], capture_output=True, text=True, check=True)
        if result.stderr:
            error = result.stderr
        result = result.stdout
    else:
        result, error = "", "Unsupported File Format"

    if result == None: result = ""
    if error == None: error = ""
    return result, error


def send(conn, msg):
    conn.sendall((msg + "\r\n").encode())


def recv_exact(conn, size):
    data = b""
    while len(data) < size:
        chunk = conn.recv(size - len(data))
        if not chunk:
            break
        data += chunk
    return data


def handle_client(conn):
    send(conn, "FTP server ready")

    username = None
    user_dir = None

    while True:
        cmd = conn.recv(1024).decode().strip()
        if not cmd:
            break

        print("CMD:", cmd)

        parts = cmd.split()

        if parts[0] == "USER":
            if len(parts) != 2:
                send(conn, "Invalid USER command")
                continue

            username = parts[1]
            user_dir = create_hash_dir(username)
            send(conn, "User logged in")

        elif parts[0] == "FILE":
            if not user_dir:
                send(conn, "Login with USER first")
                continue

            if len(parts) != 3:
                send(conn, "Invalid FILE command")
                continue

            filename = parts[1]
            filesize = int(parts[2])

            send(conn, "Ready to receive file")

            file_data = recv_exact(conn, filesize)

            file_path = os.path.join(user_dir, filename)
            with open(file_path, "wb") as f:
                f.write(file_data)

            send(conn, "File transfer complete")
            print(f"Saved file to: {file_path}")

            res, err = run_code(file_path=file_path)
            send(conn, f"Result: {res}")
            send(conn, f"Error: {err}")
            print(f"Send \tresult: {res} \n\terror: {err} \n\tuser: {username}")


        elif parts[0] == "QUIT":
            send(conn, "Connection Closed")
            break

        else:
            send(conn, "Command not implemented")

    conn.close()


def ftp_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(5)

    print(f"FTP server running at {HOST}:{PORT}")

    while True:
        conn, addr = server.accept()
        print("Connected:", addr)
        handle_client(conn)


if __name__ == "__main__":
    ftp_server()
