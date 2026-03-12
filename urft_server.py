import socket
import sys
import struct
import os

TYPE_DATA = 0
TYPE_ACK = 1
TYPE_METADATA = 2
TYPE_FIN = 3

# Header: Type (1 byte), SeqNum (4 bytes)
HEADER_FORMAT = "!BI"
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)

def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <server_ip> <server_port>")
        sys.exit(1)

    host = sys.argv[1]
    try:
        port = int(sys.argv[2])
    except ValueError:
        print("Port must be an integer.")
        sys.exit(1)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.bind((host, port))
    except Exception as e:
        print(f"Bind failed: {e}")
        sys.exit(1)
        
    print(f"Server running on {host}:{port}")

    OUTPUT_DIR = "received_files"
    if not os.path.exists(OUTPUT_DIR):
        try:
            os.makedirs(OUTPUT_DIR)
            print(f"Created directory: {OUTPUT_DIR}")
        except OSError as e:
            print(f"Error creating directory: {e}")
            sys.exit(1)

    print(f"Files will be saved to: {os.path.abspath(OUTPUT_DIR)}")

    expected_seq = 0
    buffer = {} # Key: seq_num, Value: payload
    file_handle = None
    client_addr = None
    transfer_started = False
    
    while True:
        try:
            data, addr = sock.recvfrom(65535)
            
            if len(data) < HEADER_SIZE:
                continue

            packet_type, seq_num = struct.unpack(HEADER_FORMAT, data[:HEADER_SIZE])
            payload = data[HEADER_SIZE:]

            if packet_type == TYPE_METADATA:
                try:
                    filename_raw = payload.decode('utf-8')
                    filename = os.path.basename(filename_raw)
                    filepath = os.path.join(OUTPUT_DIR, filename)
                    
                    if not transfer_started or (client_addr == addr):
                        client_addr = addr
                        transfer_started = True
                        expected_seq = 0
                        buffer.clear()
                        if file_handle:
                            file_handle.close()
                        file_handle = open(filepath, 'wb')
                        print(f"Receiving file: {filename}")
                    
                    ack = struct.pack(HEADER_FORMAT, TYPE_ACK, seq_num)
                    sock.sendto(ack, addr)
                    
                except Exception:
                    pass

            elif packet_type == TYPE_DATA:
                if not transfer_started or client_addr != addr:
                    continue 

                ack = struct.pack(HEADER_FORMAT, TYPE_ACK, seq_num)
                sock.sendto(ack, addr)

                if seq_num == expected_seq:
                    file_handle.write(payload)
                    expected_seq += 1
                    
                    while expected_seq in buffer:
                        file_handle.write(buffer.pop(expected_seq))
                        expected_seq += 1
                
                elif seq_num > expected_seq:
                    if len(buffer) < 5000: 
                        buffer[seq_num] = payload
                
            elif packet_type == TYPE_FIN:
                if client_addr == addr:
                    ack = struct.pack(HEADER_FORMAT, TYPE_ACK, seq_num)
                    for _ in range(5): 
                        sock.sendto(ack, addr)
                    break

        except KeyboardInterrupt:
            break
        except Exception:
            continue

    if file_handle:
        print(f"File transfer complete. Saved to: {file_handle.name}")
        file_handle.close()
    sock.close()
    sys.exit(0)

if __name__ == "__main__":
    main()
