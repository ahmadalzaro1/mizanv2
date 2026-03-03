"""
Map source dataset labels to Mizan schema.

Label Mapping Strategy:
- JHSC: negative -> hate (unknown type), others -> not_hate
- Let-Mi: misogyny != none -> hate (gender), others -> not_hate
- MLMA: hateful + hate (map from target), others -> not_hate
- AJ Comments: label -2 -> hate (unknown), others -> not_hate

EXCLUDE examples with unknown hate_type from final dataset.
"""

import pandas as pd
import pickle
from pathlib import Path
from tqdm import tqdm
from uuid import uuid4
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))  # dataset-curation folder

from config import (
    SOURCES_DIR,
    HATE_TYPES,
    MLMA_TARGET_MAP,
    MizanExample,
)


def map_jhsc(df_dict: dict[str, pd.DataFrame]) -> list[MizanExample]:
    """
    Map JHSC datasets to Mizan schema.

    JHSC labels:
    - negative: hate (we exclude these since hate_type is unknown)
    - neutral, positive, very positive: not_hate
    """
    print("\nMapping JHSC datasets...")

    examples = []

    for split_name, df in df_dict.items():
        print(f"  Processing {split_name}: {len(df)} rows")

        for _, row in tqdm(df.iterrows(), total=len(df)):
            label = str(row.get("Label", "")).lower().strip()

            # We SKIP negative examples (no hate_type info)
            if label == "negative":
                continue  # Skip - no fine-grained hate type

            # Map to not_hate for other labels
            mizan_label = "not_hate"

            examples.append(
                MizanExample(
                    id=f"jhsc_{row['tweet_id']}",
                    text=str(row.get("new_tweet_content", "")),
                    source_dataset="jhsc",
                    dialect="jordanian",
                    label=mizan_label,
                    hate_type=None,
                    confidence=1.0,
                    original_label=label,
                    notes=None,
                )
            )

    print(f"    Mapped: {len(examples)} not_hate examples")
    print(f"    Skipped: negative examples (no hate type)")

    return examples


def map_letmi(df: pd.DataFrame) -> list[MizanExample]:
    """
    Map Let-Mi dataset to Mizan schema.

    Let-Mi labels:
    - misogyny != none -> hate (gender)
    - misogyny == none -> not_hate
    """
    print("\nMapping Let-Mi dataset...")
    print(f"  Processing: {len(df)} rows")

    examples = []

    for _, row in tqdm(df.iterrows(), total=len(df)):
        misogyny = row.get("misogyny", "none")

        if misogyny == "none":
            # Not hate
            examples.append(
                MizanExample(
                    id=f"letmi_{uuid4().hex[:8]}",
                    text=str(row.get("text", "")),
                    source_dataset="letmi",
                    dialect="levantine",
                    label="not_hate",
                    hate_type=None,
                    confidence=1.0,
                    original_label="none",
                    notes=None,
                )
            )
        else:
            # Hate - gender type
            examples.append(
                MizanExample(
                    id=f"letmi_{uuid4().hex[:8]}",
                    text=str(row.get("text", "")),
                    source_dataset="letmi",
                    dialect="levantine",
                    label="hate",
                    hate_type="gender",
                    confidence=1.0,
                    original_label=f"misogyny: {misogyny}",
                    notes=f"Misogyny category: {misogyny}",
                )
            )

    hate_count = sum(1 for e in examples if e.label == "hate")
    print(f"    Mapped: {hate_count} hate, {len(examples) - hate_count} not_hate")

    return examples


def map_mlma(df: pd.DataFrame) -> list[MizanExample]:
    """
    Map MLMA Arabic dataset to Mizan schema.

    MLMA labels:
    - hateful -> hate (map target column to hate_type)
    - offensive, normal -> not_hate
    """
    print("\nMapping MLMA dataset...")
    print(f"  Processing: {len(df)} rows")

    examples = []

    for _, row in tqdm(df.iterrows(), total=len(df)):
        sentiment = row.get("sentiment", "").lower()
        text = str(row.get("tweet", ""))

        if sentiment == "hateful":
            # Map target to hate_type
            target = str(row.get("target", "")).lower()
            hate_type = MLMA_TARGET_MAP.get(target, None)

            # Skip if no hate_type mapping
            if hate_type is None:
                continue

            examples.append(
                MizanExample(
                    id=f"mlma_{uuid4().hex[:8]}",
                    text=text,
                    source_dataset="mlma",
                    dialect="mixed",
                    label="hate",
                    hate_type=hate_type,
                    confidence=1.0,
                    original_label=f"hateful (target: {target})",
                    notes=f"Original target: {target}",
                )
            )
        else:
            # Not hate
            examples.append(
                MizanExample(
                    id=f"mlma_{uuid4().hex[:8]}",
                    text=text,
                    source_dataset="mlma",
                    dialect="mixed",
                    label="not_hate",
                    hate_type=None,
                    confidence=1.0,
                    original_label=sentiment,
                    notes=None,
                )
            )

    hate_count = sum(1 for e in examples if e.label == "hate")
    print(f"    Mapped: {hate_count} hate, {len(examples) - hate_count} not_hate")

    return examples


