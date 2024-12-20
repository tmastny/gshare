#include <lldb/API/LLDB.h>
#include <vector>
#include <string>
#include <iostream>
#include <filesystem>

class BranchTracer {
    lldb::SBDebugger debugger;
    lldb::SBTarget target;
    std::vector<lldb::SBBreakpoint> breakpoints;

public:
    BranchTracer() {
        lldb::SBDebugger::Initialize();
        debugger = lldb::SBDebugger::Create();
        debugger.SetAsync(false);
    }

    ~BranchTracer() {
        lldb::SBDebugger::Terminate();
    }

    void createTarget(const char* binary) {
        target = debugger.CreateTarget(binary);
        if (!target.IsValid()) {
            std::cerr << "Failed to create target\n";
            exit(1);
        }
    }

    void setBreakpoints(
        const std::vector<uint64_t>& addresses,
        const std::vector<char*>& args
    ) {
        target.BreakpointCreateByName("main");

        // Launch and wait for main
        lldb::SBLaunchInfo launch_info(const_cast<const char**>(args.data()));
        lldb::SBError error;
        auto process = target.Launch(launch_info, error);

        if (!error.Success()) {
            std::cerr << "Launch failed: " << error.GetCString() << "\n";
            exit(1);
        }

        for (auto addr : addresses) {
            auto bp = target.BreakpointCreateByAddress(addr);
            breakpoints.push_back(bp);
        }

        // Run and collect trace
        while (process.GetState() == lldb::eStateStopped) {
            auto thread = process.GetSelectedThread();
            auto frame = thread.GetFrameAtIndex(0);

            uint64_t pc = frame.GetPC();
            uint64_t rflags = frame.FindRegister("rflags").GetValueAsUnsigned();

            // Simple CSV output: pc,rflags
            std::cout << std::hex << "0x" << pc << ","
                << rflags << "\n";

            process.Continue();
        }
    }
};

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Usage: " << argv[0] << " <binary> <arguments>\n";
        return 1;
    }

    std::vector<char*> args;
        for (int i = 2; i < argc; i++) {
            args.push_back(argv[i]);
    }

    // Read addresses from stdin
    std::vector<uint64_t> addresses;
    std::string line;
    while (std::getline(std::cin, line)) {
        uint64_t addr = std::stoull(line, nullptr, 16);
        addresses.push_back(addr);
    }

    BranchTracer tracer;
    tracer.createTarget(argv[1]);
    tracer.setBreakpoints(addresses, args);

    return 0;
}
