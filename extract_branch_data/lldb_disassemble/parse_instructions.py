import json

BRANCH_INSTRUCTIONS = {
    "je", "jne", "jg", "jge", "jl", "jle",
    "ja", "jae", "jb", "jbe", "jo", "jno",
    "js", "jns", "jp", "jnp",
}

def extract_branch_info(instruction_str: str) -> tuple[str, str]:
    """Extract branch instruction and target from instruction string.
    Returns tuple of (instruction, target)"""
    # Split on whitespace and get mnemonic and operand
    parts = instruction_str.split(None, 1)  # split on first whitespace only
    if len(parts) != 2:
        return None, None
    return parts[0], parts[1]

def process_instructions(disassembly_path: str) -> dict:
    """Process disassembly file and extract branch instructions"""
    with open(disassembly_path) as f:
        data = json.load(f)

    branch_data = {}

    instructions = (data["/usr/lib/system/libsystem_c.dylib"]
                   ["sections"]["__TEXT"]
                   ["subsections"]["__text"]
                   ["instructions"])

    for inst in instructions:
        mnemonic, operand = extract_branch_info(inst["instruction"])
        if mnemonic in BRANCH_INSTRUCTIONS:
            addr = inst["address"]["numeric"]
            branch_data[addr] = {
                "instruction": mnemonic,
                "target": operand
            }

    return branch_data

def main():
    branch_data = process_instructions("disassembly.json")

    # Save results
    with open("branch_instructions.json", "w") as f:
        json.dump(branch_data, f, indent=2)

    print(f"Found {len(branch_data)} branch instructions")

if __name__ == "__main__":
    main()
