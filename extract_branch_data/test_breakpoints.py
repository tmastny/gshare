import lldb


def test_breakpoints():
    import json

    with open("lib/parse_branches.json", "r") as f:
        branches = json.load(f)
        #
        # Load shared lib branches
    with open("lldb_disassemble/branch_instructions.json", "r") as f:
        shared_lib_branches = json.load(f)

    branches.update(shared_lib_branches)

    # Get current target
    target = lldb.debugger.GetSelectedTarget()
    if not target:
        print("No target selected")
        return

    # Set breakpoints and count them
    breakpoint_count = 0
    for pc in branches:
        bp = target.BreakpointCreateByAddress(int(pc, 16))
        if bp:
            breakpoint_count += 1

    print(f"Set {breakpoint_count} breakpoints out of {len(branches)} branch addresses")
