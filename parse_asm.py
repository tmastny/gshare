#!/usr/bin/env python3
import sys
import re

# All conditional branch instructions we care about
BRANCH_INSTRUCTIONS = {
    'je', 'jne', 'jg', 'jge', 'jl', 'jle',
    'ja', 'jae', 'jb', 'jbe', 'jo', 'jno',
    'js', 'jns', 'jp', 'jnp'
}

def parse_instruction(line):
    # Example line: ls[0x100003962] <+16>: jne    0x100007554
    match = re.match(r'.*\[(0x[0-9a-f]+)\].*:\s+(\w+)\s+(.*)', line)
    if match:
        addr = match.group(1)
        instruction = match.group(2)
        operands = match.group(3)
        
        if instruction in BRANCH_INSTRUCTIONS:
            target_addr = operands.split()[0]
            return {
                'address': addr,
                'instruction': instruction,
                'target': target_addr
            }
    return None

def main():
    # Read from stdin
    for line in sys.stdin:
        branch = parse_instruction(line)
        if branch:
            print(f"{branch}")

if __name__ == "__main__":
    main()
