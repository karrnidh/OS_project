# OS_project

# 🧮 Process Scheduling and IP Address Subnetting Simulator with Linux Integration

A Python-based **CPU Scheduling Simulator** that fetches **live Linux processes** and runs them through multiple scheduling algorithms.  
It calculates **waiting time**, **turnaround time**, and shows **Gantt charts** for each algorithm.

---

## ⚙️ File Information

📄 **File:** `scheduling.py`  
🧠 **Purpose:** Simulate how an Operating System schedules processes using:
- First Come First Serve (FCFS)
- Shortest Job First (SJF)
- Round Robin (RR)
- Priority Scheduling

---

## 🚀 Features

- Fetches real-time process data from Linux using the `ps` command  
- Converts system processes into simulated jobs  
- Implements **four scheduling algorithms**  
- Calculates average waiting and turnaround times  
- Generates **Gantt charts** for visualization  
- Provides comparison summary across all algorithms  

---

## 🧰 Requirements

Before running, make sure you have Python 3.8+ and install these libraries:

```bash
pip install pandas matplotlib
