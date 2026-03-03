"""
Export the curated dataset to CSV and JSON formats.

Output formats:
1. CSV: For easy viewing and sharing
2. JSON: For programmatic use and with full metadata

Also creates a separate file ready for Mizan DB import.
"""

import pickle
import json
import csv
from pathlib import Path
from datetime import datetime
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))  # dataset-curation folder

from config import (
    OUTPUT_DIR,
    OUTPUT_CSV,
    OUTPUT_JSON,
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

    # Build JSON structure
    output = {
        "metadata": {
            "name": "Mizan Benchmark v1",
            "version": "1.0.0",
            "created_at": datetime.now().isoformat(),
            "total_examples": len(examples),
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
            "source_attribution": {
                "jhsc": "Jordanian Hate Speech Corpus (CC BY 4.0)",
                "letmi": "Let-Mi Levantine Misogyny Dataset",
                "mlma": "Multilingual Multi-Aspect Arabic Dataset",
                "aj_comments": "Al Jazeera Comments Dataset (CrowdFlower)",
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
                "notes": e.notes,
            }
            for e in examples
        ],
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)


def export_for_mizan_db(examples: list[MizanExample], output_path: Path):
    """Export in format ready for Mizan content_examples table.

    CSV columns: text, label, hate_type, dialect, source
    """
    print(f"\nExporting for Mizan DB: {output_path}")

    with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)

        # Header matching Mizan content_examples table
        writer.writerow(["text", "label", "hate_type", "dialect", "source"])

        # Data rows - map labels
        for example in examples:
            # Map hate_type None to "unknown" for DB
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
    """Load balanced dataset and export to all formats."""
    print("\n" + "=" * 60)
    print("Mizan Dataset Curation - Step 5: Export")
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

    # Export to all formats
    export_to_csv(balanced_examples, OUTPUT_CSV)
    export_to_json(balanced_examples, OUTPUT_JSON)

    # Export for Mizan DB
    mizan_db_path = OUTPUT_DIR / "mizan_content_examples.csv"
    export_for_mizan_db(balanced_examples, mizan_db_path)

    print(f"\n✓ Export complete!")
    print(f"  CSV: {OUTPUT_CSV}")
    print(f"  JSON: {OUTPUT_JSON}")
    print(f"  Mizan DB: {mizan_db_path}")


if __name__ == "__main__":
    main()
