#!/usr/bin/env python3
import json
import sys


def will_branch_be_taken(instruction, flags):
    """Determine if branch will be taken based on flags register"""
    ZF = (flags >> 6) & 1  # Zero flag
    SF = (flags >> 7) & 1  # Sign flag
    CF = (flags >> 0) & 1  # Carry flag
    OF = (flags >> 11) & 1  # Overflow flag
    PF = (flags >> 2) & 1  # Parity flag

    match instruction:
        case "je":  # Jump if equal (ZF=1)
            return ZF == 1
        case "jne":  # Jump if not equal (ZF=0)
            return ZF == 0
        case "jg":  # Jump if greater (ZF=0 and SF=OF)
            return ZF == 0 and SF == OF
        case "jge":  # Jump if greater or equal (SF=OF)
            return SF == OF
        case "jl":  # Jump if less (SF≠OF)
            return SF != OF
        case "jle":  # Jump if less or equal (ZF=1 or SF≠OF)
            return ZF == 1 or SF != OF
        case "ja":  # Jump if above (CF=0 and ZF=0)
            return CF == 0 and ZF == 0
        case "jae":  # Jump if above or equal (CF=0)
            return CF == 0
        case "jb":  # Jump if below (CF=1)
            return CF == 1
        case "jbe":  # Jump if below or equal (CF=1 or ZF=1)
            return CF == 1 or ZF == 1
        case "jo":  # Jump if overflow (OF=1)
            return OF == 1
        case "jno":  # Jump if not overflow (OF=0)
            return OF == 0
        case "js":  # Jump if sign (SF=1)
            return SF == 1
        case "jns":  # Jump if not sign (SF=0)
            return SF == 0
        case "jp":  # Jump if parity (PF=1)
            return PF == 1
        case "jnp":  # Jump if not parity (PF=0)
            return PF == 0


def history(trace, branches):
    """Generate branch history from trace data"""
    branch_history = []  # sequence of taken/not-taken (1/0)

    for entry in trace:
        for pc, flags in entry.items():
            if pc in branches:
                instruction = branches[pc]["instruction"]
                taken = will_branch_be_taken(instruction, flags)
                branch_history.append({pc: 1 if taken else 0})

    return branch_history


if __name__ == "__main__":
    with open("trace.json", "r") as f:
        trace = json.load(f)

    with open("parse_branches.json", "r") as f:
        branches = json.load(f)

    output = history(trace, branches)

    json.dump(output, sys.stdout, indent=2)
