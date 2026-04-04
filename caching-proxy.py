import socket
import select

HOST = 'localhost'
PORT = 3000
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def handle_server():
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(1)
    print(f"Proxy server listening on {HOST}:{PORT}")

CLIENT_PORT = 80
def handle_client(data, conn):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # client_socket.settimeout(0.5)
    client_socket.connect((socket.gethostbyname('jewish.capetown'), CLIENT_PORT))
    client_socket.sendall(data)

    response = b""
    while True:
        ready, _, _ = select.select([client_socket], [], [], 1.0)
        if not ready:
            break  # no data arrived within 1 second, we're done
        chunk = client_socket.recv(4096)
        if not chunk:
            break
        response += chunk

    conn.sendall(response)
    client_socket.close()
    # print(f"Received response from server: {response}")

def main():
    global server_socket
  
    
    handle_server()
    conn, addr = server_socket.accept()

    print(f"Connected by {addr}")

    while True:
        data = conn.recv(1024)
        if not data:
            break
        print(f"Received data: {data.decode().replace('localhost:3000', 'jewish.capetown')}")
        handle_client(data.decode().replace('localhost:3000', 'jewish.capetown').encode(), conn)

    conn.close()
    server_socket.close()

if __name__ == "__main__":
    main()