def map_aj_comments(df: pd.DataFrame) -> list[MizanExample]:
    """
    Map AJ Comments dataset to Mizan schema.

    AJ Comments labels (from CrowdFlower):
    - -2: hate (we exclude these since hate_type is unknown)
    - -1, 0, 1, 2: not_hate
    """
    print("\nMapping AJ Comments dataset...")
    print(f"  Processing: {len(df)} rows")

    examples = []

    # Find the label column (may vary)
    label_col = None
    text_col = None
    for col in df.columns:
        col_lower = col.lower()
        if "label" in col_lower or "class" in col_lower:
            label_col = col
        if "text" in col_lower or "comment" in col_lower or "tweet" in col_lower:
            text_col = col

    if label_col is None or text_col is None:
        print(f"    WARNING: Could not find label/text columns")
        print(f"    Available columns: {list(df.columns)}")
        return examples

    print(f"    Using columns: label={label_col}, text={text_col}")

    for _, row in tqdm(df.iterrows(), total=len(df)):
        label = row.get(label_col)
        text = str(row.get(text_col, ""))

        # Convert label to numeric if needed
        try:
            label_num = float(label)
        except (ValueError, TypeError):
            continue

        # Skip hate examples (no hate_type info)
        if label_num == -2:
            continue

        # Map to not_hate
        examples.append(
            MizanExample(
                id=f"aj_{uuid4().hex[:8]}",
                text=text,
                source_dataset="aj_comments",
                dialect="mixed",
                label="not_hate",
                hate_type=None,
                confidence=1.0,
                original_label=str(label),
                notes=f"Original score: {label_num}",
            )
        )

    print(f"    Mapped: {len(examples)} not_hate examples")
    print(f"    Skipped: hate examples (no hate type)")

    return examples


def main():
    """Load pickled data and map all datasets."""
    print("\n" + "=" * 60)
    print("Mizan Dataset Curation - Step 2: Map Labels")
    print("=" * 60)

    # Load pickled data
    input_path = SOURCES_DIR / "loaded_data.pkl"
    if not input_path.exists():
        print(f"\nERROR: Run 01_load_sources.py first!")
        print(f"Expected: {input_path}")
        return

    with open(input_path, "rb") as f:
        all_data = pickle.load(f)

    # Map each dataset
    all_examples = []

    # JHSC
    if "jhsc" in all_data and all_data["jhsc"]:
        jhsc_examples = map_jhsc(all_data["jhsc"])
        all_examples.extend(jhsc_examples)

    # Let-Mi
    if "letmi" in all_data and not all_data["letmi"].empty:
        letmi_examples = map_letmi(all_data["letmi"])
        all_examples.extend(letmi_examples)

    # MLMA
    if "mlma" in all_data and not all_data["mlma"].empty:
        mlma_examples = map_mlma(all_data["mlma"])
        all_examples.extend(mlma_examples)

    # AJ Comments
    if "aj_comments" in all_data and not all_data["aj_comments"].empty:
        aj_examples = map_aj_comments(all_data["aj_comments"])
        all_examples.extend(aj_examples)

    # Save mapped examples
    output_path = SOURCES_DIR / "mapped_examples.pkl"
    with open(output_path, "wb") as f:
        pickle.dump(all_examples, f)

    # Print summary
    print("\n" + "=" * 60)
    print("Mapping Summary:")
    print("=" * 60)

    hate_count = sum(1 for e in all_examples if e.label == "hate")
    not_hate_count = len(all_examples) - hate_count

    print(f"  Total examples: {len(all_examples):,}")
    print(f"  Hate: {hate_count:,} ({hate_count / len(all_examples) * 100:.1f}%)")
    print(
        f"  Not hate: {not_hate_count:,} ({not_hate_count / len(all_examples) * 100:.1f}%)"
    )

    # Hate type breakdown
    print("\n  Hate types:")
    hate_type_counts = {}
    for e in all_examples:
        if e.label == "hate" and e.hate_type:
            hate_type_counts[e.hate_type] = hate_type_counts.get(e.hate_type, 0) + 1

    for ht, count in sorted(hate_type_counts.items(), key=lambda x: -x[1]):
        print(f"    {ht}: {count}")

    # Source breakdown
    print("\n  Sources:")
    source_counts = {}
    for e in all_examples:
        source_counts[e.source_dataset] = source_counts.get(e.source_dataset, 0) + 1

    for src, count in sorted(source_counts.items(), key=lambda x: -x[1]):
        print(f"    {src}: {count}")

    print(f"\n✓ Mapped examples saved to {output_path}")


if __name__ == "__main__":
    main()
