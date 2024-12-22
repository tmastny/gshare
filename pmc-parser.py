import sys
import xml.etree.ElementTree as ET


def parse_pmc_events(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Initialize counters
    total_mispredictions = 0
    total_branches = 0

    # Find all pmc-events elements
    for pmc_event in root.findall(".//pmc-events"):
        if not pmc_event.text:
            continue

        # Split the text into two numbers
        values = pmc_event.text.strip().split()
        if len(values) != 2:
            continue

        try:
            mispredictions = int(values[0])
            branches = int(values[1])

            # Add to running totals
            total_mispredictions += mispredictions
            total_branches += branches
        except ValueError:
            continue

    # Calculate branch prediction accuracy
    accuracy = (
        100 * (1 - (total_mispredictions / total_branches)) if total_branches > 0 else 0
    )

    return {
        "total_mispredictions": total_mispredictions,
        "total_branches": total_branches,
        "accuracy": accuracy,
    }


def main():
    file = sys.argv[1] if len(sys.argv) > 1 else "summary.xml"
    results = parse_pmc_events(file)

    print(f"Total Mispredicted Branches: {results['total_mispredictions']:,}")
    print(f"Total Branches: {results['total_branches']:,}")
    print(f"Branch Prediction Accuracy: {results['accuracy']:.2f}%")


if __name__ == "__main__":
    main()
