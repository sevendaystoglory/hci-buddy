import subprocess
import sys

def kill_process_on_port(port):
    try:
        command = f"lsof -t -i:{port}"
        pids = subprocess.check_output(command, shell=True).decode().strip().split('\n')
        
        if pids:
            for pid in pids:
                if pid: 
                    print(f"Killing process {pid} on port {port}")
                    subprocess.run(["kill", pid], check=True)
                    print(f"Process {pid} on port {port} has been killed.")
        else:
            print(f"No process found running on port {port}.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to kill process on port {port}. Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 kill_process.py <port>")
        sys.exit(1)
    
    port = sys.argv[1]
    kill_process_on_port(port)
