#!/usr/bin/env python3
import sys
import json

def parse_lldb_output(output):
    logs = []
    for line in output:
        if "(unsigned long) $" in line and "0x" in line:
            str_hex = "0x" + line.split("0x")[1].strip()
            pc = hex(int(str_hex, 16))
            logs.append(pc)
        elif "rflags = 0x" in line:
            flags = int(line.split("0x")[1].strip(), 16)
            logs.append(flags)

    return logs


def trace(output):
    logs = parse_lldb_output(output)

    trace = []
    for i in range(0, len(logs), 2):
        trace.append({logs[i]: logs[i + 1]})

    return trace


if __name__ == "__main__":
    # lldb -b -s commands.lldb
    output = sys.stdin.readlines()

    data = trace(output)

    # trace.json
    json.dump(data, sys.stdout)
