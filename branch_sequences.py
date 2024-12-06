def hash_concat(addr, history):
    """Concatenation scheme: last 2 bits of addr + last 2 bits of history"""
    return addr[-2:] + history[-2:]

def hash_gshare(addr, history):
    """Gshare scheme: XOR full addr with history"""
    addr_int = int(addr, 2)
    history_int = int(history, 2)
    return format(addr_int ^ history_int, '04b')

def generate_history_sequence(pattern, num_repeats=4):
    """Generate sequence of histories from a repeating pattern"""
    bits = list(map(int, pattern * num_repeats))
    histories = []
    for i in range(len(bits) - 4):
        curr_history = "".join(map(str, bits[i:i+4]))
        next_bit = bits[i+4] if i+4 < len(bits) else bits[0]
        histories.append({
            'history': curr_history,
            'next_bit': next_bit
        })
    return histories

def generate_branch_sequences(branch_addr, pattern, hash_function):
    """
    Generate all possible sequences for a branch address and pattern

    Args:
        branch_addr: Binary string of branch address
        pattern: Repeating pattern of branch behavior
        hash_function: Function that takes (addr, history) and returns key

    Returns: List of dictionaries containing:
        {
            'addr': branch address
            'history': 4-bit history
            'key': resulting key from hash function
            'next_bit': next bit in sequence
        }
    """
    results = []
    histories = generate_history_sequence(pattern)

    for entry in histories:
        key = hash_function(branch_addr, entry['history'])
        results.append({
            'addr': branch_addr,
            'history': entry['history'],
            'key': key,
            'next_bit': entry['next_bit']
        })

    return results

def analyze_aliases(key_data):
    """
    Analyze key data for aliasing conflicts

    Returns: Dictionary containing:
        {
            'total_keys': number of unique keys
            'keys': {
                key: {
                    'histories': list of histories mapping to this key
                    'next_bits': list of next bits for this key
                    'has_conflict': boolean indicating if next bits differ
                }
            }
        }
    """
    analysis = {'keys': {}}

    for entry in key_data:
        key = entry['key']
        if key not in analysis['keys']:
            analysis['keys'][key] = {
                'histories': [],
                'next_bits': [],
                'has_conflict': False
            }

        analysis['keys'][key]['histories'].append(entry['history'])
        analysis['keys'][key]['next_bits'].append(entry['next_bit'])

    # Calculate conflicts
    for key_info in analysis['keys'].values():
        key_info['has_conflict'] = len(set(key_info['next_bits'])) > 1

    analysis['total_keys'] = len(analysis['keys'])
    analysis['conflict_count'] = sum(1 for k in analysis['keys'].values() if k['has_conflict'])

    return analysis

def print_key_table(key_data):
    """Print formatted table of key data"""
    print("Addr  | History | Key  | Next Bit")
    print("-" * 35)
    for entry in sorted(key_data, key=lambda x: (x['addr'], x['history'])):
        print(f"{entry['addr']} | {entry['history']} | {entry['key']} | {entry['next_bit']}")

def print_alias_analysis(analysis):
    """Print formatted analysis of aliases"""
    print(f"\nTotal unique keys: {analysis['total_keys']}")
    print(f"Keys with conflicts: {analysis['conflict_count']}")

    print("\nDetailed Key Analysis:")
    for key, info in sorted(analysis['keys'].items()):
        print(f"\nKey: {key}")
        print(f"Histories: {info['histories']}")
        print(f"Next bits: {info['next_bits']}")
        if info['has_conflict']:
            print("*** Has prediction conflict ***")

if __name__ == "__main__":
    # Example usage
    branch_addr = "1010"
    pattern = "1101"

    print("Concatenation Scheme:")
    concat_data = generate_branch_sequences(branch_addr, pattern, hash_concat)
    print_key_table(concat_data)
    print_alias_analysis(analyze_aliases(concat_data))

    print("\nGshare Scheme:")
    gshare_data = generate_branch_sequences(branch_addr, pattern, hash_gshare)
    print_key_table(gshare_data)
    print_alias_analysis(analyze_aliases(gshare_data))