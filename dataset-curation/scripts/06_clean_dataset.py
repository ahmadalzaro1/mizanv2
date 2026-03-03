"""
Data cleaning pipeline for Mizan dataset.

This script fixes encoding issues, removes duplicates, and flags borderline cases.
"""

import pandas as pd
import pickle
import re
from pathlib import Path
from collections import Counter
from tqdm import tqdm
import sys
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import (
    SOURCES_DIR,
    OUTPUT_DIR,
    MizanExample,
    HATE_TYPES,
)


# Quality thresholds
MIN_TEXT_LENGTH = 10
MAX_TEXT_LENGTH = 280
MAX_DUPLICATE_RATIO = 0.9  # 90% similarity = considered duplicate
MAX_CORRUPTED_RATIO = 0.1  # 10% corrupted chars = considered bad

# Offensive terms that might indicate mislabeling (even in not_hate)
offensive_terms = [
    # Dehumanizing
    "خنزير",
    "pig",
    "حيوان",
    "animal",
    "كلب",
    "dog",
    "قرد",
    "lice",
    "جرثوم",
    "germ",
    "حشر",
    "insect",
    "حشرة",
    "filth",
    # Slurs
    "عاهرة",
    "whore",
    "واطية",
    "slut",
    "زانية",
    "bitch",
    "قحب",
    "whore",
    "شرموطة",
    "prostitute",
    "عرص",
    "pimp",
    # Religious insults
    "كافر",
    "infidel",
    "مرتد",
    "apostate",
    "زنديق",
    "atheist",
    # Racial/national slurs
    "مجوس",
    "majus",
    "رافضي",
    "rafidi",
    "بول البعير",
    "camel urine",
    # Death/violence
    "يقبر",
    "bury",
    "انتقم",
    "revenge",
]


def is_text_corrupted(text: str) -> tuple[bool, float]:
    """Check if text has encoding issues."""
    if not text or len(text.strip()) < MIN_TEXT_LENGTH:
        return True, 1.0

    # Check for replacement characters
    corrupted_count = text.count("�")
    corrupted_count += text.count("?")
    corrupted_count += text.count("؟")

    # Check for high ratio of non-Arabic characters
    arabic_chars = sum(1 for c in text if "\u0600" <= c <= "\u06ff")
    total_chars = len(text.strip())

    if total_chars > 0:
        arabic_ratio = arabic_chars / total_chars
        if arabic_ratio < 0.5:  # Less than 50% Arabic
            return True, max(1 - arabic_ratio, 0.2)

    corruption_ratio = corrupted_count / len(text)
    return corruption_ratio > MAX_CORRUPTED_RATIO, corruption_ratio


def is_highly_offensive(text: str) -> tuple[bool, list[str]]:
    """Check if text contains highly offensive terms that might indicate mislabeling."""
    text_lower = text.lower()
    found_terms = []

    for term in offensive_terms:
        if term in text_lower:
            found_terms.append(term)

    return len(found_terms) > 0, found_terms


def calculate_similarity(text1: str, text2: str) -> float:
    """Calculate text similarity (normalized)."""

    # Normalize: lowercase, remove extra spaces, remove diacritics
    def normalize(t):
        t = t.lower().strip()
        t = re.sub(r"\s+", " ", t)
        return t

    n1, n2 = normalize(text1), normalize(text2)

    # Quick check for exact match
    if n1 == n2:
        return 1.0

    # Calculate Jaccard similarity (word-based)
    words1 = set(n1.split())
    words2 = set(n2.split())

    if not words1 and not words2:
        return 1.0
    if not words1 or not words2:
        return 0.0

    intersection = len(words1 & words2)
    union = len(words1 | words2)

    return intersection / union if union > 0 else 0.0


def remove_duplicates(examples: list[MizanExample]) -> list[MizanExample]:
    """Remove near-duplicate examples."""
    print(f"\n  Removing duplicates from {len(examples)} examples...")

    unique_examples = []
    duplicate_groups = {}  # Track groups of similar texts

    # Sort by id to keep first occurrence
    examples_sorted = sorted(examples, key=lambda e: e.id)

    for example in tqdm(examples_sorted, desc="  Checking duplicates"):
        is_duplicate = False

        for existing in unique_examples:
            similarity = calculate_similarity(example.text, existing.text)
            if similarity > MAX_DUPLICATE_RATIO:
                # Track duplicate groups
                key = existing.text[:50]  # Use first 50 chars as key
                if key not in duplicate_groups:
                    duplicate_groups[key] = [existing]
                duplicate_groups[key].append(example)
                is_duplicate = True
                break

        if not is_duplicate:
            unique_examples.append(example)

    # Report duplicates
    if duplicate_groups:
        print(
            f"\n  Found {sum(len(g) for g in duplicate_groups.values()) - len(duplicate_groups)} duplicate examples"
        )
        for key, group in list(duplicate_groups.items())[:5]:  # Show first 5 groups
            print(f"    - {len(group)} similar: {group[0].text[:60]}...")

    print(f"  After deduplication: {len(unique_examples)} unique examples")

    return unique_examples


