#!/usr/bin/env python3
import subprocess
import sys
import json
from lib.parse_branches import parse_branches
from lib.trace import trace
from lib.history import history


def generate_commands_lldb(binary, arguments, branches):
    with open("lib/commands.lldb.tmp", "r") as f:
        template = f.read()

    bps = []
    bp_template = "breakpoint set --address {}"
    for pc in branches:
        bps.append(bp_template.format(pc))

    with open("lib/commands.lldb", "w") as f:
        f.write(
            template.format(
                binary=binary, arguments=arguments, breakpoints="\n".join(bps)
            )
        )


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: branch_data_lldb.py <output> <binary> [arguments]")
        sys.exit(1)

    output = sys.argv[1]
    binary = sys.argv[2]
    arguments = " ".join(sys.argv[3:])

    asm = subprocess.check_output(["otool", "-tv", binary], text=True)

    branches = parse_branches(asm.splitlines())

    # test branches in my copy of "/usr/local/bin/tree"
    if "--test-keys" in sys.argv:
        test_keys = set(["0x100007f09", "0x100006685"])
        branches = {k: v for k, v in branches.items() if k in test_keys}

    generate_commands_lldb(binary, arguments, branches)

    log = subprocess.check_output(["lldb", "-b", "-s", "lib/commands.lldb"], text=True)

    branch_trace = trace(log.splitlines())

    branch_history = history(branch_trace, branches)
    branch_data = {
        "binary": binary,
        "arguments": arguments,
        "branch_history": branch_history,
    }

    with open(output, "w") as f:
        json.dump(branch_data, f, indent=2)
