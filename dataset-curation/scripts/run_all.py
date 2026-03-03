"""
Run all curation steps in sequence.

Usage:
    python run_all.py
"""

import subprocess
import sys
from pathlib import Path

scripts_dir = Path(__file__).parent  # Already in scripts folder

scripts = [
    ("01_load_sources.py", "Loading source datasets"),
    ("02_map_labels.py", "Mapping labels to Mizan schema"),
    ("03_balance_dataset.py", "Balancing dataset"),
    ("04_quality_check.py", "Generating quality report"),
    ("05_export.py", "Exporting to all formats"),
    ("06_clean_dataset.py", "Cleaning dataset (fix encoding, remove duplicates)"),
    ("07_rebalance_cleaned.py", "Re-balancing cleaned dataset"),
    ("08_final_quality_check.py", "Final quality check"),
    ("09_export_cleaned.py", "Exporting cleaned dataset"),
]


def run_script(script_name: str, description: str) -> bool:
    """Run a single script and return success status."""
    script_path = scripts_dir / script_name

    print(f"\n{'=' * 60}")
    print(f"Step: {description}")
    print(f"Script: {script_name}")
    print("=" * 60)

    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=scripts_dir,
            capture_output=True,
            text=True,
        )

        print(result.stdout)

        if result.returncode != 0:
            print(f"\n❌ ERROR in {script_name}:")
            print(result.stderr)
            return False

        return True
    except Exception as e:
        print(f"\n❌ Failed to run {script_name}: {e}")
        return False


def main():
    """Run all curation steps in sequence."""
    print("\n" + "=" * 60)
    print("Mizan Dataset Curation - Full Pipeline")
    print("=" * 60)

    success = True
    for script_name, description in scripts:
        if not run_script(script_name, description):
            success = False
            print(f"\n❌ Pipeline stopped at: {script_name}")
            break

    if success:
        print("\n" + "=" * 60)
        print("✓ Pipeline Complete!")
        print("=" * 60)
        print("\nOutput files:")
        print("  - output/mizan_benchmark_v1.csv")
        print("  - output/mizan_benchmark_v1.json")
        print("  - output/mizan_content_examples.csv")
        print("  - output/stats/distribution_report.txt")
    else:
        print("\n" + "=" * 60)
        print("❌ Pipeline Failed")
        print("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    main()
