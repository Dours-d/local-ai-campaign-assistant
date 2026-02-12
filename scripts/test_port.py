
import socket

def test_port(ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)
    try:
        s.connect((ip, port))
        print(f"Port {port} is OPEN on {ip}")
        s.close()
    except Exception as e:
        print(f"Port {port} is CLOSED on {ip}: {e}")

test_port("127.0.0.1", 9222)
test_port("0.0.0.0", 9222)
test_port("localhost", 9222)
