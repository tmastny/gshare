#!/usr/bin/env python3
import subprocess
import sys
import json
from parse_branches import parse_branches
from trace import trace
from history import history


def generate_commands_lldb(branches):
    with open("commands.lldb.tmp", "r") as f:
        template = f.read()

    bps = []
    bp_template = "breakpoint set --address {}"
    for pc in branches:
        bps.append(bp_template.format(pc))

    with open("commands.lldb", "w") as f:
        f.write(template.format("\n".join(bps)))


if __name__ == "__main__":
    if len(sys.argv) < 1:
        print("Usage: branch_data.py /path/to/binary [--test-keys]")
        sys.exit(1)

    binary = sys.argv[1]
    asm = subprocess.check_output(["otool", "-tv", binary], text=True)

    branches = parse_branches(asm.splitlines())

    # test branches in my copy of "/usr/local/bin/tree"
    if "--test-keys" in sys.argv:
        test_keys = set(["0x100007f09", "0x100006685"])
        branches = {k: v for k, v in branches.items() if k in test_keys}

    generate_commands_lldb(branches)

    log = subprocess.check_output(["lldb", "-b", "-s", "commands.lldb"], text=True)

    branch_trace = trace(log.splitlines())

    branch_history = history(branch_trace, branches)

    # > branch_data.json
    json.dump(branch_history, sys.stdout, indent=2)
