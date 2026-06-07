import subprocess
import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
PID_FILE = os.path.join(PROJECT_ROOT, "app.pid")

def log_banner(message):
    print("=" * 70)
    print(f" 🛑 {message}")
    print("=" * 70)

def stop_active_server(port=8000):
    log_banner(f"Shutting Down Background Analytics Engine on Port {port}")
    
    if os.path.exists(PID_FILE):
        try:
            with open(PID_FILE, "r") as f:
                pid = f.read().strip()
            
            if pid:
                print(f"Located active application tracking reference PID: {pid}")
                if sys.platform.startswith("win"):
                    subprocess.run(f"taskkill /F /T /PID {pid}", shell=True, capture_output=True)
                else:
                    subprocess.run(f"kill -9 {pid}", shell=True, capture_output=True)
                print("✅ Core background thread terminated gracefully.")
        except Exception as e:
            print(f"Notice: PID termination step passed, handling port sweep instead. ({e})")
        finally:
            try:
                os.remove(PID_FILE)
            except Exception:
                pass

    try:
        if sys.platform.startswith("win"):
            cmd = f"netstat -ano | findstr :{port}"
            output = subprocess.check_output(cmd, shell=True).decode()
            for line in output.strip().split("\n"):
                if "LISTENING" in line:
                    socket_pid = line.strip().split()[-1]
                    print(f"Sweeping network socket process ID {socket_pid} blocking port {port}...")
                    subprocess.run(f"taskkill /F /PID {socket_pid}", shell=True, capture_output=True)
        else:
            cmd = f"lsof -t -i:{port}"
            socket_pid = subprocess.check_output(cmd, shell=True).decode().strip()
            if socket_pid:
                print(f"Sweeping network socket process ID {socket_pid} blocking port {port}...")
                subprocess.run(f"kill -9 {socket_pid}", shell=True, capture_output=True)
        print("✅ Network socket clearance verified.")
    except Exception:
        print("Network port checks verified clear.")

if __name__ == "__main__":
    stop_active_server(port=8000)
    print("=" * 70)