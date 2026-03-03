"""
Generate quality check report for the curated dataset.

Reports:
- Class distribution
- Hate type distribution
- Source distribution
- Dialect distribution
- Text length statistics
- Sample content examples
"""

import pickle
from pathlib import Path
from collections import Counter
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))  # dataset-curation folder

from config import (
    OUTPUT_DIR,
    STATS_DIR,
    STATS_REPORT,
    MizanExample,
)


def generate_report(examples: list[MizanExample]) -> str:
    """Generate a comprehensive quality report."""
    report_lines = []

    report_lines.append("=" * 70)
    report_lines.append("Mizan Benchmark v1 - Quality Report")
    report_lines.append("=" * 70)
    report_lines.append("")

    # Overview
    hate_count = sum(1 for e in examples if e.label == "hate")
    not_hate_count = len(examples) - hate_count

    report_lines.append("## Overview")
    report_lines.append(f"Total examples: {len(examples)}")
    report_lines.append(f"Hate: {hate_count} ({hate_count / len(examples) * 100:.1f}%)")
    report_lines.append(
        f"Not hate: {not_hate_count} ({not_hate_count / len(examples) * 100:.1f}%)"
    )
    report_lines.append("")

    # Hate type distribution
    report_lines.append("## Hate Type Distribution")
    hate_type_counts = Counter(
        e.hate_type for e in examples if e.label == "hate" and e.hate_type
    )

    if hate_type_counts:
        for ht, count in sorted(hate_type_counts.items(), key=lambda x: -x[1]):
            pct = count / hate_count * 100
            report_lines.append(f"  {ht}: {count} ({pct:.1f}%)")
    else:
        report_lines.append("  No hate types annotated")
    report_lines.append("")

    # Source distribution
    report_lines.append("## Source Dataset Distribution")
    source_counts = Counter(e.source_dataset for e in examples)

    for src, count in sorted(source_counts.items(), key=lambda x: -x[1]):
        pct = count / len(examples) * 100
        report_lines.append(f"  {src}: {count} ({pct:.1f}%)")
    report_lines.append("")

    # Dialect distribution
    report_lines.append("## Dialect Distribution")
    dialect_counts = Counter(e.dialect for e in examples)

    for dialect, count in sorted(dialect_counts.items(), key=lambda x: -x[1]):
        pct = count / len(examples) * 100
        report_lines.append(f"  {dialect}: {count} ({pct:.1f}%)")
    report_lines.append("")

    # Text length statistics
    report_lines.append("## Text Length Statistics")
    text_lengths = [len(e.text) for e in examples]

    avg_len = sum(text_lengths) / len(text_lengths)
    min_len = min(text_lengths)
    max_len = max(text_lengths)

    report_lines.append(f"  Average length: {avg_len:.1f} characters")
    report_lines.append(f"  Min length: {min_len} characters")
    report_lines.append(f"  Max length: {max_len} characters")
    report_lines.append("")

    # Sample examples by category
    report_lines.append("## Sample Examples")
    report_lines.append("")

    # Sample hate examples
    report_lines.append("### Hate Examples (by type):")

    hate_by_type = {}
    for e in examples:
        if e.label == "hate" and e.hate_type:
            if e.hate_type not in hate_by_type:
                hate_by_type[e.hate_type] = e

    for hate_type, example in sorted(hate_by_type.items())[:5]:
        report_lines.append(f"\n**{hate_type.upper()}**:")
        report_lines.append(f"  Source: {example.source_dataset}")
        report_lines.append(f"  Text: {example.text[:100]}...")
        report_lines.append(f"  Original label: {example.original_label}")

    # Sample not_hate examples
    report_lines.append("\n### Not Hate Examples:")

    not_hate_samples = [e for e in examples if e.label == "not_hate"][:5]
    for example in not_hate_samples:
        report_lines.append(f"\n  Source: {example.source_dataset}")
        report_lines.append(f"  Text: {example.text[:100]}...")
        report_lines.append(f"  Original label: {example.original_label}")

    report_lines.append("")
    report_lines.append("=" * 70)
    report_lines.append("End of Report")
    report_lines.append("=" * 70)

    return "\n".join(report_lines)


def main():
    """Load balanced dataset and generate quality report."""
    print("\n" + "=" * 60)
    print("Mizan Dataset Curation - Step 4: Quality Check")
    print("=" * 60)

    # Load balanced examples
    input_path = OUTPUT_DIR / "balanced_examples.pkl"
    if not input_path.exists():
        print(f"\nERROR: Run 03_balance_dataset.py first!")
        print(f"Expected: {input_path}")
        return

    with open(input_path, "rb") as f:
        balanced_examples = pickle.load(f)

    print(f"\nLoaded {len(balanced_examples)} balanced examples")

    # Generate report
    report = generate_report(balanced_examples)

    # Save report
    STATS_DIR.mkdir(parents=True, exist_ok=True)

    with open(STATS_REPORT, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"\n✓ Quality report saved to {STATS_REPORT}")

    # Print report to console
    print("\n" + report)


if __name__ == "__main__":
    main()
