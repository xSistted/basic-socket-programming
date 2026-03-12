import socket
import sys
import struct
import os
import time
import select

TYPE_DATA = 0
TYPE_ACK = 1
TYPE_METADATA = 2
TYPE_FIN = 3

HEADER_FORMAT = "!BI"
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)
PAYLOAD_SIZE = 1400 
WINDOW_SIZE = 256 #256 * 1400 ~= 350KB.

INITIAL_TIMEOUT = 0.5
MIN_TIMEOUT = 0.05

def main():
    if len(sys.argv) != 4:
        print(f"Usage: {sys.argv[0]} <file_path> <server_ip> <server_port>")
        sys.exit(1)

    file_path = sys.argv[1]
    server_ip = sys.argv[2]
    try:
        server_port = int(sys.argv[3])
    except ValueError:
        print("Port must be an integer")
        sys.exit(1)

    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        sys.exit(1)

    server_addr = (server_ip, server_port)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setblocking(False)

    filename = os.path.basename(file_path)
    meta_packet = struct.pack(HEADER_FORMAT, TYPE_METADATA, 0) + filename.encode('utf-8')
    
    timeout = INITIAL_TIMEOUT
    start_time = time.time()
    
    est_rtt = INITIAL_TIMEOUT
    dev_rtt = 0.0

    while True:
        sock.sendto(meta_packet, server_addr)
        send_time = time.time()
        
        ready = select.select([sock], [], [], timeout)
        if ready[0]:
            try:
                data, _ = sock.recvfrom(2048)
                if len(data) >= HEADER_SIZE:
                    ptype, pseq = struct.unpack(HEADER_FORMAT, data[:HEADER_SIZE])
                    if ptype == TYPE_ACK and pseq == 0:
                        sample_rtt = time.time() - send_time
                        est_rtt = sample_rtt
                        dev_rtt = sample_rtt / 2
                        timeout = est_rtt + 4 * dev_rtt
                        timeout = max(timeout, MIN_TIMEOUT)
                        break
            except ConnectionResetError:
                pass 
            
        if time.time() - start_time > 10:
           print("Could not connect to server.")
           sock.close()
           sys.exit(1)
        
        timeout = min(timeout * 1.5, 1.0)

    packets = []
    try:
        with open(file_path, 'rb') as f:
            seq = 0
            while True:
                chunk = f.read(PAYLOAD_SIZE)
                if not chunk:
                    break
                pkt = struct.pack(HEADER_FORMAT, TYPE_DATA, seq) + chunk
                packets.append(pkt)
                seq += 1
    except OSError as e:
        print(f"Error reading file: {e}")
        sock.close()
        sys.exit(1)

    total_packets = len(packets)
    if total_packets == 0:
        pass 

    base = 0
    acked_bitmap = [False] * total_packets
    pkt_sent_time = [0.0] * total_packets
    
    pkt_transmissions = [0] * total_packets

    while base < total_packets:
        window_upper = min(base + WINDOW_SIZE, total_packets)
        current_time = time.time()

        for seq in range(base, window_upper):
            if acked_bitmap[seq]:
                continue
            
            if pkt_sent_time[seq] == 0 or (current_time - pkt_sent_time[seq] > timeout):
                sock.sendto(packets[seq], server_addr)
                pkt_sent_time[seq] = current_time
                pkt_transmissions[seq] += 1
        
        while True:
            ready = select.select([sock], [], [], 0.001) 
            if not ready[0]:
                break
            
            try:
                data, _ = sock.recvfrom(2048)
                if len(data) >= HEADER_SIZE:
                    ptype, pseq = struct.unpack(HEADER_FORMAT, data[:HEADER_SIZE])
                    
                    if ptype == TYPE_ACK:
                        if 0 <= pseq < total_packets:
                            if not acked_bitmap[pseq]:
                                acked_bitmap[pseq] = True
                                
                                if pkt_transmissions[pseq] == 1:
                                    sample = time.time() - pkt_sent_time[pseq]
                                    err = sample - est_rtt
                                    est_rtt = est_rtt + 0.125 * err
                                    dev_rtt = dev_rtt + 0.25 * (abs(err) - dev_rtt)
                                    timeout = est_rtt + 4 * dev_rtt
                                    timeout = max(timeout, MIN_TIMEOUT)
            except:
                pass
            
        while base < total_packets and acked_bitmap[base]:
            base += 1

    fin_pkt = struct.pack(HEADER_FORMAT, TYPE_FIN, 0)
    attempts = 0
    while attempts < 20: 
        sock.sendto(fin_pkt, server_addr)
        
        ready = select.select([sock], [], [], 0.2)
        if ready[0]:
            try:
                data, _ = sock.recvfrom(2048)
                if len(data) >= HEADER_SIZE:
                    ptype, _ = struct.unpack(HEADER_FORMAT, data[:HEADER_SIZE])
                    if ptype == TYPE_ACK:
                        break 
            except:
                pass
        attempts += 1

    sock.close()
    sys.exit(0)

if __name__ == "__main__":
    main()
