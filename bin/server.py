import socket
import os
import json
import threading
import signal
import sys
from transcriber.audio_transcriber import AudioTranscriber
from utils.config_loader import ConfigLoader

# Use absolute path for socket
config = ConfigLoader.load_config()
SOCKET_PATH = config["server"]["socket_path"]
PROJECT_ROOT = os.environ.get('SKALD_ROOT')

def cleanup():
    """Clean up resources before exit"""
    print("\nShutting down server...")
    if os.path.exists(SOCKET_PATH):
        try:
            os.remove(SOCKET_PATH)
        except OSError as e:
            print(f"Error removing socket file: {e}")
    print("Cleanup complete")
    sys.exit(0)

def signal_handler(signum, frame):
    """Handle interrupt signals"""
    cleanup()

def display_startup_message():
    config = ConfigLoader.load_config("config.json")
    version = config.get("version", "1.0")
    print(f"""
╔═══════════════════════════════════╗
║ 👄   Skald (STT Transcriber)   🎙️  ║
║      Created by @shoewind1997     ║
║ 👂     Version {version:<6}          📝 ║
╚═══════════════════════════════════╝
    """)

def run_server():
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    if os.path.exists(SOCKET_PATH):
        os.remove(SOCKET_PATH)
        
    # Initialize transcriber once at startup
    print("Initializing transcriber...")
    transcriber = AudioTranscriber()
    recording_thread = None
    
    # Get timeout from config
    config = ConfigLoader.load_config("config.json")
    socket_timeout = config["server"]["socket_timeout"]
    
    display_startup_message()
    print("Server started. Waiting for commands...")
    
    try:
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(SOCKET_PATH)
        sock.listen(1)
        sock.settimeout(socket_timeout)  # Use configured timeout
        
        while True:
            try:
                conn, addr = sock.accept()
                conn.settimeout(socket_timeout)  # Use same timeout for connection
                with conn:
                    data = conn.recv(1024).decode()
                    if not data:
                        continue
                        
                    command = json.loads(data)
                    
                    if command["action"] == "start":
                        if not recording_thread or not recording_thread.is_alive():
                            # Just reset state, don't reinitialize
                            transcriber.reset_state()
                            recording_thread = threading.Thread(target=transcriber.start_recording)
                            recording_thread.start()
                            conn.send(json.dumps({"status": "Recording started"}).encode())
                        else:
                            conn.send(json.dumps({"status": "Already recording"}).encode())
                            
                    elif command["action"] == "stop":
                        if recording_thread and recording_thread.is_alive():
                            transcriber.recording.clear()
                            conn.send(json.dumps({"status": "Recording stopped"}).encode())
                        else:
                            conn.send(json.dumps({"status": "Not recording"}).encode())
            except socket.timeout:
                continue
                
    except Exception as e:
        print(f"Error: {e}")
        cleanup()

if __name__ == "__main__":
    try:
        run_server()
    except Exception as e:
        print(f"Error: {e}")
        cleanup() 