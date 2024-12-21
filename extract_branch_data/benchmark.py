#!/usr/bin/env python3
import subprocess
import time
import statistics
import sys


def run_command(cmd):
    start_time = time.time()
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    end_time = time.time()
    return end_time - start_time


def benchmark_script(script_name, binary, args, runs=5):
    times = []
    for i in range(runs):
        cmd = [script_name, "/dev/null", binary, *args]
        duration = run_command(cmd)
        times.append(duration)
        print(f"{script_name} run {i+1}: {duration:.3f} seconds")

    avg_time = statistics.mean(times)
    std_dev = statistics.stdev(times) if len(times) > 1 else 0

    return {
        "script": script_name,
        "times": times,
        "average": avg_time,
        "std_dev": std_dev,
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: benchmark.py <binary> [args...]")
        sys.exit(1)

    binary = sys.argv[1]
    args = sys.argv[2:]

    scripts = ["./branch_data_cpp.py", "./branch_data_py.py", "./branch_data_lldb.py"]

    results = []

    print("Starting benchmark...\n")

    for script in scripts:
        print(f"\nBenchmarking {script}:")
        result = benchmark_script(script, binary, args)
        results.append(result)
        print(f"Average: {result['average']:.3f} seconds")
        print(f"Std Dev: {result['std_dev']:.3f} seconds")

    print("\nSummary:")
    print("-" * 50)
    for result in sorted(results, key=lambda x: x["average"]):
        print(
            f"{result['script']:<20} {result['average']:.3f} ± {result['std_dev']:.3f} seconds"
        )


if __name__ == "__main__":
    main()
