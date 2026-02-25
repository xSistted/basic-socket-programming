import socket

if __name__ == "__main__":
    host = '127.0.0.1'
    port = 8080
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect((host, port))
    
    while True:
        filename = input('Input filename you want to send: ')
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