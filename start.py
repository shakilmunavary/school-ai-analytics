import subprocess
import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

def log_banner(message):
    print("=" * 70)
    print(f" 🚀 {message}")
    print("=" * 70)

def kill_existing_server(port=8000):
    """Safely drops any lingering processes locking the analytics port cross-platform."""
    print(f"Checking for processes blocking network port {port}...")
    try:
        if sys.platform.startswith("win"):
            cmd = f"netstat -ano | findstr :{port}"
            output = subprocess.check_output(cmd, shell=True).decode()
            for line in output.strip().split("\n"):
                if "LISTENING" in line:
                    pid = line.strip().split()[-1]
                    print(f"Killing Windows process ID {pid} holding port {port}...")
                    subprocess.run(f"taskkill /F /PID {pid}", shell=True)
        else:
            cmd = f"lsof -t -i:{port}"
            pid = subprocess.check_output(cmd, shell=True).decode().strip()
            if pid:
                print(f"Killing Unix process ID {pid} holding port {port}...")
                subprocess.run(f"kill -9 {pid}", shell=True)
    except Exception:
        print(f"Port {port} is clear and ready for network data streams.")

def run_script(script_name):
    """Executes background modules safely inside the active Python interpreter environment."""
    script_path = os.path.join(PROJECT_ROOT, script_name)
    print(f"Executing subsystem step: {script_name}...")
    result = subprocess.run([sys.executable, script_path], capture_output=False)
    if result.returncode != 0:
        print(f"❌ Error detected while executing {script_name}. Aborting launch sequence.")
        sys.exit(1)

def launch_workspace():
    log_banner("School AI Workspace Ecosystem - Foreground Interactive Logging Deployment")
    
    # 1. Clear out any old background server processes hanging onto the port
    kill_existing_server(port=8000)
    
    # 2. Run data generator scripts
    run_script("setup_db.py")
    run_script("index.py")
    
    log_banner("Workspace Engines Initialized - Launching Live Server Console Stream")
    print("Access Link active at: http://localhost:8000")
    print("Keep this terminal window open to monitor live incoming traffic logs.\n")
    
    try:
        # 3. Launch uvicorn directly in the foreground with live reloads
        subprocess.run([
            sys.executable, "-m", "uvicorn", "server:app", 
            "--host", "0.0.0.0", 
            "--port", "8000",
            "--reload"
        ], cwd=PROJECT_ROOT)
    except KeyboardInterrupt:
        log_banner("Ecosystem web server shut down cleanly via keyboard interrupt signal.")

if __name__ == "__main__":
    launch_workspace()