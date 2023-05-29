import signal
import sys
from socket import *
import os
import time
import struct


def checksum(pkt) -> int:
    """
    Calculate the checksum of the given data.

    """
    res = 0

    if len(pkt) % 2 != 0:
        pkt += b'\x00'
    for i in range(0, len(pkt), 2):
        chunk = pkt[i:i + 2]
        word = struct.unpack('!H', chunk)[0]
        res += word
    res = (res >> 16) + (res & 0xFFFF)
    res += res >> 16
    # One's complement
    res = ~res & 0xFFFF
    return res


def ping_packet() -> bytes:
    """
    Create an ICMP ping packet.

     """
    icmp_type = 8  # ICMP Echo Request
    icmp_code = 0
    icmp_checksum = 0
    icmp_identifier = 18  # TODO:
    icmp_sequence = 1
    icmp_header = struct.pack('!BBHHH', icmp_type, icmp_code, icmp_checksum, icmp_identifier, icmp_sequence)
    icmp_checksum = checksum(icmp_header)
    icmp_header = struct.pack('!BBHHH', icmp_type, icmp_code, icmp_checksum, icmp_identifier, icmp_sequence)
    icmp_packet = icmp_header

    return icmp_packet


def handle_better_ping() -> None:
    """
    Handle the betterPing logic.

    This function sends ICMP ping packets, starts a watchdog process,
    establishes a TCP connection to the watchdog, receives ICMP pong packets,
    prints the packet information, shuts down the TCP connection, and terminates
    the watchdog process.

    """
    num = 0
    with socket(AF_INET, SOCK_RAW, IPPROTO_ICMP) as sock:
        while True:
            num += 1
            ping = ping_packet()
            start = time.time()
            sock.sendto(ping, (sys.argv[1], 0))
            pid = os.fork()  # Create a child process
            if pid == 0:  # child process
                os.execvp("python3", ["python3", "watchdog.py"])  # Start watchdog process , execvp replaces the
                # current process with the watchdog process
            else:  # parent process pid == child process id
                time.sleep(1)  # Wait for watchdog to start
                with socket(AF_INET, SOCK_STREAM, IPPROTO_TCP) as watchdog:  # watchdog socket
                    watchdog.connect(("127.0.0.1", 3000))  # Connect to watchdog
                    watchdog.sendall(sys.argv[1].encode())  # Send IP address to watchdog
                    pong = sock.recvfrom(8192)  # Receive ICMP pong packet
                    end = time.time()  # Get end time
                    print(
                        f"Reply from ip: {pong[1][0]}, seq num: {num}, time: {(end - start) - 1} seconds")  # Print packet information
                    watchdog.shutdown(SHUT_RDWR)  # Shutdown watchdog
                    os.kill(pid, signal.SIGTERM)  # Terminate watchdog
                    os.wait()  # Wait for watchdog to terminate


if __name__ == "__main__":
    try:
        handle_better_ping()
    except KeyboardInterrupt:
        sys.exit(0)
