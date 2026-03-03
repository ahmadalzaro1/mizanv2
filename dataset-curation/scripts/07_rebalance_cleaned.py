"""
Re-balance the cleaned dataset after removing problematic examples.

This script:
1. Loads the cleaned examples
2. Creates balanced dataset (hate = not_hate)
3. Ensures diverse hate type representation
"""

import pickle
import random
from pathlib import Path
from collections import Counter
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import (
    OUTPUT_DIR,
    HATE_TYPE_TARGETS,
    MizanExample,
)


def rebalance_cleaned(examples: list[MizanExample]) -> list[MizanExample]:
    """Re-balance cleaned dataset to create 50/50 distribution."""
    print("\nRe-balancing cleaned dataset...")

    # Separate by label
    hate_examples = [e for e in examples if e.label == "hate"]
    not_hate_examples = [e for e in examples if e.label == "not_hate"]

    print(f"  Available: {len(hate_examples)} hate, {len(not_hate_examples)} not_hate")

    # Determine balance point - use minimum of hate vs not_hate
    min_count = min(len(hate_examples), len(not_hate_examples))

    print(f"  Target: {min_count} hate, {min_count} not_hate = {min_count * 2} total")

    if min_count < 50:
        print(f"\n  WARNING: Very few hate examples available ({min_count})")

    # Sample hate examples, prioritizing diverse hate types
    balanced_hate = []

    # Group hate by type
    hate_by_type = {}
    for e in hate_examples:
        if e.hate_type:
            if e.hate_type not in hate_by_type:
                hate_by_type[e.hate_type] = []
            hate_by_type[e.hate_type].append(e)

    print(
        f"\n  Available hate types: {dict(Counter(e.hate_type for e in hate_examples if e.hate_type))}"
    )

    # Sample from each hate type proportionally
    hate_type_counts = Counter(e.hate_type for e in hate_examples if e.hate_type)
    total_hate_with_type = sum(hate_type_counts.values())

    for hate_type, available in hate_by_type.items():
        # Proportional sampling based on availability
        proportion = len(available) / total_hate_with_type
        target_count = max(1, int(min_count * proportion))
        target_count = min(target_count, len(available))
        sampled = random.sample(available, target_count)
        balanced_hate.extend(sampled)
        print(f"    {hate_type}: sampled {target_count}/{len(available)}")

    # Fill remaining quota with random hate examples
    remaining_quota = min_count - len(balanced_hate)
    if remaining_quota > 0:
        remaining = [e for e in hate_examples if e not in balanced_hate]
        if len(remaining) >= remaining_quota:
            additional = random.sample(remaining, remaining_quota)
            balanced_hate.extend(additional)
            print(f"    (additional): sampled {remaining_quota}")
        elif remaining:
            balanced_hate.extend(remaining)
            print(f"    (additional): took all {len(remaining)} remaining")

    print(f"\n  Total hate sampled: {len(balanced_hate)}")

    # Sample not_hate to match
    balanced_not_hate = random.sample(not_hate_examples, len(balanced_hate))

    print(f"  Total not_hate sampled: {len(balanced_not_hate)}")

    # Combine
    all_balanced = balanced_hate + balanced_not_hate
    random.shuffle(all_balanced)

    print(f"\n  Final dataset size: {len(all_balanced)}")

    return all_balanced


def main():
    """Load cleaned examples and re-balance."""
    print("\n" + "=" * 60)
    print("Mizan Dataset Curation - Step 7: Re-balance Cleaned")
    print("=" * 60)

    # Load cleaned examples
    cleaned_path = OUTPUT_DIR / "cleaned_examples.pkl"
    if not cleaned_path.exists():
        print(f"\nERROR: Run 06_clean_dataset.py first!")
        print(f"Expected: {cleaned_path}")
        return

    with open(cleaned_path, "rb") as f:
        cleaned_examples = pickle.load(f)

    print(f"\nLoaded {len(cleaned_examples)} cleaned examples")

    # Re-balance
    rebalanced = rebalance_cleaned(cleaned_examples)

    # Save
    output_path = OUTPUT_DIR / "rebalanced_examples.pkl"
    with open(output_path, "wb") as f:
        pickle.dump(rebalanced, f)

    # Print summary
    print("\n" + "=" * 60)
    print("Re-balanced Dataset Summary:")
    print("=" * 60)

    hate_count = sum(1 for e in rebalanced if e.label == "hate")
    not_hate_count = len(rebalanced) - hate_count

    print(f"  Total examples: {len(rebalanced)}")
    print(f"  Hate: {hate_count} ({hate_count / len(rebalanced) * 100:.1f}%)")
    print(
        f"  Not hate: {not_hate_count} ({not_hate_count / len(rebalanced) * 100:.1f}%)"
    )

    # Hate type distribution
    print("\n  Hate types:")
    hate_type_counts = Counter(
        e.hate_type for e in rebalanced if e.label == "hate" and e.hate_type
    )
    for ht, count in sorted(hate_type_counts.items(), key=lambda x: -x[1]):
        print(f"    {ht}: {count}")

    # Source breakdown
    print("\n  Sources:")
    source_counts = Counter(e.source_dataset for e in rebalanced)
    for src, count in sorted(source_counts.items(), key=lambda x: -x[1]):
        print(f"    {src}: {count}")

    # Dialect breakdown
    print("\n  Dialects:")
    dialect_counts = Counter(e.dialect for e in rebalanced)
    for dialect, count in sorted(dialect_counts.items(), key=lambda x: -x[1]):
        print(f"    {dialect}: {count}")

    print(f"\n✓ Re-balanced dataset saved to {output_path}")


if __name__ == "__main__":
    main()
