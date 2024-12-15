import lldb

def file_load_addr(debugger, command, result, internal_dict):
    target = debugger.CreateTarget("/usr/local/bin/tree")
    target.BreakpointCreateByName("main")
    target.LaunchSimple(None, None, None)

    bp = target.BreakpointCreateByAddress(0x100007f09)
    loc = bp.GetLocationAtIndex(0)
    addr = loc.GetAddress()

    print(f"File address: 0x{addr.GetFileAddress():x}")
    print(f"Load address: 0x{addr.GetLoadAddress(target):x}")


def __lldb_init_module(debugger, internal_dict):
    debugger.HandleCommand('command script add -f file_load_addr.file_load_addr file_load_addr')
