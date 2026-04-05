import socket
import select
import argparse
import threading
import hashlib

HOST = '0.0.0.0'
CLIENT_PORT = 80
cache = {}
cache_lock = threading.Lock()

def get_cache_key(data):
    """Extract method + path from the request as a cache key."""
    try:
        first_line = data.decode().split("\r\n")[0]  # e.g. "GET /path HTTP/1.1"
        method, path, _ = first_line.split(" ", 2)
        if method != "GET":
            return None  # only cache GET requests
        return path
    except:
        return None

def forward_request(data, website):
    global PORT
    modified = data.replace(
        f"Host: localhost:{PORT}".encode(),
        f"Host: {website}".encode()
    )
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((socket.gethostbyname(website), CLIENT_PORT))
        client_socket.sendall(modified)
        response = b""
        while True:
            ready, _, _ = select.select([client_socket], [], [], 2.0)
            if not ready:
                break
            chunk = client_socket.recv(4096)
            if not chunk:
                break
            response += chunk
        return response
    finally:
        client_socket.close()

def main():
    global PORT
    parser = argparse.ArgumentParser(description='A simple caching proxy.')
    parser.add_argument('--port', type=int, default=3000, help='Port to listen on')
    parser.add_argument('--origin', type=str, default='vanilla.co.za', help='Website to proxy to')
    parser.add_argument('--clear-cache', action='store_true', help='Clear the cache on startup')

    args = parser.parse_args()
    PORT = args.port
    WEBSITE = args.origin
    if args.clear_cache:
        with cache_lock:
            cache.clear()
        print("Cache cleared.")
        return

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    print(f"Proxy listening on {HOST}:{PORT} → {WEBSITE}:{CLIENT_PORT}")
    try:
        while True:
            conn, addr = server_socket.accept()
            print(f"Connection from {addr}")
            try:
                while True:
                    data = conn.recv(65536)
                    if not data:
                        break
                    key = get_cache_key(data)
                    if key:
                        with cache_lock:
                            if key in cache:
                                print(f"X-Cache: HIT")
                                conn.sendall(cache[key])
                                continue
                    response = forward_request(data, WEBSITE)
                    if key and response:
                        with cache_lock:
                            print(f"X-Cache: MISS")
                            cache[key] = response
                    conn.sendall(response)
            finally:
                conn.close()
    finally:
        server_socket.close()

if __name__ == "__main__":
    main()