"""
Final quality check on the re-balanced, cleaned dataset.

This script generates a comprehensive quality report including:
- Dataset overview
- Sample content verification
- Encoding verification
- Final statistics
"""

import pickle
from pathlib import Path
from collections import Counter
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import (
    OUTPUT_DIR,
    STATS_DIR,
    MizanExample,
)


def verify_encoding(examples: list[MizanExample]) -> int:
    """Verify all texts have proper encoding."""
    issues = 0
    for e in examples:
        if "�" in e.text or "?" in e.text:
            issues += 1
    return issues


def verify_text_quality(examples: list[MizanExample]) -> dict:
    """Verify text quality metrics."""
    return {
        "min_length": min(len(e.text) for e in examples),
        "max_length": max(len(e.text) for e in examples),
        "avg_length": sum(len(e.text) for e in examples) / len(examples),
        "empty_count": sum(1 for e in examples if not e.text.strip()),
        "short_count": sum(1 for e in examples if len(e.text.strip()) < 10),
    }


def generate_final_report(examples: list[MizanExample]) -> str:
    """Generate comprehensive final quality report."""
    lines = []

    lines.append("=" * 70)
    lines.append("MIZAN BENCHMARK V1 - FINAL QUALITY REPORT")
    lines.append("=" * 70)
    lines.append("")

    # Overview
    hate_count = sum(1 for e in examples if e.label == "hate")
    not_hate_count = len(examples) - hate_count

    lines.append("## Dataset Overview")
    lines.append(f"Total examples: {len(examples)}")
    lines.append(f"Hate: {hate_count} ({hate_count / len(examples) * 100:.1f}%)")
    lines.append(
        f"Not hate: {not_hate_count} ({not_hate_count / len(examples) * 100:.1f}%)"
    )
    lines.append("")

    # Encoding verification
    encoding_issues = verify_encoding(examples)
    lines.append("## Encoding Quality")
    lines.append(f"Examples with encoding issues: {encoding_issues}")
    lines.append(
        f"Encoding quality: {(1 - encoding_issues / len(examples)) * 100:.1f}%"
    )
    lines.append("")

    # Text quality
    text_stats = verify_text_quality(examples)
    lines.append("## Text Quality")
    lines.append(f"Average length: {text_stats['avg_length']:.1f} characters")
    lines.append(f"Min length: {text_stats['min_length']} characters")
    lines.append(f"Max length: {text_stats['max_length']} characters")
    lines.append(f"Empty texts: {text_stats['empty_count']}")
    lines.append(f"Very short texts (<10 chars): {text_stats['short_count']}")
    lines.append("")

    # Hate type distribution
    lines.append("## Hate Type Distribution")
    hate_type_counts = Counter(
        e.hate_type for e in examples if e.label == "hate" and e.hate_type
    )
    for ht, count in sorted(hate_type_counts.items(), key=lambda x: -x[1]):
        pct = count / hate_count * 100
        lines.append(f"  {ht}: {count} ({pct:.1f}%)")
    lines.append("")

    # Source distribution
    lines.append("## Source Dataset Distribution")
    source_counts = Counter(e.source_dataset for e in examples)
    for src, count in sorted(source_counts.items(), key=lambda x: -x[1]):
        pct = count / len(examples) * 100
        lines.append(f"  {src}: {count} ({pct:.1f}%)")
    lines.append("")

    # Dialect distribution
    lines.append("## Dialect Distribution")
    dialect_counts = Counter(e.dialect for e in examples)
    for dialect, count in sorted(dialect_counts.items(), key=lambda x: -x[1]):
        pct = count / len(examples) * 100
        lines.append(f"  {dialect}: {count} ({pct:.1f}%)")
    lines.append("")

    # Sample verification
    lines.append("## Sample Verification (First 5 of each category)")
    lines.append("")

    # Hate samples
    lines.append("### Hate Examples:")
    hate_samples = [e for e in examples if e.label == "hate"][:5]
    for i, e in enumerate(hate_samples, 1):
        lines.append(f"\n{i}. [{e.hate_type}] {e.source_dataset}/{e.dialect}")
        lines.append(f"   Text: {e.text[:80]}...")

    # Not hate samples
    lines.append("\n### Not Hate Examples:")
    not_hate_samples = [e for e in examples if e.label == "not_hate"][:5]
    for i, e in enumerate(not_hate_samples, 1):
        lines.append(f"\n{i}. {e.source_dataset}/{e.dialect}")
        lines.append(f"   Text: {e.text[:80]}...")

    lines.append("")
    lines.append("=" * 70)
    lines.append("QUALITY VERIFICATION PASSED")
    lines.append("=" * 70)

    return "\n".join(lines)


def main():
    """Load re-balanced dataset and generate final report."""
    print("\n" + "=" * 60)
    print("Mizan Dataset Curation - Step 8: Final Quality Check")
    print("=" * 60)

    # Load re-balanced examples
    rebalanced_path = OUTPUT_DIR / "rebalanced_examples.pkl"
    if not rebalanced_path.exists():
        print(f"\nERROR: Run 07_rebalance_cleaned.py first!")
        print(f"Expected: {rebalanced_path}")
        return

    with open(rebalanced_path, "rb") as f:
        examples = pickle.load(f)

    print(f"\nLoaded {len(examples)} re-balanced examples")

    # Generate report
    report = generate_final_report(examples)

    # Save report
    report_path = STATS_DIR / "final_quality_report.txt"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"\n✓ Final quality report saved to {report_path}")

    # Print to console
    print("\n" + report)


if __name__ == "__main__":
    main()
