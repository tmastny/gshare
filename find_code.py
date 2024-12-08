#!/usr/bin/env python3
import sys
import re


def parse_code_sections(line):
    # Looking for lines with 'code' type
    # Example: 0x00000001 code [0x0000000100003940-0x00000001000073df) r-x ...
    match = re.match(r".*code\s+\[(0x[0-9a-f]+)-(0x[0-9a-f]+)\).*r-x", line)
    if match:
        start_addr = match.group(1)
        end_addr = match.group(2)
        return {"start": start_addr, "end": end_addr}
    return None


def main():
    for line in sys.stdin:
        section = parse_code_sections(line)
        if section:
            print(f"{section}")


if __name__ == "__main__":
    main()
