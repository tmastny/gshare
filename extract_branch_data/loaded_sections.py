#!/usr/bin/env python3

import lldb

def print_code_section(debugger, command, result, internal_dict):
    """
    Prints code section (__TEXT/__text) for modules with address ranges
    Usage: code_section [module_name]
    Example: code_section libsystem_c.dylib
    """
    target = debugger.GetSelectedTarget()
    if not target:
        print("No target selected")
        return

    module_filter = command.strip()

    for module in target.modules:
        # Skip if module filter is provided and doesn't match
        if module_filter and not (module_filter in str(module.file)):
            continue

        print(f"\nModule: {module.file}")

        # Find __TEXT section
        text_section = None
        for section in module.sections:
            if section.name == "__TEXT":
                text_section = section
                break

        if text_section:
            load_addr = text_section.GetLoadAddress(target)
            if load_addr != lldb.LLDB_INVALID_ADDRESS:
                section_end = load_addr + text_section.size
                print(f"  Section: {text_section.name}")
                print(f"    Load Address: 0x{load_addr:x}")
                print(f"    Range: 0x{load_addr:x} - 0x{section_end:x}")
                print(f"    File Address: 0x{text_section.file_addr:x}")
                print(f"    Size: {text_section.size} bytes")

                # Find __text subsection
                for subsection in text_section:
                    if subsection.name == "__text":
                        sub_load_addr = subsection.GetLoadAddress(target)
                        if sub_load_addr != lldb.LLDB_INVALID_ADDRESS:
                            subsection_end = sub_load_addr + subsection.size
                            print(f"    Subsection: {subsection.name}")
                            print(f"      Load Address: 0x{sub_load_addr:x}")
                            print(f"      Range: 0x{sub_load_addr:x} - 0x{subsection_end:x}")
                            print(f"      File Address: 0x{subsection.file_addr:x}")
                            print(f"      Size: {subsection.size} bytes")
        else:
            print("  No __TEXT section found")

def __lldb_init_module(debugger, internal_dict):
    # Add command to LLDB
    debugger.HandleCommand('command script add -f loaded_sections.print_code_section code_section')
    print('The "code_section" command has been installed')
