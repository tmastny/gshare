import lldb

def run_commands(debugger, command=None, result=None, internal_dict=None):
    """Run sequence of commands to disassemble libsystem_c.dylib"""

    # Create target
    print("Creating target...")
    target = debugger.CreateTarget("/usr/local/bin/tree")
    if not target:
        print("Failed to create target")
        return

    # Launch process
    print("Launching process...")
    error = lldb.SBError()
    process = target.Launch(debugger.GetListener(), None, None, None, None, None,
                          None, 0, False, error)

    if not process or error.Fail():
        print(f"Failed to launch process: {error.GetCString()}")
        return

    # Find libsystem_c.dylib module
    print("\nLooking for libsystem_c.dylib...")
    lib_c = None
    for module in target.modules:
        if "libsystem_c.dylib" in str(module.file):
            lib_c = module
            print(f"Found at: {module.file}")
            break

    if not lib_c:
        print("Could not find libsystem_c.dylib")
        return

    # Find __TEXT,__text section
    print("\nLooking for __TEXT,__text section...")
    text_section = None
    for section in lib_c.sections:
        if section.name == "__TEXT":
            for subsection in section:
                if subsection.name == "__text":
                    text_section = subsection
                    break
            if text_section:
                break

    if not text_section:
        print("Could not find __TEXT,__text section")
        return

    # Get section details
    start_addr = text_section.GetLoadAddress(target)
    size = text_section.size
    print(f"Section found:")
    print(f"  Load Address: 0x{start_addr:x}")
    print(f"  Size: {size} bytes")

    # Read memory
    print("\nReading memory...")
    error = lldb.SBError()
    memory_buffer = target.ReadMemory(lldb.SBAddress(start_addr, target), size, error)
    if not error.Success():
        print(f"Error reading memory: {error.GetCString()}")
        return

    # Get instructions
    print("Disassembling...")
    instructions = target.GetInstructions(lldb.SBAddress(start_addr, target), memory_buffer)

    # Print instructions
    print(f"\nFirst 10 instructions of {instructions.GetSize()} total:")
    for i in range(min(10, instructions.GetSize())):
        inst = instructions.GetInstructionAtIndex(i)
        print(f"{inst.GetAddress()}: {inst}")
