import lldb

def handle_breakpoint(frame, bp_loc, dict):
    debugger = frame.GetThread().GetProcess().GetTarget().GetDebugger()
    interpreter = debugger.GetCommandInterpreter()
    result = lldb.SBCommandReturnObject()

    interpreter.HandleCommand("p/x $rip", result)
    print(result.GetOutput())

    interpreter.HandleCommand("register read rflags", result)
    print(result.GetOutput())

    frame.GetThread().StepInstruction(True)

    interpreter.HandleCommand("p/x $rip", result)
    print(result.GetOutput())

    frame.GetThread().GetProcess().Continue()

def __lldb_init_module(debugger, internal_dict):
    # Get all breakpoints except main (1)
    for i in range(2, debugger.GetTargetAtIndex(0).GetNumBreakpoints() + 1):
        debugger.HandleCommand(f"breakpoint command add {i} -F commands.handle_breakpoint")
