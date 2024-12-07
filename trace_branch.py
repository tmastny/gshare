#!/usr/bin/env python3
import subprocess
from parse_asm import parse_asm

def run_lldb_commands(commands):
    cmd = ['lldb', '-b'] + sum([['-o', cmd] for cmd in commands], [])
    output = subprocess.check_output(cmd, text=True)
    return output

def analyze_branches(binary_path, branch_points):

    # Set up target and breakpoints
    commands = [
        f"target create {binary_path}",
        "breakpoint set --name main",
        "run"
    ]

    # Set breakpoints
    for branch in branch_points:
        commands.append(f"breakpoint set -a {branch['address']}")

    # Add breakpoint commands and run
    commands.extend([
        "breakpoint list",  # Show our breakpoints
        "breakpoint command add -o 'command source bp_commands.txt'",
        "continue"
    ])

    output = run_lldb_commands(commands)
    print("LLDB Output:")
    print(output)

def main(branches):
    binary_path = '/usr/local/bin/tree'
    analyze_branches(binary_path, branches)

if __name__ == "__main__":
    # branches = parse_asm()
    branches = [{'address': '0x100007f09', 'instruction': 'je', 'target': '0x100008281'}]
    main(branches)  # Start with 3 branches for testing
