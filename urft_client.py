import socket
import sys

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python urft_client.py <file_path> <server_ip> <server_port>")
        sys.exit(1)
    
    host = sys.argv[2]
    port = int(sys.argv[3])
    
    filename = sys.argv[1]
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect((host, port))
    
    try:
        with open(filename,'r') as fi:
            while True:
                    data = fi.read(1024) 
                    if not data:
                        break
                    sock.send(data.encode())
        sock.send(b'')
        print("File sent successful")
    except IOError:
        print("Invalid filename! Please try again.")