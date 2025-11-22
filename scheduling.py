import os
import subprocess
import pandas as pd
import matplotlib.pyplot as plt
from dataclasses import dataclass, field
from typing import List, Optional

# Detect if the script is running in an environment with a display (e.g., local machine)
# or in a headless environment (e.g., remote server / EC2) where GUI windows cannot be shown.
# If DISPLAY is not set, we assume headless mode and only save plots to files.
HEADLESS = not os.environ.get("DISPLAY")


# ----------------------------
# STEP 1: FETCH LINUX PROCESSES
# ----------------------------
def fetch_processes(limit=5) -> pd.DataFrame:
    """
    Fetch live Linux processes using the 'ps' command and return them as a DataFrame.

    Parameters
    ----------
    limit : int
        Maximum number of top CPU-using processes to fetch.

    Returns
    -------
    pd.DataFrame
        DataFrame containing process info: PID, COMMAND, ETIMES, PRI, NI, PCPU.

    Notes
    -----
    - This works only on Linux systems where the ps command is available.
    - If the command fails (e.g., not Linux or permission issues), sample data is returned.
    """
    try:
        # ps -eo: specify output columns
        # pid,comm,etimes,pri,ni,pcpu: process ID, command name, elapsed time,
        # priority, nice value, CPU usage
        # --sort=-pcpu: sort by CPU usage descending (most CPU first)
        cmd = ["ps", "-eo", "pid,comm,etimes,pri,ni,pcpu", "--sort=-pcpu"]
        raw = subprocess.check_output(cmd, text=True).strip().split("\n")

        data = []
        # First line is the header, so we skip it and process the next limit lines
        for line in raw[1:limit + 1]:
            # Split line into at most 6 whitespace-separated parts
            parts = line.split(None, 5)
            if len(parts) < 6:
                # If the line doesn't have all fields, skip it
                continue
            pid, comm, etimes, pri, ni, pcpu = parts

            # Convert the extracted strings to appropriate data types and store in dict
            data.append({
                "PID": int(pid),
                "COMMAND": comm,
                "ETIMES": int(etimes),   # elapsed time in seconds
                "PRI": int(pri),         # priority value
                "NI": int(ni),           # nice value
                "PCPU": float(pcpu)      # CPU usage in percentage
            })

        # Create a DataFrame from the list of process dictionaries
        return pd.DataFrame(data)

    except Exception:
        # If fetching live processes fails (e.g., not on Linux, ps missing),
        # use a small set of hard-coded sample processes instead so that
        # the scheduling simulation can still run.
        print("Could not fetch live processes, using sample data instead.")
        sample = {
            "PID": [1, 2, 3, 4, 5],
            "COMMAND": ["procA", "procB", "procC", "procD", "procE"],
            "ETIMES": [5, 3, 8, 6, 2],    # used as a proxy for burst time
            "PRI": [20, 18, 22, 19, 21],  # arbitrary priority values
            "NI": [0, 0, 0, 0, 0],
            "PCPU": [1.2, 0.9, 2.3, 0.5, 1.0],
        }
        return pd.DataFrame(sample)


# ----------------------------
# STEP 2: JOB DATA STRUCTURE
# ----------------------------
@dataclass
class Job:
    """
    Represents a single process/job for CPU scheduling simulation.

    Attributes
    ----------
    pid : int
        Process ID from the OS.
    name : str
        Process/command name.
    arrival : int
        Time at which the job arrives in the ready queue (default 0 for all).
    burst : int
        CPU burst time (how long it needs the CPU).
    priority : int
        Priority of the job (smaller value = higher priority in this simulation).
    start : Optional[int]
        Time when the job first starts execution.
    completion : Optional[int]
        Time when the job finishes execution.
    remaining : int
        Remaining CPU burst time (used by preemptive algorithms like Round Robin).
    """
    pid: int
    name: str
    arrival: int = 0
    burst: int = 1
    priority: int = 0
    start: Optional[int] = None
    completion: Optional[int] = None
    remaining: int = field(init=False)

    def __post_init__(self):
        # Initialize remaining burst time equal to the total burst time
        # This is especially useful for algorithms that split execution into chunks.
        self.remaining = self.burst


def df_to_jobs(df: pd.DataFrame) -> List[Job]:
    """
    Convert a DataFrame of process info into a list of Job objects.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing at least PID, COMMAND, ETIMES, and PRI columns.

    Returns
    -------
    List[Job]
        List of Job instances ready to be used by scheduling algorithms.
    """
    jobs = []
    for _, r in df.iterrows():
        # Use ETIMES (elapsed time) as a stand-in for burst time.
        # Clamp it between 1 and 20 to keep the simulation manageable.
        burst = max(1, min(20, int(r.ETIMES)))

        # Create a Job object from each row of the DataFrame.
        # Arrival time is left at default 0 for all jobs.
        jobs.append(Job(
            pid=int(r.PID),
            name=r.COMMAND,
            burst=burst,
            priority=int(r.PRI)
        ))
    return jobs


