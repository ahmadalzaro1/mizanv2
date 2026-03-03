"""
Export the final cleaned, re-balanced dataset to all formats.

Output formats:
1. CSV - mizan_benchmark_v1_cleaned.csv
2. JSON - mizan_benchmark_v1_cleaned.json
3. Mizan DB format - mizan_content_examples_cleaned.csv
"""

import pickle
import json
import csv
from pathlib import Path
from datetime import datetime
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import (
    OUTPUT_DIR,
    MizanExample,
)


def export_to_csv(examples: list[MizanExample], output_path: Path):
    """Export to CSV format."""
    print(f"\nExporting to CSV: {output_path}")

    with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)

        # Header
        writer.writerow(
            [
                "id",
                "text",
                "source_dataset",
                "dialect",
                "label",
                "hate_type",
                "confidence",
                "original_label",
                "notes",
            ]
        )

        # Data rows
        for example in examples:
            writer.writerow(
                [
                    example.id,
                    example.text,
                    example.source_dataset,
                    example.dialect,
                    example.label,
                    example.hate_type or "",
                    example.confidence,
                    example.original_label,
                    example.notes or "",
                ]
            )


def export_to_json(examples: list[MizanExample], output_path: Path):
    """Export to JSON format with metadata."""
    print(f"\nExporting to JSON: {output_path}")

    output = {
        "metadata": {
            "name": "Mizan Benchmark v1 (Cleaned)",
            "version": "1.0.0-cleaned",
            "created_at": datetime.now().isoformat(),
            "total_examples": len(examples),
            "quality_notes": [
                "Encoding issues fixed",
                "Duplicates removed",
                "Borderline cases flagged",
                "Balanced 50/50 distribution",
            ],
            "schema": {
                "label": ["hate", "not_hate"],
                "hate_types": [
                    "race",
                    "religion",
                    "ideology",
                    "gender",
                    "disability",
                    "social_class",
                    "tribalism",
                    "refugee_related",
                    "political_affiliation",
                ],
                "dialects": ["jordanian", "levantine", "mixed"],
            },
        },
        "examples": [
            {
                "id": e.id,
                "text": e.text,
                "source_dataset": e.source_dataset,
                "dialect": e.dialect,
                "label": e.label,
                "hate_type": e.hate_type,
                "confidence": e.confidence,
                "original_label": e.original_label,
            }
            for e in examples
        ],
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)


def export_for_mizan_db(examples: list[MizanExample], output_path: Path):
    """Export in format ready for Mizan content_examples table."""
    print(f"\nExporting for Mizan DB: {output_path}")

    with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)

        # Header matching Mizan content_examples table
        writer.writerow(["text", "label", "hate_type", "dialect", "source"])

        for example in examples:
            hate_type_db = example.hate_type if example.hate_type else "unknown"

            writer.writerow(
                [
                    example.text,
                    example.label,
                    hate_type_db,
                    example.dialect,
                    example.source_dataset,
                ]
            )


def main():
    """Load final dataset and export to all formats."""
    print("\n" + "=" * 60)
    print("Mizan Dataset Curation - Step 9: Export Cleaned")
    print("=" * 60)

    # Load re-balanced examples
    rebalanced_path = OUTPUT_DIR / "rebalanced_examples.pkl"
    if not rebalanced_path.exists():
        print(f"\nERROR: Run 07_rebalance_cleaned.py first!")
        print(f"Expected: {rebalanced_path}")
        return

    with open(rebalanced_path, "rb") as f:
        examples = pickle.load(f)

    print(f"\nLoaded {len(examples)} final examples")

    # Export to all formats
    csv_path = OUTPUT_DIR / "mizan_benchmark_v1_cleaned.csv"
    json_path = OUTPUT_DIR / "mizan_benchmark_v1_cleaned.json"
    mizan_path = OUTPUT_DIR / "mizan_content_examples_cleaned.csv"

    export_to_csv(examples, csv_path)
    export_to_json(examples, json_path)
    export_for_mizan_db(examples, mizan_path)

    print("\n" + "=" * 60)
    print("✓ EXPORT COMPLETE!")
    print("=" * 60)
    print(f"\nOutput files:")
    print(f"  CSV: {csv_path}")
    print(f"  JSON: {json_path}")
    print(f"  Mizan DB: {mizan_path}")


if __name__ == "__main__":
    main()
