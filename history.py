import json


def history(trace, branches):
    pass


if __name__ == "__main__":
    with open("trace.json", "r") as f:
        trace = json.load(f)

    with open("parse_branches.json", "r") as f:
        branches = json.load(f)

    output = history(trace, branches)

    print(output)
