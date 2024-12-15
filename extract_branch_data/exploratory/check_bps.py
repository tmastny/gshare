import lldb

def check_breakpoints(debugger, command, result, internal_dict):
    # Create target to load the module
    target = debugger.CreateTarget("/usr/local/bin/tree")

    # Create raw address breakpoint
    raw_bp = target.BreakpointCreateByAddress(0x100007f09)
    raw_loc = raw_bp.GetLocationAtIndex(0)
    raw_addr = raw_loc.GetAddress()

    # Get the module and find its text section
    module = target.module["tree"]
    text_section = module.FindSection("__TEXT").FindSubSection("__text")

    # Create SBAddress with section context
    # addr = lldb.SBAddress(text_section, 0x100007f09)
    addr = lldb.SBAddress(0x100007f09, target)
    module_bp = target.BreakpointCreateBySBAddress(addr)
    module_loc = module_bp.GetLocationAtIndex(0)
    module_addr = module_loc.GetAddress()

    # Print initial state
    print(f"Raw breakpoint module: {raw_addr.GetModule()}")
    print(f"Raw breakpoint load address: 0x{raw_loc.GetLoadAddress():x}")
    print(f"Module breakpoint module: {module_addr.GetModule()}")
    print(f"Module breakpoint load address: 0x{module_loc.GetLoadAddress():x}")

    # Break at main and run
    target.BreakpointCreateByName("main")
    process = target.LaunchSimple(None, None, None)

    # this one is actaully resolved after loading,
    # but unlike when you do it from the command line is not
    # in `tree[0x...]`
    mod_bp2 = target.BreakpointCreateBySBAddress(addr)
    mod_bp2_loc = mod_bp2.GetLocationAtIndex(0)
    mod_bp2_addr = mod_bp2_loc.GetAddress()

    # Print load address after running
    print(f"\nAfter running to main:")
    print(f"Raw breakpoint: {raw_bp}")
    print(f"Raw breakpoint module: {raw_addr.GetModule()}")
    print(f"Raw breakpoint load address: 0x{raw_loc.GetLoadAddress():x}")
    print(f"Raw breakpoint load address: 0x{raw_loc.GetAddress()}")
    print(f"Raw breakpoint valid: {raw_bp.IsValid()}")
    print("----")

    print(f"Module breakpoint: {module_bp}")
    print(f"Module breakpoint module: {module_addr.GetModule()}")
    print(f"Module breakpoint load address: 0x{module_loc.GetLoadAddress():x}")
    print(f"Module breakpoint load address: 0x{module_loc.GetAddress()}")
    print("----")

    print(f"Module 2 breakpoint: {mod_bp2}")
    print(f"Module 2 breakpoint module: {mod_bp2_addr.GetModule()}")
    print(f"Module 2 breakpoint file addr: {mod_bp2_addr.GetFileAddress()}")
    print(f"Module 2 breakpoint load addr: {mod_bp2_addr.GetLoadAddress(target)}")
    print(f"Module 2 breakpoint load address: 0x{mod_bp2_loc.GetLoadAddress():x}")
    print(f"Module 2 breakpoint address: 0x{mod_bp2_loc.GetAddress()}")


def __lldb_init_module(debugger, internal_dict):
    debugger.HandleCommand('command script add -f check_bps.check_breakpoints check_bps')
