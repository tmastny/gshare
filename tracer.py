import subprocess
import json
import re
from pathlib import Path
import argparse
from datetime import datetime


class LLDBTracer:
    def __init__(self, output_file=None):
        self.output_file = output_file
        self.branch_count = 0

    def run_lldb_command(self, cmd):
        process = subprocess.Popen(
            # what do these flags do?
            # -b: batch mode
            # -o: execute command
            ["lldb", "-b", "-o", cmd],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        output, error = process.communicate()
        return output

    def log_branch(self, address, instruction, taken, target_addr):
        timestamp = datetime.now().strftime("%H:%M:%S.%f")
        log_entry = f"{timestamp},{self.branch_count},0x{address:x},{instruction},{taken},0x{target_addr:x}\n"

        if self.output_file:
            with open(self.output_file, "a") as f:
                f.write(log_entry)
        else:
            print(log_entry, end="")

        self.branch_count += 1

    def trace_program(self, program_path, args=[]):
        # Start LLDB session
        lldb_commands = [
            f"target create {program_path}",
            "breakpoint set --name main",  # Initial breakpoint
            "process launch",  # Start the program
            "disassemble",  # Get initial disassembly
        ]

        for cmd in lldb_commands:
            output = self.run_lldb_command(cmd)
            # Process output to find branch instructions
            # Set breakpoints at those addresses

        # Continue execution and process breakpoint hits
        while True:
            output = self.run_lldb_command("continue")
            if "Process exited" in output:
                break

            # Process breakpoint hit
            # Get current instruction
            # Determine if branch was taken
            # Log information


def main():
    parser = argparse.ArgumentParser(description="Branch trace utility")
    parser.add_argument("program", help="Program to trace")
    parser.add_argument("args", nargs="*", help="Arguments for the program")
    parser.add_argument("-o", "--output", help="Output file for trace")
    args = parser.parse_args()

    tracer = LLDBTracer(args.output)
    tracer.trace_program(args.program, args.args)


if __name__ == "__main__":
    main()
