import os
import signal
import time
from socket import *


def run_watchdog() -> None:
    """
    Main function to run the server.

    This function sets up a TCP socket, listens for incoming connections,
    receives an IP address from the client, waits for 10 seconds, and then
    shuts down the client connection. If the server cannot be reached, it
    terminates the parent process.

    """
    try:
        with socket(AF_INET, SOCK_STREAM, IPPROTO_TCP) as sock:
            sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
            sock.bind(("127.0.0.1", 3000))
            sock.listen() 
            client, addr = sock.accept()
            ip = client.recv(8192)
            for i in range(10):  # Wait for 10 seconds
                time.sleep(1)
            client.shutdown(SHUT_RDWR)
        print(f"Server {ip.decode()} cannot be reached")
        os.kill(os.getppid(), signal.SIGTERM)  # Terminate the parent process
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    run_watchdog()


