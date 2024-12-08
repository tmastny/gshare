from branch_sequences import generate_branch_sequences, hash_concat, hash_gshare


class BranchPredictor:
    def __init__(self, hash_function, predictor_type="1bit"):
        self.hash_function = hash_function
        self.predictor_type = predictor_type
        self.prediction_table = {}  # Shared BPT

    def predict(self, addr, history):
        key = self.hash_function(addr, history)
        if self.predictor_type == "1bit":
            return self.prediction_table.get(key, 1)  # Default taken
        else:  # 2bit
            state = self.prediction_table.get(key, "11")  # Default strongly taken
            return 1 if state in ["11", "10"] else 0

    def update(self, addr, history, actual):
        key = self.hash_function(addr, history)
        if self.predictor_type == "1bit":
            self.prediction_table[key] = actual
        else:  # 2bit
            current = self.prediction_table.get(key, "11")
            if actual == 1 and current != "11":
                self.prediction_table[key] = format(int(current, 2) + 1, "02b")
            elif actual == 0 and current != "00":
                self.prediction_table[key] = format(int(current, 2) - 1, "02b")


def simulate_prediction(branch_patterns, predictor_type="1bit"):
    """
    Simulates branch prediction using pre-calculated sequences

    Args:
        branch_patterns: Dict mapping branch addresses to their patterns
        predictor_type: "1bit" or "2bit"
    """
    # Generate all possible sequences for each branch
    concat_sequences = {}
    gshare_sequences = {}

    for addr, pattern in branch_patterns.items():
        concat_sequences[addr] = generate_branch_sequences(addr, pattern, hash_concat)
        gshare_sequences[addr] = generate_branch_sequences(addr, pattern, hash_gshare)

    # Create predictors
    concat_pred = BranchPredictor(hash_concat, predictor_type)
    gshare_pred = BranchPredictor(hash_gshare, predictor_type)

    results = {
        "branch_patterns": branch_patterns,
        "predictor_type": predictor_type,
        "num_branches": 0,
        "concat_results": [],
        "gshare_results": [],
    }

    # Simulate predictions using interleaved sequences
    for i in range(100):  # Simulate 100 branches
        for addr in branch_patterns:
            # Get current entry from each sequence
            concat_entry = concat_sequences[addr][i % len(concat_sequences[addr])]
            gshare_entry = gshare_sequences[addr][i % len(gshare_sequences[addr])]

            # Make predictions
            concat_prediction = concat_pred.predict(
                concat_entry["addr"], concat_entry["history"]
            )
            gshare_prediction = gshare_pred.predict(
                gshare_entry["addr"], gshare_entry["history"]
            )

            # Update predictors
            concat_pred.update(
                concat_entry["addr"], concat_entry["history"], concat_entry["next_bit"]
            )
            gshare_pred.update(
                gshare_entry["addr"], gshare_entry["history"], gshare_entry["next_bit"]
            )

            # Store results
            results["concat_results"].append(
                {
                    "branch_addr": concat_entry["addr"],
                    "history": concat_entry["history"],
                    "prediction": concat_prediction,
                    "key": concat_entry["key"],
                    "actual": concat_entry["next_bit"],
                }
            )

            results["gshare_results"].append(
                {
                    "branch_addr": gshare_entry["addr"],
                    "history": gshare_entry["history"],
                    "prediction": gshare_prediction,
                    "key": gshare_entry["key"],
                    "actual": gshare_entry["next_bit"],
                }
            )

            results["num_branches"] += 1

    return results


def print_prediction_trace(results, num_to_print=10):
    """Print the step-by-step prediction trace showing how predictions evolved"""
    print(f"\nPrediction Trace (first {num_to_print} branches):")
    print("Branch Addr | History | Actual | Scheme  | Key  | Prediction")
    print("-" * 65)

    for i in range(min(num_to_print, results["num_branches"])):
        concat = results["concat_results"][i]
        gshare = results["gshare_results"][i]

        # Print first line with branch info and concat results
        print(
            f"{concat['branch_addr']:10} | {concat['history']:7} | "
            f"{concat['actual']:6} | Concat  | {concat['key']:4} | {concat['prediction']:9}"
        )

        # Print second line with just gshare scheme info
        print(
            f"{'':10} | {'':7} | {'':6} | Gshare  | {gshare['key']:4} | {gshare['prediction']:9}"
        )

        if i < num_to_print - 1:
            print("-" * 65)


def print_prediction_accuracy(results):
    """Print accuracy statistics for both prediction schemes"""
    print("\nPrediction Accuracy:")
    print("-" * 50)

    for scheme in ["concat", "gshare"]:
        scheme_results = results[f"{scheme}_results"]
        correct = sum(1 for r in scheme_results if r["prediction"] == r["actual"])
        total = len(scheme_results)
        accuracy = correct / total if total > 0 else 0

        print(f"\n{scheme.capitalize()} Scheme:")
        print(f"Total predictions: {total}")
        print(f"Correct predictions: {correct}")
        print(f"Accuracy: {accuracy:.2%}")


if __name__ == "__main__":
    # Example usage
    branch_patterns = {
        "1010": "1101",  # Branch A
        "1100": "1010",  # Branch B
    }

    print("Running 1-bit predictor simulation:")
    results_1bit = simulate_prediction(branch_patterns, "1bit")
    print_prediction_trace(results_1bit, num_to_print=5)
    print_prediction_accuracy(results_1bit)

    print("\nRunning 2-bit predictor simulation:")
    results_2bit = simulate_prediction(branch_patterns, "2bit")
    print_prediction_trace(results_2bit, num_to_print=5)
    print_prediction_accuracy(results_2bit)
