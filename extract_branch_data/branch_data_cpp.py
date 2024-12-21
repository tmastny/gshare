#!/usr/bin/env python3
import subprocess
import sys
import json
from lib.parse_branches import parse_branches
from lib.history import history

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: branch_data_cpp.py <output> <binary> [arguments]")
        sys.exit(1)

    output = sys.argv[1]
    binary = sys.argv[2]
    arguments = sys.argv[3:]

    # Get branch addresses
    asm = subprocess.check_output(["otool", "-tv", binary], text=True)
    branches = parse_branches(asm.splitlines())

    # Create process for the C++ program
    cpp_process = subprocess.Popen(
        ["./lib/commands.out", binary, *arguments],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        text=True,
    )

    # Send addresses to C++ program
    for address in branches:
        cpp_process.stdin.write(f"{address}\n")
    cpp_process.stdin.close()  # Signal end of input

    # Read output from C++ program
    branch_trace = []
    for line in cpp_process.stdout:
        # Assuming output format is "0xADDRESS,FLAGS"
        pc, rflags = line.strip().split(",")
        branch_trace.append({pc: int(rflags)})

    # Wait for C++ program to finish
    cpp_process.wait()

    branch_history = history(branch_trace, branches)

    branch_data = {
        "binary": binary,
        "arguments": arguments,
        "branch_history": branch_history,
    }

    with open(output, "w") as f:
        json.dump(branch_data, f, indent=2)
