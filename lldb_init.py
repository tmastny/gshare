import lldb


def __lldb_init_module(debugger, internal_dict):
    # Get all breakpoints except main (1)
    for i in range(2, debugger.GetTargetAtIndex(0).GetNumBreakpoints() + 1):
        # Add the command source to each breakpoint individually
        debugger.HandleCommand(
            f"breakpoint command add {i} -o 'command source bp_commands.lldb'"
        )
