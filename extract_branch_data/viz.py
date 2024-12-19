#!/usr/bin/env python3
import json
import argparse
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from matplotlib.colors import LogNorm  # Add this import

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

def analyze_patterns_with_rotations(branch_history, pattern_length=8):
    history = [1 if list(inst.values())[0] else 0 for inst in branch_history]
    history_str = ''.join(map(str, history))

    def get_rotations(pattern):
        rotations = set()
        for i in range(len(pattern)):
            rotations.add(pattern[i:] + pattern[:i])
        return rotations

    # Count patterns including rotations
    pattern_groups = {}
    seen_patterns = set()

    for i in range(len(history_str) - pattern_length):
        pattern = history_str[i:i+pattern_length]
        if pattern not in seen_patterns:
            rotations = get_rotations(pattern)
            total_count = 0
            for rot in rotations:
                total_count += history_str.count(rot)
                seen_patterns.add(rot)
            pattern_groups[pattern] = {
                'count': total_count,
                'rotations': list(rotations)
            }

    # Convert to DataFrame for plotting
    df = pd.DataFrame.from_dict(pattern_groups, orient='index')
    df = df.sort_values('count', ascending=False).head(10)

    # Create visualization
    plt.figure(figsize=(15, 10))

    # Create the bar plot
    plt.bar(range(len(df)), df['count'])

    # Customize the plot
    plt.title(f'Most Common {pattern_length}-bit Patterns (Including Rotations)')
    plt.xlabel('Pattern (Representative)')
    plt.ylabel('Total Frequency (All Rotations)')

    # Add pattern labels
    plt.xticks(range(len(df)), df.index, rotation=45, ha='right')

    # Add rotation information
    for idx, row in df.iterrows():
        y_pos = row['count']
        rots = '\n'.join(sorted(row['rotations']))
        plt.text(df.index.get_loc(idx), y_pos, f'\nRotations:\n{rots}',
                ha='center', va='bottom', fontsize=8)

    plt.tight_layout()

def analyze_pattern_lengths(branch_history, min_length=4, max_length=16):
    history = [1 if list(inst.values())[0] else 0 for inst in branch_history]
    history_str = ''.join(map(str, history))

    def get_rotations(pattern):
        rotations = set()
        for i in range(len(pattern)):
            rotations.add(pattern[i:] + pattern[:i])
        return rotations

    # Collect stats for each pattern length
    length_stats = {}
    for pattern_length in range(min_length, max_length + 1):
        pattern_groups = {}
        seen_patterns = set()

        for i in range(len(history_str) - pattern_length):
            pattern = history_str[i:i+pattern_length]
            if pattern not in seen_patterns:
                rotations = get_rotations(pattern)
                total_count = 0
                for rot in rotations:
                    total_count += history_str.count(rot)
                    seen_patterns.add(rot)
                pattern_groups[pattern] = total_count

        # Get statistics for this length
        if pattern_groups:
            top_counts = sorted(pattern_groups.values(), reverse=True)
            length_stats[pattern_length] = {
                'max_count': max(pattern_groups.values()),
                'unique_patterns': len(pattern_groups),
                'top_3_counts': top_counts[:3],
                'count_distribution': top_counts
            }

    # Create visualization
    plt.figure(figsize=(15, 10))

    # Plot 1: Maximum pattern frequency vs pattern length
    plt.subplot(2, 1, 1)
    plt.plot([k for k in length_stats.keys()],
             [v['max_count'] for v in length_stats.values()],
             'o-', label='Most frequent pattern')
    plt.plot([k for k in length_stats.keys()],
             [v['top_3_counts'][1] if len(v['top_3_counts']) > 1 else 0 for v in length_stats.values()],
             'o-', label='2nd most frequent')
    plt.plot([k for k in length_stats.keys()],
             [v['top_3_counts'][2] if len(v['top_3_counts']) > 2 else 0 for v in length_stats.values()],
             'o-', label='3rd most frequent')
    plt.title('Pattern Frequency vs Length')
    plt.xlabel('Pattern Length')
    plt.ylabel('Frequency')
    plt.legend()
    plt.grid(True)

    # Plot 2: Number of unique patterns vs length
    plt.subplot(2, 1, 2)
    plt.plot([k for k in length_stats.keys()],
             [v['unique_patterns'] for v in length_stats.values()],
             'o-')
    plt.title('Number of Unique Patterns vs Length')
    plt.xlabel('Pattern Length')
    plt.ylabel('Number of Unique Patterns')
    plt.grid(True)

    plt.tight_layout()

    # Print analysis
    print("\nPattern Length Analysis:")
    for length, stats in length_stats.items():
        print(f"\nLength {length}:")
        print(f"Most frequent pattern appears {stats['max_count']} times")
        print(f"Number of unique patterns: {stats['unique_patterns']}")
        print(f"Top 3 frequencies: {stats['top_3_counts']}")

