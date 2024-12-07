#!/usr/bin/env python3
import json
import sys

from operator import xor

def concat(pc, history):
    pc &= 0x7F
    history &= 0x7
    return (pc << 3) | history

class BrandPredictionTable:
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


def predict(branch_history, func):
    predictions = []
    bpt = BrandPredictionTable(func, 10)
    for instruction in branch_history:
        [(addr, taken)] = instruction.items()
        prediction = bpt.update(int(addr, 16), taken)

        predictions.append({
            "address": addr,
            "taken": taken,
            "prediction": prediction
        })

    return predictions

if __name__ == "__main__":
    with open("history.json", "r") as f:
        branch_history = json.load(f)

    hashes = [xor, concat]

    for func in hashes:
        output = predict(branch_history, func)

        correct = 0
        for p in output:
            if p["taken"] == p["prediction"]:
                correct += 1

        print(f"Accuracy: {correct / len(output)}")

    # json.dump(output, sys.stdout, indent=2)
