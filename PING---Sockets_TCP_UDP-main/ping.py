import socket
import sys
import time
import io
import struct


def calculate_checksum(data):
    checksum = 0
    if len(data) % 2 != 0: # if odd number of bytes
        data += b'\x00'
    for i in range(0, len(data), 2): # iterate over bytes pairwise
        chunk = data[i:i+2] # get 2 bytes
        word = struct.unpack('!H', chunk)[0]
        checksum += word
    checksum = (checksum >> 16) + (checksum & 0xFFFF)
    checksum += checksum >> 16
    checksum = ~checksum & 0xFFFF
    return checksum


def create_ping_packet():
    icmp_type = 8 
    icmp_code = 0
    icmp_checksum = 0
    icmp_identifier = 1
    icmp_sequence = 1
    icmp_header = struct.pack('!BBHHH', icmp_type, icmp_code, icmp_checksum, icmp_identifier, icmp_sequence)
    icmp_checksum = calculate_checksum(icmp_header)
    icmp_header = struct.pack('!BBHHH', icmp_type, icmp_code, icmp_checksum, icmp_identifier, icmp_sequence)
    icmp_packet = icmp_header
    return icmp_packet


def handle_ping():
    try: 
        Packet = create_ping_packet() 
        with socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP) as sock:
            seq = 0
            while True:
                start = time.time()
                sock.sendto(Packet, (sys.argv[1], 8)) 
                pong_pkt = sock.recvfrom(io.DEFAULT_BUFFER_SIZE)
                end = time.time() # time in seconds
                time.sleep(0.5)
                print(f"Packet IP: {pong_pkt[1][0]} , seq : {seq} , time : {end-start} seconds")
                seq = seq + 1
    except KeyboardInterrupt: 
        if sock: # if socket is open close it
            sock.close()


if __name__ == "__main__":
    handle_ping()