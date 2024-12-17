#!/usr/bin/env python3
import json
import argparse
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def create_history_heatmap(branch_history, window_size=32):
    # Convert branch history into rows of window_size
    history = [1 if list(inst.values())[0] else 0 for inst in branch_history]
    rows = [history[i:i+window_size] for i in range(0, len(history), window_size)]
    # Pad last row if needed
    if len(rows[-1]) < window_size:
        rows[-1].extend([0] * (window_size - len(rows[-1])))

    plt.figure(figsize=(15, 10))
    sns.heatmap(rows, cmap='binary', cbar=False)
    plt.title('Branch History Heatmap')
    plt.xlabel('Position in Window')
    plt.ylabel('Window Number')

def plot_branch_timeline(branch_history):
    addresses = [int(list(inst.keys())[0], 16) for inst in branch_history]
    taken = [list(inst.values())[0] for inst in branch_history]

    plt.figure(figsize=(15, 5))
    plt.scatter(range(len(addresses)), addresses, c=taken, cmap='coolwarm', alpha=0.5)
    plt.title('Branch Execution Timeline')
    plt.xlabel('Execution Order')
    plt.ylabel('Branch Address')
    plt.colorbar(label='Taken/Not Taken')

def analyze_patterns(branch_history, pattern_length=8):
    history = [1 if list(inst.values())[0] else 0 for inst in branch_history]
    history_str = ''.join(map(str, history))

    patterns = {}
    for i in range(len(history_str) - pattern_length):
        pattern = history_str[i:i+pattern_length]
        patterns[pattern] = patterns.get(pattern, 0) + 1

    # Convert to DataFrame for plotting
    df = pd.DataFrame.from_dict(patterns, orient='index', columns=['count'])
    df = df.sort_values('count', ascending=False).head(20)

    plt.figure(figsize=(15, 8))
    df['count'].plot(kind='bar')
    plt.title(f'Most Common {pattern_length}-bit Patterns')
    plt.xlabel('Pattern')
    plt.ylabel('Frequency')
    plt.xticks(rotation=45)

def main():
    parser = argparse.ArgumentParser(description="Branch History Visualizer")
    parser.add_argument("branch_data", help="Path to the branch trace file")
    parser.add_argument("--window", type=int, default=32,
                      help="Window size for heatmap (default: 32)")
    parser.add_argument("--pattern", type=int, default=8,
                      help="Pattern length for analysis (default: 8)")
    parser.add_argument("--output", type=str, default="branch_visualization",
                      help="Output prefix for saved plots")

    args = parser.parse_args()

    # Load branch data
    with open(args.branch_data, "r") as f:
        branch_data = json.load(f)

    binary = branch_data["binary"]
    arguments = branch_data.get("arguments", "")
    branch_history = branch_data["branch_history"]

    print("================================")
    print(f"Analyzing: {binary} {arguments}")
    print(f"Total branches: {len(branch_history)}")
    print("--------------------------------")

    # Create visualizations
    create_history_heatmap(branch_history, args.window)
    plt.savefig(f"{args.output}_heatmap.png")

    plot_branch_timeline(branch_history)
    plt.savefig(f"{args.output}_timeline.png")

    analyze_patterns(branch_history, args.pattern)
    plt.savefig(f"{args.output}_patterns.png")

    print(f"Visualizations saved with prefix: {args.output}")

    # Optional: show plots interactively
    # plt.show()

if __name__ == "__main__":
    main()
