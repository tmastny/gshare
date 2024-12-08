#!/usr/bin/env python3
import subprocess
from parse_branches import parse_branches
import sys

if __name__ == "__main__":
    args = set(sys.argv)

    asm = subprocess.check_output(["otool", "-tv", "/usr/local/bin/tree"], text=True)

    branches = parse_branches(asm.splitlines())

    if "--test" in args:
        test_keys = set(["0x100007f09", "0x100006685"])
        branches = {k: v for k, v in branches.items() if k in test_keys}
