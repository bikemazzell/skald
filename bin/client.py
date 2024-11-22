import socket
import json
import sys
from utils.config_loader import ConfigLoader

config = ConfigLoader.load_config()
SOCKET_PATH = config["server"]["socket_path"]

def send_command(action):
    config = ConfigLoader.load_config()
    try:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
            sock.settimeout(config["server"].get("socket_timeout", 1.0))
            sock.connect(SOCKET_PATH)
            sock.send(json.dumps({"action": action}).encode())
            response = json.loads(sock.recv(1024).decode())
            if "status" not in response:
                print("Error: Invalid response from server")
                return
            print(response["status"])
    except socket.timeout:
        print("Error: Server not responding")
    except FileNotFoundError:
        print("Error: Server not running. Start it with './skald-server'")
    except ConnectionRefusedError:
        print("Error: Could not connect to server")

def main():
    if len(sys.argv) != 2 or sys.argv[1] not in ["start", "stop"]:
        print("Usage: ./skald-client [start|stop]")
        sys.exit(1)
    send_command(sys.argv[1])

if __name__ == "__main__":
    main() 