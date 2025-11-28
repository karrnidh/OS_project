# OS Project – Process Scheduling Simulator & Subnetting Tool

This repository contains two core modules designed for Operating Systems and Networking coursework.  
It balances academic clarity, developer‑friendly documentation, and professional GitHub presentation.

---

##  Project Overview

- **CPU Scheduling Simulator** – runs classical scheduling algorithms on real Linux process data  
- **Subnetting Calculator** – computes subnet masks, usable hosts, and address ranges automatically  
- **Cross‑platform behavior** – works on local machines and headless EC2 environments  
- **Clear, structured outputs** – includes tables, Gantt charts, and subnet summaries  

---

#  1. CPU Scheduling Simulator (`scheduling.py`)

The scheduling module fetches processes from the live Linux system using the `ps` command and simulates how operating systems schedule tasks.

###  How the Data is Obtained
- The script calls:
  ```
  ps -eo pid,comm,etimes,pri,ni,pcpu --sort=-pcpu
  ```
- On non‑Linux or restricted environments, it falls back to a built‑in sample dataset.

### What the Script Does
- Converts processes into `Job` objects (containing PID, burst time, priority, etc.)
- Simulates **four scheduling algorithms**:
  - **FCFS** – First‑Come, First‑Served
  - **SJF** – Shortest Job First (non‑preemptive)
  - **Round Robin** – fixed quantum = 3
  - **Priority Scheduling** – lower number = higher priority

###  Metrics Calculated
For each job, the simulator computes:
- Start Time  
- Completion Time  
- Burst Duration  
- Waiting Time  
- Turnaround Time  

For each algorithm:
- **Average Waiting Time**  
- **Average Turnaround Time**

###  Gantt Chart Output
- On desktop: charts open directly  
- On EC2/headless: charts are **saved automatically** as PNG files

---

#  2. Subnetting Calculator (`subnetting.py`)

A clean and interactive tool for computing subnet divisions from a base CIDR and host requirement.

###  Inputs
- Base network (e.g. `192.168.1.0/24`)
- Required hosts per subnet

###  What the Tool Computes
- Required host bits  
- New subnet prefix (CIDR)  
- Subnet mask  
- Number of available subnets  
- Usable hosts per subnet  

###  Per‑Subnet Output
For each generated subnet:
- Network Address  
- Broadcast Address  
- First Usable Host  
- Last Usable Host  
- Total Usable Hosts  

This makes the script suitable for networking labs, exams, and real‑world subnet planning.

---

#  Repository Structure

```
README.md            → Main documentation  
scheduling.py        → CPU Scheduling Simulator  
subnetting.py        → Subnetting Calculator  
EC2_SETUP.md         → Guide for running scripts on AWS EC2  
```

---

#  Requirements

- Python **3.8+**
- Install dependencies:
  ```bash
  pip install pandas matplotlib
  ```

---

#  How to Run

### Run CPU Scheduling Simulator
```bash
python3 scheduling.py
```

### Run Subnetting Tool
```bash
python3 subnetting.py
```

---
# Clone the Repository
```bash
git clone https://github.com/karrnidh/OS_project.git
cd OS_project
```
# To pull the latest updates:
```bash
git pull origin main
```
