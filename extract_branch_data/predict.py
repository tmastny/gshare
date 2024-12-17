#!/usr/bin/env python3
import json
import argparse

from operator import xor


def make_concat(size):
    history_bits = size // 2
    pc_bits = size - history_bits

    def concat(pc, history):
        pc_mask = (1 << pc_bits) - 1
        history_mask = (1 << history_bits) - 1
        return ((pc & pc_mask) << history_bits) | (history & history_mask)

    return concat


class BranchPredictionTable:
    def __init__(self, hash, size, method="2bit"):
        self.bitmask = (1 << size) - 1

        self.method = method
        self.hash = hash
        self.table = {}
        self.history = 0

    def counter(self, taken, prediction):
        if self.method == "2bit":
            if taken:
                return min(3, prediction + 1)
            else:
                return max(0, prediction - 1)
        elif self.method == "1bit":
            return taken

    def update(self, addr, taken):
        addr &= self.bitmask
        history = self.history & self.bitmask

        key = self.hash(addr, history)

        prediction = self.table.get(key, 1)

        self.table[key] = self.counter(taken, prediction)
        self.history = (self.history << 1) | taken

        return prediction >= 2 if self.method == "2bit" else prediction


def predict(branch_history, func, size=10, method="2bit"):
    predictions = []
    bpt = BranchPredictionTable(func, size, method)
    for instruction in branch_history:
        [(addr, taken)] = instruction.items()
        prediction = bpt.update(int(addr, 16), taken)
        predictions.append({"address": addr, "taken": taken, "prediction": prediction})
    return predictions


def main():
    parser = argparse.ArgumentParser(description="Branch Prediction Simulator")
    parser.add_argument("branch_data", help="Path to the branch trace file")
    parser.add_argument(
        "--size",
        type=int,
        default=10,
        help="Size of the prediction table (default: 10)",
    )
    parser.add_argument(
        "--method",
        choices=["1bit", "2bit"],
        default="2bit",
        help="Counter method (default: 2bit)",
    )

    args = parser.parse_args()

    with open(args.branch_data, "r") as f:
        branch_data = json.load(f)

    binary = branch_data["binary"]
    arguments = branch_data.get("arguments", "")
    branch_history = branch_data["branch_history"]

    print("================================")
    print(f"Program: {binary} {arguments}")
    print(f"Table size: {args.size} bits ({2**args.size} entries)")
    print(f"Counter method: {args.method}")
    print("--------------------------------")

    hashes = {"gshare": xor, "concat": make_concat(args.size)}

    results = []
    for name, func in hashes.items():
        output = predict(branch_history, func, size=args.size, method=args.method)
        correct = sum(1 for p in output if p["taken"] == p["prediction"])
        accuracy = correct / len(output)
        results.append((name, accuracy))

    max_name_len = max(len(name) for name, _ in results)
    for name, accuracy in results:
        print(f"{name:<{max_name_len}} accuracy: {accuracy:.4f}")


if __name__ == "__main__":
    main()
