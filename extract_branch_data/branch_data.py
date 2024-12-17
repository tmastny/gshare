#!/usr/bin/env python3
import subprocess
import sys
import json
from parse_branches import parse_branches
from trace import trace
from history import history


def generate_commands_lldb(binary, arguments, branches):
    with open("commands.lldb.tmp", "r") as f:
        template = f.read()

    bps = []
    bp_template = "breakpoint set --address {}"
    for pc in branches:
        bps.append(bp_template.format(pc))

    with open("commands.lldb", "w") as f:
        f.write(
            template.format(
                binary=binary, arguments=arguments, breakpoints="\n".join(bps)
            )
        )


if __name__ == "__main__":
    if len(sys.argv) < 1:
        print("Usage: branch_data.py /path/to/binary [arguments]")
        sys.exit(1)

    binary = sys.argv[1]
    arguments = " ".join(sys.argv[2:])

    asm = subprocess.check_output(["otool", "-tv", binary], text=True)

    branches = parse_branches(asm.splitlines())

    # test branches in my copy of "/usr/local/bin/tree"
    if "--test-keys" in sys.argv:
        test_keys = set(["0x100007f09", "0x100006685"])
        branches = {k: v for k, v in branches.items() if k in test_keys}

    generate_commands_lldb(binary, arguments, branches)

    log = subprocess.check_output(["lldb", "-b", "-s", "commands.lldb"], text=True)

    branch_trace = trace(log.splitlines())

    branch_history = history(branch_trace, branches)
    branch_data = {"binary": binary, "arguments": arguments, "branch_history": branch_history}

    # > branch_data.json
    json.dump(branch_data, sys.stdout, indent=2)
