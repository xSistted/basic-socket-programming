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
    while True:
        data, addr = sock.recvfrom(1024)
        if not data:
            continue
        filename = 'output'+str(fileno)+'.txt'
        fileno += 1
        with open(filename, "w") as f:
            while data:
                f.write(data.decode())
                data, addr = sock.recvfrom(1024)
                if not data:
                    break
        print("Received file from", addr)
        print("Saved as", filename)