#!/usr/bin/env python3
import lldb
import json
import subprocess
import sys
from lib.parse_branches import parse_branches


def run_with_breakpoints(binary, arguments, branches):
    # Initialize debugger
    debugger = lldb.SBDebugger.Create()
    debugger.SetAsync(False)

    # Create target
    target = debugger.CreateTarget(binary)
    if not target:
        print("Failed to create target")
        return

    target.BreakpointCreateByName("main")

    # Launch process
    launch_info = lldb.SBLaunchInfo(arguments.split())
    error = lldb.SBError()
    process = target.Launch(launch_info, error)

    # Wait until we hit main
    thread = process.GetSelectedThread()
    if thread.GetStopReason() == lldb.eStopReasonBreakpoint:
        # Now set all the address breakpoints
        breakpoints = []
        for pc in branches:
            bp = target.BreakpointCreateByAddress(int(pc, 16))
            breakpoints.append(bp)

    branch_trace = []
    process.Continue()

    while process.GetState() == lldb.eStateStopped:
        thread = process.GetSelectedThread()
        frame = thread.GetSelectedFrame()

        pc = frame.GetPC()
        rflags = frame.FindRegister("rflags").GetValueAsUnsigned()

        branch_trace.append({hex(pc): rflags})

        process.Continue()

    return branch_trace


def run_analysis(binary, arguments, filename):
    asm = subprocess.check_output(["otool", "-tv", binary], text=True)
    branches = parse_branches(asm.splitlines())

    branch_trace = run_with_breakpoints(binary, arguments, branches)
    json.dump(branch_trace, sys.stdout, indent=2)
