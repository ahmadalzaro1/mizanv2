"""
Balance the dataset to target distribution.

Target: 500 examples total (250 hate, 250 not_hate)
Hate type distribution within hate examples:
- gender: 50
- religion: 40
- race: 30
- ideology: 20
- disability: 10
- social_class: 10
- unknown: 90 (from JHSC negative, skipped in our pipeline)
"""

import pandas as pd
import pickle
import random
from pathlib import Path
from tqdm import tqdm
from collections import Counter
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))  # dataset-curation folder

from config import (
    SOURCES_DIR,
    OUTPUT_DIR,
    TARGET_TOTAL,
    TARGET_HATE_RATIO,
    HATE_TYPE_TARGETS,
    MizanExample,
)


def balance_dataset(examples: list[MizanExample]) -> list[MizanExample]:
    """
    Balance dataset to target distribution.

    Strategy:
    1. Separate hate vs not_hate
        2. Sample hate examples by hate_type (prioritize targets)
        3. Sample not_hate examples from all sources
        4. Deduplicate by text content
        5. Return balanced dataset
    """
    print("\nBalancing dataset...")

    # Separate by label
    hate_examples = [e for e in examples if e.label == "hate"]
    not_hate_examples = [e for e in examples if e.label == "not_hate"]

    print(f"  Available: {len(hate_examples)} hate, {len(not_hate_examples)} not_hate")

    # Target counts
    target_hate = int(TARGET_TOTAL * TARGET_HATE_RATIO)
    target_not_hate = TARGET_TOTAL - target_hate

    print(f"  Target: {target_hate} hate, {target_not_hate} not_hate")

    # Sample hate examples by hate_type
    balanced_hate = []

    # Group hate by type
    hate_by_type = Counter(e.hate_type for e in hate_examples if e.hate_type)
    print(f"\n  Available hate types: {dict(hate_by_type)}")

    # Sample from each hate type
    for hate_type, target_count in HATE_TYPE_TARGETS.items():
        available = [e for e in hate_examples if e.hate_type == hate_type]

        if len(available) >= target_count:
            sampled = random.sample(available, target_count)
            balanced_hate.extend(sampled)
            print(f"    {hate_type}: sampled {target_count}/{len(available)}")
        else:
            balanced_hate.extend(available)
            print(
                f"    {hate_type}: took all {len(available)} (target: {target_count})"
            )

    # Fill remaining hate quota with random hate examples
    current_hate_count = len(balanced_hate)
    remaining_hate_quota = target_hate - current_hate_count

    if remaining_hate_quota > 0:
        remaining_hate = [e for e in hate_examples if e not in balanced_hate]
        if len(remaining_hate) >= remaining_hate_quota:
            additional = random.sample(remaining_hate, remaining_hate_quota)
            balanced_hate.extend(additional)
            print(f"    (additional): sampled {remaining_hate_quota}")

    print(f"\n  Total hate sampled: {len(balanced_hate)}")

    # Sample not_hate examples
    if len(not_hate_examples) >= target_not_hate:
        balanced_not_hate = random.sample(not_hate_examples, target_not_hate)
    else:
        balanced_not_hate = not_hate_examples
        print(f"  WARNING: Only {len(not_hate_examples)} not_hate available")

    print(f"  Total not_hate sampled: {len(balanced_not_hate)}")

    # Combine and deduplicate
    all_balanced = balanced_hate + balanced_not_hate

    # Deduplicate by text content
    seen_texts = set()
    deduplicated = []

    for example in all_balanced:
        text_normalized = example.text.strip().lower()[:100]
        if text_normalized not in seen_texts:
            seen_texts.add(text_normalized)
            deduplicated.append(example)

    print(f"\n  After deduplication: {len(deduplicated)} examples")

    return deduplicated


def main():
    """Load mapped examples and balance dataset."""
    print("\n" + "=" * 60)
    print("Mizan Dataset Curation - Step 3: Balance Dataset")
    print("=" * 60)

    # Load mapped examples
    input_path = SOURCES_DIR / "mapped_examples.pkl"
    if not input_path.exists():
        print(f"\nERROR: Run 02_map_labels.py first!")
        print(f"Expected: {input_path}")
        return

    with open(input_path, "rb") as f:
        all_examples = pickle.load(f)

    print(f"\nLoaded {len(all_examples)} mapped examples")

    # Balance dataset
    balanced = balance_dataset(all_examples)

    # Save balanced dataset
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / "balanced_examples.pkl"

    with open(output_path, "wb") as f:
        pickle.dump(balanced, f)

    # Print final summary
    print("\n" + "=" * 60)
    print("Final Dataset Summary:")
    print("=" * 60)

    hate_count = sum(1 for e in balanced if e.label == "hate")
    not_hate_count = len(balanced) - hate_count

    print(f"  Total examples: {len(balanced)}")
    print(f"  Hate: {hate_count} ({hate_count / len(balanced) * 100:.1f}%)")
    print(f"  Not hate: {not_hate_count} ({not_hate_count / len(balanced) * 100:.1f}%)")

    # Hate type breakdown
    print("\n  Hate types:")
    hate_type_counts = Counter(
        e.hate_type for e in balanced if e.label == "hate" and e.hate_type
    )
    for ht, count in sorted(hate_type_counts.items(), key=lambda x: -x[1]):
        print(f"    {ht}: {count}")

    # Source breakdown
    print("\n  Sources:")
    source_counts = Counter(e.source_dataset for e in balanced)
    for src, count in sorted(source_counts.items(), key=lambda x: -x[1]):
        print(f"    {src}: {count}")

    # Dialect breakdown
    print("\n  Dialects:")
    dialect_counts = Counter(e.dialect for e in balanced)
    for dialect, count in sorted(dialect_counts.items(), key=lambda x: -x[1]):
        print(f"    {dialect}: {count}")

    print(f"\n✓ Balanced dataset saved to {output_path}")


if __name__ == "__main__":
    main()
