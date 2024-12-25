import lldb
import json
from pathlib import Path
from typing import Dict, List, Optional

def debug_memory(target, start_addr, mem_data, section, cutoff_addr=0x7ff8121e46cc):
    """Debug memory content around the cutoff address"""
    print(f"\nDEBUG MEMORY:")
    print(f"Section: {section.name}")
    print(f"Section start address: 0x{start_addr:x}")
    print(f"Section expected size: {section.size}")
    print(f"Actual memory read size: {len(mem_data)} bytes")

    # Convert cutoff address to offset
    offset = cutoff_addr - start_addr
    print(f"Offset from start: {offset} bytes")

    if section.name == "__text":
        next_inst_addr = 0x7ff8121e46cf
        next_inst_offset = next_inst_addr - start_addr
        if next_inst_offset < len(mem_data):
            print(f"\nChecking next known instruction at 0x{next_inst_addr:x}")
            print(f"Bytes at that location: {mem_data[next_inst_offset:next_inst_offset+4].hex()}")

            # Try to disassemble just this instruction
            next_inst = target.GetInstructions(
                lldb.SBAddress(next_inst_addr, target),
                mem_data[next_inst_offset:next_inst_offset+4]
            )
            if next_inst.GetSize() > 0:
                print(f"Disassembled instruction: {next_inst.GetInstructionAtIndex(0)}")

    if offset < len(mem_data):
        print(f"Memory continues after cutoff address")
        # Print some bytes before and after the cutoff
        start_slice = max(0, offset - 16)
        end_slice = min(len(mem_data), offset + 16)
        print(f"Bytes around cutoff point (offset {offset}):")
        print(f"Hex dump: {mem_data[start_slice:end_slice].hex()}")
    else:
        print(f"Memory stops before cutoff address")
        print(f"Last few bytes: {mem_data[-16:].hex()}")


def get_section_instructions(debugger, target, section) -> Dict:
    """Extract instructions from a section and return as dictionary."""
    start_addr = section.GetLoadAddress(target)
    size = section.size
    name = section.name
    error = lldb.SBError()

    if start_addr == lldb.LLDB_INVALID_ADDRESS or size == 0:
        return {
            "name": name,
            "error": "Invalid address or size",
            "instructions": []
        }

    # Read the raw bytes
    mem_data = target.ReadMemory(
        lldb.SBAddress(start_addr, target),
        size,
        error
    )

    debug_memory(target, start_addr, mem_data, section)

    if not error.Success():
        return {
            "name": name,
            "error": error.GetCString(),
            "instructions": []
        }

    # Get instructions from the bytes
    instructions = target.GetInstructions(
        lldb.SBAddress(start_addr, target),
        mem_data
    )

    if not instructions or instructions.GetSize() == 0:
        return {
            "name": name,
            "error": "Failed to read instructions",
            "instructions": []
        }

    # Convert instructions to serializable format
    instruction_list = []
    for i in range(instructions.GetSize()):
        inst = instructions.GetInstructionAtIndex(i)
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
                "numeric": numeric_addr,
                "symbolic": symbolic_addr,
                "fallback": fallback_addr
            },
            "instruction": str(inst.GetMnemonic(target)) + " " + str(inst.GetOperands(target)),
            "raw_instruction": str(inst)
        })

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
        perms = section.GetPermissions()
        if perms & lldb.ePermissionsExecutable:
            section_name = str(section.name)
            module_data["sections"][section_name] = {
                "main": get_section_instructions(debugger, target, section),
                "subsections": {}
            }

            for subsec in section:
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
