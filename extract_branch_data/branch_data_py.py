#!/usr/bin/env python3
import subprocess
import sys
import json
from lib.parse_branches import parse_branches
from lib.history import history

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: branch_data_py.py <output> <binary> [arguments]")
        sys.exit(1)

    output = sys.argv[1]
    binary = sys.argv[2]
    arguments = " ".join(sys.argv[3:])

    asm = subprocess.check_output(["otool", "-tv", binary], text=True)
    branches = parse_branches(asm.splitlines())

    cmd = (
        'lldb -b -Q -o "script import lib.commands; '
        + f"lib.commands.run_analysis('{binary}', '{arguments}', '{output}')\""
    )

    branch_trace = subprocess.check_output(cmd, shell=True, text=True)
    branch_trace = json.loads(branch_trace)

    branch_history = history(branch_trace, branches)
    branch_data = {"binary": binary, "arguments": arguments, "history": branch_history}

    with open(output, "w") as f:
        json.dump(branch_data, f, indent=2)