# ----------------------------
# STEP 3: SCHEDULING ALGORITHMS
# ----------------------------
def clone_jobs(jobs: List[Job]) -> List[Job]:
    """
    Create a fresh copy of each Job object.

    This ensures that when we run multiple scheduling algorithms (FCFS, SJF, etc.),
    they don't interfere with each other by modifying the same Job instances.
    """
    return [Job(j.pid, j.name, j.arrival, j.burst, j.priority) for j in jobs]


def fcfs(jobs: List[Job]):
    """
    First-Come, First-Served (non-preemptive) scheduling.

    Behaviour
    ---------
    - Jobs are executed in the order of their arrival time.
    - Once a job starts, it runs to completion before the next job starts.

    Parameters
    ----------
    jobs : List[Job]
        Original list of jobs.

    Returns
    -------
    (List[Job], List[tuple])
        - Updated list of jobs with start and completion times set.
        - Gantt chart list of tuples (pid, start_time, end_time).
    """
    t = 0                      # Current simulated time
    gantt = []                 # Gantt chart entries
    js = clone_jobs(jobs)      # Work on a copy of jobs
    js.sort(key=lambda x: x.arrival)  # Order by arrival time

    for j in js:
        # If no job has arrived yet, move time forward to the job's arrival
        if t < j.arrival:
            t = j.arrival
        # Record when the job starts
        j.start = t
        # Job runs for its entire burst time
        t += j.burst
        # Record when the job completes
        j.completion = t
        # Store this interval for Gantt visualization
        gantt.append((j.pid, j.start, j.completion))
    return js, gantt


def sjf(jobs: List[Job]):
    """
    Shortest Job First (non-preemptive) scheduling.

    Behaviour
    ---------
    - At any time, among all jobs that have arrived and are not completed,
      the job with the smallest burst time is selected.
    - Once selected, a job runs to completion.

    Parameters
    ----------
    jobs : List[Job]

    Returns
    -------
    (List[Job], List[tuple])
        - List of completed jobs in the order they finished.
        - Gantt chart as (pid, start_time, end_time) tuples.
    """
    t = 0
    done = []        # List of jobs that have completed
    gantt = []
    js = clone_jobs(jobs)

    # Continue until all jobs are completed
    while len(done) < len(js):
        # Filter jobs that have arrived (arrival <= current time) and not done yet
        ready = [j for j in js if j not in done and j.arrival <= t]

        if not ready:
            # If no job is ready at current time, simulate idle CPU by increasing time
            t += 1
            continue

        # Among the ready jobs, choose the one with the smallest burst time
        cur = min(ready, key=lambda x: x.burst)

        # This job starts at the current time
        cur.start = t
        # It runs to completion
        t += cur.burst
        cur.completion = t

        # Mark as done and record in the Gantt chart
        done.append(cur)
        gantt.append((cur.pid, cur.start, cur.completion))
    return done, gantt


def priority_scheduling(jobs: List[Job]):
    """
    Priority scheduling (non-preemptive).

    Behaviour
    ---------
    - At any time, among the jobs that have arrived and are not completed,
      select the job with the highest priority.
    - In this implementation, a lower priority value means higher priority.
    - Once selected, a job runs until completion.

    Parameters
    ----------
    jobs : List[Job]

    Returns
    -------
    (List[Job], List[tuple])
        - List of completed jobs.
        - Gantt chart as (pid, start_time, end_time) tuples.
    """
    t = 0
    done = []
    gantt = []
    js = clone_jobs(jobs)

    while len(done) < len(js):
        # Find all jobs that have arrived and are not yet completed
        ready = [j for j in js if j not in done and j.arrival <= t]

        if not ready:
            # If no job is ready, CPU is idle; advance time
            t += 1
            continue

        # Choose job with the smallest priority value (i.e., highest priority)
        cur = min(ready, key=lambda x: x.priority)
        cur.start = t
        t += cur.burst
        cur.completion = t

        done.append(cur)
        gantt.append((cur.pid, cur.start, cur.completion))
    return done, gantt


