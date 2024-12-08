#!/usr/bin/env python3
import subprocess
from parse_asm import parse_asm
from collections import defaultdict

def parse_lldb_output(output):
    """Parse LLDB output to extract branch outcomes"""
    branch_outcomes = defaultdict(list)

    lines = output.split('\n')
    i = 0
    while i < len(lines):
        if "p/x $rip" in lines[i]:
            # Next line contains branch address
            branch_addr = lines[i+1].split('0x')[1].strip()

            # Skip to flags
            while i < len(lines) and "register read rflags" not in lines[i]:
                i += 1
            if i < len(lines):
                # Next line contains flags
                flags = int(lines[i+1].split('0x')[1].strip(), 16)

                # Skip to next instruction (after si)
                while i < len(lines) and "p/x $rip" not in lines[i]:
                    i += 1
                if i < len(lines):
                    # Next line contains next instruction address
                    next_addr = lines[i+1].split('0x')[1].strip()

                    # Compare addresses to determine if branch was taken
                    taken = branch_addr != next_addr
                    branch_outcomes[branch_addr].append(taken)
        i += 1

    return branch_outcomes

def run_lldb_commands(commands):
    cmd = ['lldb', '-b'] + sum([['-o', cmd] for cmd in commands], [])
    print(cmd)
    output = subprocess.check_output(cmd, text=True)
    return output

def analyze_branches(binary_path, branch_points):
    commands = [
        f"target create {binary_path}",
        "breakpoint set --name main",
        "run"
    ]

    for branch in branch_points:
        commands.append(f"breakpoint set -a {branch['address']}")

    commands.extend([
        "breakpoint list",
        "breakpoint command add -o 'command source -c FALSE bp_commands.txt'",
        "continue"
    ])

    output = run_lldb_commands(commands)
    print(output)
    return parse_lldb_output(output)

def main(branches):
    binary_path = '/usr/local/bin/tree'
    outcomes = analyze_branches(binary_path, branches)
    print(outcomes)

if __name__ == "__main__":
    # branches = parse_asm()
    branches = [
        {'address': '0x100007f09', 'instruction': 'je', 'target': '0x100008281'},
        {'address': '0x100006685', 'instruction': 'je', 'target': '0x100006689'}
    ]
    main(branches)
