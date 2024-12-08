import json
import sys

def history(trace):
    pass

if __name__ == '__main__':
    trace = json.loads(sys.stdin.readline())
    
    # TODO: need to load instructions so we can 
    # map address to instruction, and then map
    # instruction to rflags to check if branch was taken

    output = history(trace)

    print(output)