import math
from collections import Counter

def get_rotations(pattern):
    rotations = set()
    for i in range(len(pattern)):
        rotations.add(pattern[i:] + pattern[:i])
    return rotations

def calculate_gini(values):
    values = sorted(values)
    n = len(values)
    mean = sum(values) / n
    abs_diff_sum = sum(abs(xi - xj) for i, xi in enumerate(values)
                                   for j, xj in enumerate(values))
    gini = abs_diff_sum / (2 * n * n * mean)
    return gini

def calculate_entropy(values):
    total = sum(values)
    frequencies = [count/total for count in values]
    return -sum(p * math.log2(p) for p in frequencies)

def calculate_metrics(branch_history, min_length=4, max_length=10):
    # Convert to bit string
    history = [1 if list(inst.values())[0] else 0 for inst in branch_history]
    history_str = ''.join(map(str, history))

    results = {}
    for length in range(min_length, max_length + 1):
        # Count patterns (unique up to rotation)
        pattern_counts = {}
        seen_patterns = set()

        for i in range(len(history_str) - length):
            pattern = history_str[i:i+length]
            if pattern not in seen_patterns:
                rotations = get_rotations(pattern)
                count = 0
                for rot in rotations:
                    count += history_str.count(rot)
                    seen_patterns.add(rot)
                pattern_counts[pattern] = count

        # Get values for calculations
        values = list(pattern_counts.values())

        results[length] = {
            'entropy': calculate_entropy(values),
            'gini': calculate_gini(values),
            'unique_patterns': len(pattern_counts)
        }

    # Print results
    print("\nPattern Analysis Results:")
    print("Length | Entropy | Gini  | Unique Patterns")
    print("--------|---------|-------|----------------")
    for length, metrics in results.items():
        print(f"{length:6d} | {metrics['entropy']:7.3f} | {metrics['gini']:5.3f} | {metrics['unique_patterns']:>15d}")

def plot_pattern_frequency_heatmap(branch_history, min_length=4, max_length=10):
    # Get max patterns across all lengths for y-axis
    max_patterns = 0
    pattern_frequencies = {}

    # Collect frequencies for each length
    for length in range(min_length, max_length + 1):
        pattern_counts = {}
        seen_patterns = set()
        history = [1 if list(inst.values())[0] else 0 for inst in branch_history]
        history_str = ''.join(map(str, history))

        for i in range(len(history_str) - length):
            pattern = history_str[i:i+length]
            if pattern not in seen_patterns:
                rotations = get_rotations(pattern)
                count = 0
                for rot in rotations:
                    count += history_str.count(rot)
                    seen_patterns.add(rot)
                pattern_counts[pattern] = count

        # Sort by frequency and normalize
        total = sum(pattern_counts.values())
        frequencies = sorted([count/total for count in pattern_counts.values()], reverse=True)
        pattern_frequencies[length] = frequencies
        max_patterns = max(max_patterns, len(frequencies))

    # Create data matrix for heatmap
    data = np.zeros((max_patterns, max_length - min_length + 1))
    for i, length in enumerate(range(min_length, max_length + 1)):
        freqs = pattern_frequencies[length]
        data[:len(freqs), i] = freqs
        data[len(freqs):, i] = np.nan  # Mark empty cells as NaN

    # Create heatmap with log scale
    plt.figure(figsize=(12, 8))
    heatmap = sns.heatmap(data,
                         cmap='viridis',
                         xticklabels=range(min_length, max_length + 1),
                         yticklabels=range(1, max_patterns + 1),
                         mask=np.isnan(data),
                         norm=LogNorm())  # Add log scale normalization

    plt.title('Pattern Frequency Distribution by Length (Log Scale)')
    plt.xlabel('Pattern Length')
    plt.ylabel('Pattern Rank')
    plt.colorbar(heatmap.collections[0], label='Frequency (log scale)')


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

    analyze_patterns_with_rotations(branch_history, args.pattern)
    plt.savefig(f"{args.output}_patterns_with_rotations.png")

    analyze_pattern_lengths(branch_history, min_length=4, max_length=10)
    plt.savefig(f"{args.output}_pattern_lengths.png")

    print(f"Visualizations saved with prefix: {args.output}")

    # Optional: show plots interactively
    # plt.show()

if __name__ == "__main__":
    main()
