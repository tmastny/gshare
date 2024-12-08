#!/usr/bin/env python3
import sys

def parse_lldb_output():
    """Parse LLDB output to extract pc and rflags"""
    branch_data = []

    for line in sys.stdin:
        if "rflags = 0x" in line:
            flags = int(line.split('0x')[1].strip(), 16)
            branch_data.append({'flags': flags})
        elif "(unsigned long) $" in line and "0x" in line:
            pc = line.split('0x')[1].strip()
            branch_data.append({'pc': pc})

    return branch_data

if __name__ == "__main__":
    data = parse_lldb_output()
    for entry in data:
        print(entry)