def round_robin(jobs: List[Job], q=3):
    """
    Round Robin (preemptive) scheduling.

    Behaviour
    ---------
    - All jobs share the CPU in a cyclic order.
    - Each job gets a fixed time quantum q.
    - If a job doesn't finish within its quantum, it is preempted and put
      back into the queue, and the next job gets the CPU.

    Parameters
    ----------
    jobs : List[Job]
        List of jobs to schedule.
    q : int
        Time quantum for each job slice.

    Returns
    -------
    (List[Job], List[tuple])
        - List of jobs with updated start/completion times.
        - Gantt chart as (pid, start_time, end_time) slices (can contain multiple
          entries per job).
    """
    t = 0
    gantt = []
    js = clone_jobs(jobs)

    # For simplicity, assume all jobs are available at time 0
    queue = js.copy()

    # Continue looping until all jobs have remaining == 0
    while any(j.remaining > 0 for j in queue):
        for j in queue:
            if j.remaining > 0:
                # Record the first time the job starts executing
                if j.start is None and j.remaining == j.burst:
                    j.start = t

                # Determine how long this job will run in this round
                run = min(q, j.remaining)
                start_time = t
                t += run
                j.remaining -= run

                # Record this execution slice for the Gantt chart
                gantt.append((j.pid, start_time, t))

                # If job has finished in this slice, set its completion time
                if j.remaining == 0:
                    j.completion = t
    return js, gantt


# ----------------------------
# STEP 4: METRICS & GANTT
# ----------------------------
def compute_metrics(jobs: List[Job]):
    """
    Compute per-job and overall scheduling performance metrics.

    For each job, calculates:
    - Waiting time  = completion - arrival - burst
    - Turnaround    = completion - arrival

    Parameters
    ----------
    jobs : List[Job]
        Jobs with start and completion times already filled in by
        a scheduling algorithm.

    Returns
    -------
    (pd.DataFrame, float, float)
        - DataFrame with per-job metrics.
        - Average waiting time over all jobs.
        - Average turnaround time over all jobs.
    """
    total_wait = 0
    total_turn = 0
    metrics = []

    for j in jobs:
        # Waiting time is time spent in the system minus actual CPU time
        wait = j.completion - j.arrival - j.burst
        total_wait += wait

        # Turnaround time is total time in system from arrival to completion
        turn = j.completion - j.arrival
        total_turn += turn

        # Collect metrics for this job into a dict
        metrics.append({
            "PID": j.pid,
            "Name": j.name,
            "Burst": j.burst,
            "Start": j.start,
            "Completion": j.completion,
            "Waiting": wait,
            "Turnaround": turn,
            "Priority": j.priority
        })

    df = pd.DataFrame(metrics)
    avg_wait = total_wait / len(jobs)
    avg_turn = total_turn / len(jobs)

    return df, avg_wait, avg_turn


def plot_gantt(gantt, title):
    """
    Generate a simple horizontal Gantt chart for the given schedule.

    Parameters
    ----------
    gantt : List[tuple]
        List of (pid, start_time, end_time) entries.
    title : str
        Title for the chart, also used as a filename if saved.

    Behaviour
    ---------
    - In GUI environments: displays the plot interactively.
    - In headless environments: saves the chart as a PNG file.
    """
    plt.figure(figsize=(8, 3))

    # Each tuple corresponds to one bar segment on the Gantt chart
    for i, (pid, start, end) in enumerate(gantt):
        # Draw a horizontal bar representing the job's execution interval
        plt.barh(i, end - start, left=start)
        # Label the bar with the process ID (P<pid>) centered inside it
        plt.text((start + end) / 2, i, f"P{pid}",
                 va='center', ha='center', color='white')

    plt.xlabel("Time")
    plt.ylabel("Process")
    plt.title(title)
    plt.tight_layout()

    # Save on EC2/headless systems, show interactively otherwise
    if HEADLESS:
        # Create a filesystem-friendly filename based on the title
        filename = title.replace(" ", "").replace("-", "") + ".png"
        plt.savefig(filename)
        print(f"Saved Gantt chart to: {filename}")
    else:
        plt.show()

    plt.close()


# ----------------------------
# STEP 5: MAIN
# ----------------------------
def main():
    """
    Main driver function for the scheduling simulation.

    Steps
    -----
    1. Fetch processes (live, if possible; otherwise use sample data).
    2. Convert them into Job objects.
    3. Run multiple scheduling algorithms (FCFS, SJF, Round Robin, Priority).
    4. For each algorithm:
       - Compute and print the metrics.
       - Generate a Gantt chart.
    5. Print a summary comparison table of average waiting and turnaround times.
    """
    df = fetch_processes(limit=5)
    print("\nLive Linux processes:")
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


# Run the main function only when executed directly
if __name__ == "__main__":
    main()
