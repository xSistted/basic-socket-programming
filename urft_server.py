import socket

if __name__ == "__main__":
    host = '127.0.0.1'
    port = 8080
    
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