import subprocess
import pandas as pd
import matplotlib.pyplot as plt
from dataclasses import dataclass, field
from typing import List, Optional

# ================================================================
# STEP 1: FETCH LIVE LINUX PROCESSES
# ================================================================
def fetch_processes(limit=5) -> pd.DataFrame:
    """
    Fetches live running processes from Linux using `ps`.
    Extracts PID, command name, elapsed time, priority, nice value, and CPU usage.
    """
    try:
        cmd = ["ps", "-eo", "pid,comm,etimes,pri,ni,pcpu", "--sort=-pcpu"]
        raw = subprocess.check_output(cmd, text=True).strip().split("\n")
    except subprocess.CalledProcessError:
        print("Error fetching processes.")
        return pd.DataFrame()

    data = []
    for line in raw[1:limit+1]:  # skip header
        parts = line.split(None, 5)
        if len(parts) < 6:
            continue
        pid, comm, etimes, pri, ni, pcpu = parts
        data.append({
            "PID": int(pid),
            "COMMAND": comm,
            "ETIMES": int(etimes),
            "PRI": int(pri),
            "NI": int(ni),
            "PCPU": float(pcpu)
        })
    return pd.DataFrame(data)

# ================================================================
# STEP 2: JOB DATA STRUCTURE
# ================================================================
@dataclass
class Job:
    pid: int
    name: str
    arrival: int = 0
    burst: int = 1
    priority: int = 0
    start: Optional[int] = None
    completion: Optional[int] = None
    remaining: int = field(init=False)

    def __post_init__(self):
        self.remaining = self.burst

def df_to_jobs(df: pd.DataFrame) -> List[Job]:
    """
    Converts process DataFrame into a list of Job objects.
    Caps ETIMES to a range 1–20 to simulate CPU bursts realistically.
    """
    jobs = []
    for _, r in df.iterrows():
        burst = max(1, min(20, int(r.ETIMES)))
        jobs.append(Job(
            pid=int(r.PID),
            name=r.COMMAND,
            burst=burst,
            priority=int(r.PRI)
        ))
    return jobs

# ================================================================
# STEP 3: SCHEDULING ALGORITHMS
# ================================================================
def fcfs(jobs: List[Job]):
    t = 0
    gantt = []
    js = [Job(**{k: getattr(j, k) for k in ['pid','name','arrival','burst','priority']}) for j in jobs]
    js.sort(key=lambda x: x.arrival)

    for j in js:
        if t < j.arrival:
            t = j.arrival
        j.start = t
        t += j.burst
        j.completion = t
        gantt.append((j.pid, j.start, j.completion))
    return js, gantt

def sjf(jobs: List[Job]):
    t = 0
    done = []
    gantt = []
    js = [Job(**{k: getattr(j, k) for k in ['pid','name','arrival','burst','priority']}) for j in jobs]

    while len(done) < len(js):
        ready = [j for j in js if j not in done and j.arrival <= t]
        if not ready:
            t += 1
            continue
        cur = min(ready, key=lambda x: x.burst)
        cur.start = t
        t += cur.burst
        cur.completion = t
        done.append(cur)
        gantt.append((cur.pid, cur.start, cur.completion))
    return done, gantt

def round_robin(jobs: List[Job], q=3):
    t = 0
    gantt = []
    js = [Job(**{k: getattr(j, k) for k in ['pid','name','arrival','burst','priority']}) for j in jobs]
    queue = js.copy()

    while any(j.remaining > 0 for j in queue):
        for j in queue:
            if j.remaining > 0:
                if j.start is None:
                    j.start = t
                run = min(q, j.remaining)
                start_time = t
                t += run
                j.remaining -= run
                gantt.append((j.pid, start_time, t))
                if j.remaining == 0:
                    j.completion = t
    return js, gantt

def priority_scheduling(jobs: List[Job]):
    t = 0
    done = []
    gantt = []
    js = [Job(**{k: getattr(j, k) for k in ['pid','name','arrival','burst','priority']}) for j in jobs]

    while len(done) < len(js):
        ready = [j for j in js if j not in done and j.arrival <= t]
        if not ready:
            t += 1
            continue
        cur = min(ready, key=lambda x: x.priority)  # lower = higher priority
        cur.start = t
        t += cur.burst
        cur.completion = t
        done.append(cur)
        gantt.append((cur.pid, cur.start, cur.completion))
    return done, gantt

# ================================================================
# STEP 4: METRICS & GANTT CHARTS
# ================================================================
def compute_metrics(jobs: List[Job]):
    total_wait = 0
    total_turn = 0
    metrics = []

    for j in jobs:
        wait = j.completion - j.arrival - j.burst
        total_wait += wait
        total_turn += j.completion - j.arrival
        metrics.append({
            "PID": j.pid,
            "Name": j.name,
            "Burst": j.burst,
            "Start": j.start,
            "Completion": j.completion,
            "Waiting": wait,
            "Turnaround": j.completion - j.arrival,
            "Priority": j.priority
        })

    df = pd.DataFrame(metrics)
    return df, total_wait / len(jobs), total_turn / len(jobs)

def plot_gantt(gantt, title):
    plt.figure(figsize=(8, 3))
    for i, (pid, start, end) in enumerate(gantt):
        plt.barh(i, end - start, left=start)
        plt.text((start + end) / 2, i, f"P{pid}", va='center', ha='center', color='white')
    plt.xlabel("Time")
    plt.ylabel("Process")
    plt.title(title)
    plt.tight_layout()
    plt.savefig(f"gantt_{title.replace(' ', '_').lower()}.png")
    plt.close()

# ================================================================
# STEP 5: MAIN EXECUTION
# ================================================================
def main():
    df = fetch_processes(limit=5)
    if df.empty:
        print("No process data found. Exiting.")
        return

    print(f"\nFetched {len(df)} Linux processes for simulation:\n")
    print(df[["PID", "COMMAND", "ETIMES", "PRI", "NI", "PCPU"]])

    jobs = df_to_jobs(df)

    algos = {
        "FCFS": fcfs,
        "SJF": sjf,
        "Round Robin": lambda j: round_robin(j, q=3),
        "Priority": priority_scheduling
    }

    summary = []
    for name, func in algos.items():
        js, gantt = func(jobs)
        dfres, avg_wt, avg_tat = compute_metrics(js)
        print(f"\n--- {name} ---")
        print(dfres)
        print(f"Avg Waiting = {avg_wt:.2f}, Avg Turnaround = {avg_tat:.2f}")
        plot_gantt(gantt, f"Gantt Chart - {name}")
        summary.append((name, avg_wt, avg_tat))

    print("\nSummary Comparison:")
    print(pd.DataFrame(summary, columns=["Algorithm", "Avg Waiting", "Avg Turnaround"]))

if __name__ == "__main__":
    main()
