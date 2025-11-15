# OS Project – Process Scheduling Simulator with Linux Integration

This project implements a **CPU Scheduling Simulator** in Python and integrates it with **live Linux process data** using the `ps` command. It also includes a **Subnetting Tool** to support networking and CIDR concepts.

---

## Project Components

### **1. Process Scheduling Simulator (`scheduling.py`)**

This script:

- Fetches live process data on Linux using: ps -eo pid,comm,etimes,pri,ni,pcpu --sort=-pcpu
- Falls back to a sample dataset on non-Linux systems.
- Converts processes into internal **Job objects**.
- Simulates four CPU scheduling algorithms:
- **FCFS** (First-Come, First-Served)
- **SJF** (Shortest Job First, non-preemptive)
- **Round Robin** (quantum = 3)
- **Priority Scheduling** (lower value = higher priority)

### Calculates:
- Start time  
- Completion time  
- Waiting time  
- Turnaround time  
- Average waiting & turnaround time  

### Gantt Charts:
- Desktop → opens normally  
- AWS EC2 → automatically saved as PNG (headless mode)  

---

### **2. Subnetting Tool (`subnetting.py`)**

Given a base network (CIDR notation) + required hosts per subnet, it computes:

- New subnet prefix  
- Subnet mask  
- Number of subnets  
- Usable hosts per subnet  
- Addresses for each subnet:
- Network address  
- Broadcast address  
- First & last usable host  

---

## 📁 File Structure
README.md ← Main project overview
EC2_SETUP.md ← AWS EC2 setup guide (SSH, SCP, running code)
scheduling.py ← CPU scheduling simulator
subnetting.py ← Subnet calculator


---

## ⚙️ Requirements

- Python **3.8+**
- Install dependencies:

```bash
pip install pandas matplotlib
```

## Running the Scripts
Run Scheduling Simulator
python3 scheduling.py

Run Subnetting Tool
python3 subnetting.py
