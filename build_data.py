#!/usr/bin/env python3
import subprocess
import sys
from parse_branches import parse_branches
from trace import trace


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
    args = set(sys.argv)

    asm = subprocess.check_output(["otool", "-tv", "/usr/local/bin/tree"], text=True)

    branches = parse_branches(asm.splitlines())

    if "--test" in args:
        test_keys = set(["0x100007f09", "0x100006685"])
        branches = {k: v for k, v in branches.items() if k in test_keys}

    generate_commands_lldb(branches)

    log = subprocess.check_output(["lldb", "-b", "-s", "commands.lldb"], text=True)

    output = trace(log.splitlines())

    print(output)
