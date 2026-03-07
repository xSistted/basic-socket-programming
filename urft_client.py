import socket
import sys
import os

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python urft_client.py <file_path> <server_ip> <server_port>")
        sys.exit(1)
    
    host = sys.argv[2]
    port = int(sys.argv[3])
    
    path = sys.argv[1]
    filename = os.path.basename(sys.argv[1])
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect((host, port))
    
    try:
        with open(path,'rb') as fi:
            sock.send(filename.encode())
            while True:
                    data = fi.read(1024) 
                    if not data:
                        break
                    sock.send(data)
        sock.send(b'')
        print("File sent successful")
    except IOError:
        print("Invalid filename! Please try again.")