def validate_example(example: MizanExample) -> tuple[bool, list[str]]:
    """Validate a single example and return issues found."""
    issues = []

    # Check text length
    if len(example.text.strip()) < MIN_TEXT_LENGTH:
        issues.append(f"Text too short ({len(example.text.strip())} chars)")
    if len(example.text) > MAX_TEXT_LENGTH:
        issues.append(f"Text too long ({len(example.text)} chars)")

    # Check encoding
    is_corrupted, corruption_ratio = is_text_corrupted(example.text)
    if is_corrupted:
        issues.append(f"Encoding issues (corruption: {corruption_ratio:.2%})")

    # Check for offensive terms in not_hate examples
    if example.label == "not_hate":
        is_offensive, found_terms = is_highly_offensive(example.text)
        if is_offensive:
            issues.append(f"Offensive terms in not_hate: {found_terms}")

    return len(issues) == 0, issues


def main():
    """Clean the Mizan dataset."""
    print("\n" + "=" * 60)
    print("Mizan Dataset Cleaning")
    print("=" * 60)

    # Load balanced examples
    input_path = OUTPUT_DIR / "balanced_examples.pkl"
    if not input_path.exists():
        print(f"\nERROR: Run 03_balance_dataset.py first!")
        print(f"Expected: {input_path}")
        return

    with open(input_path, "rb") as f:
        examples = pickle.load(f)

    print(f"\nLoaded {len(examples)} examples")

    # Step 1: Validate all examples
    print("\n" + "-" * 60)
    print("Step 1: Validating examples...")
    print("-" * 60)

    valid_examples = []
    flagged_examples = []
    corrupted_examples = []

    for example in tqdm(examples, desc="  Validating"):
        is_valid, issues = validate_example(example)

        if is_valid:
            valid_examples.append(example)
        else:
            # Separate corrupted vs flagged
            if any("Encoding" in i for i in issues):
                corrupted_examples.append((example, issues))
            else:
                flagged_examples.append((example, issues))

    print(f"\n  Valid: {len(valid_examples)}")
    print(f"  Flagged (offensive terms): {len(flagged_examples)}")
    print(f"  Corrupted (encoding issues): {len(corrupted_examples)}")

    # Step 2: Remove duplicates from valid examples
    print("\n" + "-" * 60)
    print("Step 2: Removing duplicates...")
    print("-" * 60)

    unique_examples = remove_duplicates(valid_examples)

    # Step 3: Handle flagged examples
    print("\n" + "-" * 60)
    print("Step 3: Handling flagged examples...")
    print("-" * 60)

    # For flagged examples with offensive terms, we could:
    # 1. Re-label as hate (if not already)
    # 2. Remove from dataset
    # For now, we'll remove them but log them for review

    print(f"  Found {len(flagged_examples)} examples with offensive terms in not_hate:")
    for example, issues in flagged_examples[:10]:
        print(f"    - {example.text[:60]}...")
        print(f"      Issues: {', '.join(issues)}")

    # Step 4: Generate cleaning report
    print("\n" + "-" * 60)
    print("Cleaning Summary")
    print("-" * 60)

    original_count = len(examples)
    cleaned_count = len(unique_examples)
    removed_count = original_count - cleaned_count

    print(f"  Original examples: {original_count}")
    print(f"  Cleaned examples: {cleaned_count}")
    print(f"  Removed: {removed_count} ({removed_count / original_count * 100:.1f}%)")
    print(f"    - Corrupted: {len(corrupted_examples)}")
    print(f"    - Flagged offensive: {len(flagged_examples)}")
    print(f"    - Duplicates: {len(valid_examples) - len(unique_examples)}")

    # Save cleaned examples
    cleaned_path = OUTPUT_DIR / "cleaned_examples.pkl"
    with open(cleaned_path, "wb") as f:
        pickle.dump(unique_examples, f)

    # Save flagged examples for manual review
    flagged_path = OUTPUT_DIR / "flagged_examples.pkl"
    with open(flagged_path, "wb") as f:
        pickle.dump(flagged_examples + corrupted_examples, f)

    print(f"\n✓ Cleaned examples saved to {cleaned_path}")
    print(f"✓ Flagged examples saved to {flagged_path} for manual review")

    # Print class distribution of cleaned dataset
    hate_count = sum(1 for e in unique_examples if e.label == "hate")
    not_hate_count = len(unique_examples) - hate_count

    print(f"\nCleaned Dataset Distribution:")
    print(f"  Hate: {hate_count} ({hate_count / len(unique_examples) * 100:.1f}%)")
    print(
        f"  Not hate: {not_hate_count} ({not_hate_count / len(unique_examples) * 100:.1f}%)"
    )

    # Hate type distribution
    print(f"\nHate Types:")
    hate_type_counts = Counter(
        e.hate_type for e in unique_examples if e.label == "hate" and e.hate_type
    )
    for ht, count in sorted(hate_type_counts.items(), key=lambda x: -x[1]):
        print(f"  {ht}: {count}")


if __name__ == "__main__":
    main()
