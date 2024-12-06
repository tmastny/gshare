import sys
from branch_sequences import generate_branch_sequences, hash_concat, hash_gshare, print_key_table, analyze_aliases, print_alias_analysis
from predictions import simulate_prediction, print_prediction_trace, print_prediction_accuracy

def run_4bit_history_analysis():
    # Test parameters
    pattern = "1101"
    branch_addr = "1010"
    branch_patterns = {branch_addr: pattern}

    print("=" * 50)
    print("Branch Pattern Analysis")
    print("=" * 50)
    print(f"Pattern: {pattern}")
    print(f"Branch Address: {branch_addr}")
    print("-" * 50)

    # Run pattern analysis
    print("\nConcatenation Scheme:")
    concat_data = generate_branch_sequences(branch_addr, pattern, hash_concat)
    print_key_table(concat_data)
    print_alias_analysis(analyze_aliases(concat_data))

    print("\nGshare Scheme:")
    gshare_data = generate_branch_sequences(branch_addr, pattern, hash_gshare)
    print_key_table(gshare_data)
    print_alias_analysis(analyze_aliases(gshare_data))

    print("\n" + "=" * 50)
    print("Branch Prediction Simulation")
    print("=" * 50)

    # Run 1-bit predictor simulation
    print("\n1-Bit Predictor:")
    print("-" * 50)
    results_1bit = simulate_prediction(branch_patterns, predictor_type="1bit")
    print_prediction_trace(results_1bit, num_to_print=10)
    print_prediction_accuracy(results_1bit)

    # Run 2-bit predictor simulation
    print("\n2-Bit Predictor:")
    print("-" * 50)
    results_2bit = simulate_prediction(branch_patterns, predictor_type="2bit")
    print_prediction_trace(results_2bit, num_to_print=10)
    print_prediction_accuracy(results_2bit)

def run_multi_branch_analysis():
    branch_patterns = {"0011": "1100", "1100": "0011"}

    print("\nMulti-Branch Pattern Analysis")
    print("=" * 50)

    schemes = {"concat": {"func": hash_concat, "data": []}, "gshare": {"func": hash_gshare, "data": []}}
    for scheme in schemes.values():
        for addr, pattern in branch_patterns.items():
            scheme["data"].extend(generate_branch_sequences(addr, pattern, scheme["func"]))

    print("\nConcatenation Scheme:")
    print_key_table(schemes["concat"]["data"])
    print_alias_analysis(analyze_aliases(schemes["concat"]["data"]))

    print("\nGshare Scheme:")
    print_key_table(schemes["gshare"]["data"])
    print_alias_analysis(analyze_aliases(schemes["gshare"]["data"]))

    print("\nBranch Prediction Simulation")
    print("=" * 50)

    results = simulate_prediction(branch_patterns, "1bit")
    print_prediction_trace(results, num_to_print=20)
    print_prediction_accuracy(results)

if __name__ == "__main__":
    # Pattern where gshare performs better
    with open('gshare-better.txt', 'w') as f:
        original_stdout = sys.stdout
        sys.stdout = f
        try:
            pattern = "1101"
            print(f"Pattern where gshare performs better: {pattern}")
            print("This pattern has different predictions needed for the same history bits")
            print("Gshare can handle this by XORing with the address\n")
            run_4bit_history_analysis()
        finally:
            sys.stdout = original_stdout

    # Pattern where gshare performs worse or the same
    with open('gshare-worse.txt', 'w') as f:
        original_stdout = sys.stdout
        sys.stdout = f
        try:
            print("Pattern where gshare aliases, but concat does not")
            run_multi_branch_analysis()
        finally:
            sys.stdout = original_stdout