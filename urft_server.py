import socket
import sys

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python urft_server.py <server_ip> <server_port>")
        sys.exit(1)
    
    host = sys.argv[1]
    port = int(sys.argv[2])
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((host, port))
    
    print("UDP Server is waiting for data...")
        
    fileno = 0
    filename_real = sock.recvfrom(1024)[0].decode()
    while True:
        data, addr = sock.recvfrom(1024)
        if not data:
            continue
        filename = filename_real
        fileno += 1
        with open(filename, "wb") as f:
            while data:
                f.write(data)
                data, addr = sock.recvfrom(1024)
                if not data:
                    break
        print("Received file from", addr)
        print("Saved as", filename)
