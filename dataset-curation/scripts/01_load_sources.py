"""
Load all source datasets into pandas DataFrames.

This script loads data from:
- JHSC (Jordanian Hate Speech Corpus)
- Let-Mi (Levantine Misogyny)
- MLMA (Multilingual Multi-Aspect)
- AJ Comments (Al Jazeera)

And saves each to a pickle file for fast loading.
"""

import pandas as pd
from pathlib import Path
import pickle
from tqdm import tqdm
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))  # dataset-curation folder

from config import SOURCE_FILES, SOURCES_DIR, MIZAN_DATA_DIR


def load_jhsc() -> dict[str, pd.DataFrame]:
    """Load JHSC train and test datasets."""
    print("Loading JHSC datasets...")

    dfs = {}

    for split_name in ["jhsc_train", "jhsc_test"]:
        filepath = SOURCE_FILES[split_name]
        if filepath.exists():
            df = pd.read_csv(filepath)
            print(f"  {split_name}: {len(df)} rows")
            print(f"    Columns: {list(df.columns)}")
            dfs[split_name] = df
        else:
            print(f"  WARNING: {split_name} not found at {filepath}")

    return dfs


def load_letmi() -> pd.DataFrame:
    """Load Let-Mi dataset."""
    print("Loading Let-Mi dataset...")

    filepath = SOURCE_FILES["letmi"]
    if filepath.exists():
        df = pd.read_csv(filepath)
        print(f"  Loaded: {len(df)} rows")
        print(f"    Columns: {list(df.columns)}")
        return df
    else:
        print(f"  WARNING: Let-Mi not found at {filepath}")
        return pd.DataFrame()


def load_mlma() -> pd.DataFrame:
    """Load MLMA Arabic dataset."""
    print("Loading MLMA Arabic dataset...")

    filepath = SOURCE_FILES["mlma"]
    if filepath.exists():
        df = pd.read_csv(filepath)
        print(f"  Loaded: {len(df)} rows")
        print(f"    Columns: {list(df.columns)}")
        return df
    else:
        print(f"  WARNING: MLMA not found at {filepath}")
        return pd.DataFrame()


def load_aj_comments() -> pd.DataFrame:
    """Load AJ Comments dataset from Excel."""
    print("Loading AJ Comments dataset...")

    filepath = SOURCE_FILES["aj_comments"]
    if filepath.exists():
        df = pd.read_excel(filepath)
        print(f"  Loaded: {len(df)} rows")
        print(f"    Columns: {list(df.columns)}")
        return df
    else:
        print(f"  WARNING: AJ Comments not found at {filepath}")
        return pd.DataFrame()


def main():
    """Load all datasets and save to pickle files."""
    SOURCES_DIR.mkdir(parents=True, exist_ok=True)

    print("\n" + "=" * 60)
    print("Mizan Dataset Curation - Step 1: Load Sources")
    print("=" * 60 + "\n")

    all_data = {}

    # Load each dataset
    all_data["jhsc"] = load_jhsc()
    all_data["letmi"] = load_letmi()
    all_data["mlma"] = load_mlma()
    all_data["aj_comments"] = load_aj_comments()

    # Save to pickle
    output_path = SOURCES_DIR / "loaded_data.pkl"
    with open(output_path, "wb") as f:
        pickle.dump(all_data, f)

    print(f"\n✓ All datasets saved to {output_path}")

    # Print summary
    print("\n" + "=" * 60)
    print("Summary:")
    print("=" * 60)
    total_rows = 0
    for name, dfs in all_data.items():
        if isinstance(dfs, dict):
            for split_name, df in dfs.items():
                rows = len(df)
                total_rows += rows
                print(f"  {name}/{split_name}: {rows:,} rows")
        else:
            rows = len(dfs)
            total_rows += rows
            print(f"  {name}: {rows:,} rows")
    print(f"\n  Total: {total_rows:,} rows")


if __name__ == "__main__":
    main()
