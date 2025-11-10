# ===============================================
#  Linux Integration for Scheduling Comparison
# ===============================================

import subprocess

def show_linux_process_snapshot():
    print("\n--- Linux Process Snapshot ---")

    # Top 10 running processes with PID, name, priority, and state
    cmd = "ps -eo pid,comm,pri,stat --sort=-pri | head -10"
    try:
        output = subprocess.getoutput(cmd)
        print(output)
    except Exception as e:
        print("Error fetching Linux process data:", e)

    print("\n--- CPU Scheduling Overview (from top) ---")
    cmd2 = "top -b -n 1 | head -15"
    try:
        output2 = subprocess.getoutput(cmd2)
        print(output2)
    except Exception as e:
        print("Error fetching top output:", e)
