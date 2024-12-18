#!/usr/bin/env python3
import sys
import re
import json

# All conditional branch instructions we care about
BRANCH_INSTRUCTIONS = {
    "je",
    "jne",
    "jg",
    "jge",
    "jl",
    "jle",
    "ja",
    "jae",
    "jb",
    "jbe",
    "jo",
    "jno",
    "js",
    "jns",
    "jp",
    "jnp",
}


def parse_instruction(line):
    # Match new format: address instruction operands
    # Example: 0000000100004688 pushq %rbp
    match = re.match(r"([0-9a-f]+)\s+(\w+)\s+(.*)", line)
    if match:
        addr = hex(int(match.group(1), 16))  # Convert to hex string with 0x prefix
        instruction = match.group(2)
        operands = match.group(3).strip()

        if instruction in BRANCH_INSTRUCTIONS:
            # For branch instructions, extract target address from operands
            # Note: May need to adjust based on exact format of branch targets
            target_addr = operands.split()[0]
            if not target_addr.startswith("0x"):
                target_addr = hex(int(target_addr, 16))
            return (addr, {"instruction": instruction, "target": target_addr})
    return None, None


def parse_branches(asm: list[str]):
    branches = {}
    for line in asm:
        # Skip section headers and function names
        if line.startswith("_") or line.startswith("(") or not line.strip():
            continue

        addr, data = parse_instruction(line)
        if addr:
            branches[addr] = data

    return branches


if __name__ == "__main__":
    # otool -tv /usr/local/bin/tree
    asm = sys.stdin.readlines()
    branches = parse_branches(asm)

    # parse_branches.json
    json.dump(branches, sys.stdout, indent=2)
