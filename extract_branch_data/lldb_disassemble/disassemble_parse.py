import lldb
import json
from pathlib import Path
from typing import Dict, List, Optional

def get_section_instructions(debugger, target, section) -> Dict:
    """Extract instructions from a section and return as dictionary."""
    start_addr = section.GetLoadAddress(target)
    size = section.size
    name = section.name
    error = lldb.SBError()

    print(f"\nStarting section {name}")
    print(f"Section size: {size}")
    print(f"Start address: 0x{start_addr:x}")

    if start_addr == lldb.LLDB_INVALID_ADDRESS or size == 0:
        return {
            "name": name,
            "error": "Invalid address or size",
            "instructions": []
        }

    mem_data = target.ReadMemory(
        lldb.SBAddress(start_addr, target),
        size,
        error
    )

    if not error.Success():
        return {
            "name": name,
            "error": error.GetCString(),
            "instructions": []
        }

    # Manual instruction parsing
    instruction_list = []
    current_offset = 0

    while current_offset < size:
        # Try to disassemble single instruction at current offset
        current_addr = start_addr + current_offset

        # Debug check for the problematic instruction
        if current_addr == 0x7ff8121e46cc:
            print(f"\nReached problematic address 0x7ff8121e46cc")
            print(f"Current offset: {current_offset}")
            print(f"Remaining size: {size - current_offset}")

            # Try to manually decode next instruction
            next_addr = current_addr + 3  # Known offset to next instruction
            next_inst = target.GetInstructions(
                lldb.SBAddress(next_addr, target),
                mem_data[current_offset + 3:current_offset + 7]
            )
            if next_inst.GetSize() > 0:
                print(f"Next instruction would be: {next_inst.GetInstructionAtIndex(0)}")

        inst_list = target.GetInstructions(
            lldb.SBAddress(current_addr, target),
            mem_data[current_offset:min(current_offset + 15, size)]
        )

        if inst_list.GetSize() == 0:
            current_offset += 1
            continue

        inst = inst_list.GetInstructionAtIndex(0)
        addr = inst.GetAddress()

        # Get numeric address
        numeric_addr = hex(addr.GetLoadAddress(target))

        # Get symbolic address if available
        symbol = addr.GetSymbol()
        symbolic_addr = str(symbol) if symbol else None

        # Extract address from instruction string as fallback
        inst_str = str(inst)
        if '[' in inst_str and ']' in inst_str:
            addr_start = inst_str.find('[') + 1
            addr_end = inst_str.find(']')
            fallback_addr = inst_str[addr_start:addr_end]
        else:
            fallback_addr = numeric_addr

        instruction_list.append({
            "address": {
                "numeric": hex(addr.GetLoadAddress(target)),
                "symbolic": str(addr.GetSymbol()) if addr.GetSymbol() else None,
                "fallback": fallback_addr
            },
            "instruction": str(inst.GetMnemonic(target)) + " " + str(inst.GetOperands(target)),
            "raw_instruction": str(inst)
        })

        current_offset += inst.GetByteSize()

    return {
        "name": name,
        "error": None,
        "instructions": instruction_list
    }

def collect_module_data(debugger, target, module) -> Dict:
    """Collect all instruction data from a module."""
    module_data = {
        "name": str(module.file),
        "sections": {}
    }

    for section in module.sections:
        # Only process __TEXT section
        if str(section.name) != "__TEXT":
            continue

        perms = section.GetPermissions()
        if perms & lldb.ePermissionsExecutable:
            section_name = str(section.name)
            module_data["sections"][section_name] = {
                "main": get_section_instructions(debugger, target, section),
                "subsections": {}
            }

            for subsec in section:
                # Only process __text subsection
                if str(subsec.name) != "__text":
                    continue

                subsec_perms = subsec.GetPermissions()
                if subsec_perms & lldb.ePermissionsExecutable:
                    subsec_name = str(subsec.name)
                    module_data["sections"][section_name]["subsections"][subsec_name] = \
                        get_section_instructions(debugger, target, subsec)

    return module_data

def save_instructions_to_json(data: Dict, output_path: str):
    """Save the collected data to a JSON file."""
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)

def print_preview(json_path: str):
    """Print preview of first 5 instructions from each section."""
    with open(json_path, 'r') as f:
        data = json.load(f)

    for module_name, module_data in data.items():
        print(f"\nModule: {module_name}")
        for section_name, section_data in module_data["sections"].items():
            print(f"\nSection: {section_name}")

            # Print main section preview
            main_instructions = section_data["main"]["instructions"]
            print("Main section first 5 instructions:")
            for inst in main_instructions[:5]:
                addr_info = inst["address"]
                addr_str = addr_info["symbolic"] if addr_info["symbolic"] else addr_info["numeric"]
                print(f"  {addr_str}: {inst['instruction']}")

            # Print subsection previews
            for subsec_name, subsec_data in section_data["subsections"].items():
                print(f"\nSubsection: {subsec_name}")
                subsec_instructions = subsec_data["instructions"]
                print("First 5 instructions:")
                for inst in subsec_instructions[:5]:
                    addr_info = inst["address"]
                    addr_str = addr_info["symbolic"] if addr_info["symbolic"] else addr_info["numeric"]
                    print(f"  {addr_str}: {inst['instruction']}")

def run_commands(debugger, command=None, result=None, internal_dict=None):
    """Run sequence of commands to disassemble libsystem_c.dylib."""
    target = debugger.CreateTarget("/usr/local/bin/tree")
    if not target:
        print("Failed to create target")
        return

    error = lldb.SBError()
    process = target.Launch(
        debugger.GetListener(),
        None, None, None, None, None,
        None,
        0,
        False,
        error
    )
    if error.Fail() or not process:
        print(f"Failed to launch process: {error.GetCString()}")
        return

    print("Continuing process to ensure code pages are loaded...")
    process.Continue()

    # Collect data for libsystem_c.dylib
    all_modules_data = {}
    for module in target.modules:
        if "libsystem_c.dylib" in str(module.file):
            print(f"Found libsystem_c.dylib at: {module.file}")
            module_data = collect_module_data(debugger, target, module)
            all_modules_data[str(module.file)] = module_data
            break

    # Save to both JSON files
    save_instructions_to_json(all_modules_data, "disassembly.json")
    print(f"\nSaved instruction data to libc_instructions.json and disassembly.json")

    # Print preview
    print("\nPreview of collected instructions:")
    print_preview("disassembly.json")
