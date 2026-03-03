"""Seed content_examples with ~500 rows from 4 Arabic hate speech datasets."""

import sys
import uuid
from datetime import datetime

sys.path.insert(0, "/app")

import pandas as pd
from sqlalchemy import insert, text
from app.database import engine
from app.models.content_example import ContentExample, ContentLabel, HateType


def seed_jhsc(n=125):
    """Sample n rows from JHSC train set."""
    df = pd.read_csv("/app/data/jhsc/annotated-hatetweets-4-classes_train.csv")
    sample = df.sample(n=n, random_state=42)
    rows = []
    for _, r in sample.iterrows():
        label_raw = str(r["Label"]).strip().lower()
        if label_raw == "negative":
            gt_label = ContentLabel.hate.value
            ht = HateType.unknown.value
        else:
            gt_label = ContentLabel.not_hate.value
            ht = None
        rows.append({
            "id": uuid.uuid4(),
            "text": str(r["new_tweet_content"]),
            "source_dataset": "jhsc",
            "dialect": "jordanian",
            "ground_truth_label": gt_label,
            "hate_type": ht,
            "created_at": datetime.utcnow(),
        })
    return rows


def seed_letmi(n=125):
    """Sample n rows from Let-Mi dataset."""
    df = pd.read_csv("/app/data/let-mi/let-mi_train_part.csv")
    sample = df.sample(n=n, random_state=42)
    rows = []
    for _, r in sample.iterrows():
        misogyny = str(r["misogyny"]).strip().lower()
        if misogyny != "none":
            gt_label = ContentLabel.hate.value
            ht = HateType.gender.value
        else:
            gt_label = ContentLabel.not_hate.value
            ht = None
        rows.append({
            "id": uuid.uuid4(),
            "text": str(r["text"]),
            "source_dataset": "let_mi",
            "dialect": "levantine",
            "ground_truth_label": gt_label,
            "hate_type": ht,
            "created_at": datetime.utcnow(),
        })
    return rows


def seed_mlma(n=125):
    """Sample n rows from MLMA Arabic dataset."""
    df = pd.read_csv("/app/data/mlma/ar_dataset.csv")
    sample = df.sample(n=n, random_state=42)

    target_map = {
        "gender": HateType.gender.value,
        "religion": HateType.religion.value,
        "origin": HateType.race.value,
        "disability": HateType.disability.value,
    }

    rows = []
    for _, r in sample.iterrows():
        sentiment = str(r["sentiment"]).strip().lower()
        if "hateful" in sentiment:
            gt_label = ContentLabel.hate.value
            target_raw = str(r.get("target", "")).strip().lower()
            ht = target_map.get(target_raw, HateType.unknown.value)
        elif sentiment == "normal":
            gt_label = ContentLabel.not_hate.value
            ht = None
        elif sentiment == "offensive":
            gt_label = ContentLabel.offensive.value
            ht = None
        else:
            gt_label = ContentLabel.not_hate.value
            ht = None
        rows.append({
            "id": uuid.uuid4(),
            "text": str(r["tweet"]),
            "source_dataset": "mlma",
            "dialect": "mixed",
            "ground_truth_label": gt_label,
            "hate_type": ht,
            "created_at": datetime.utcnow(),
        })
    return rows


def seed_aj(target=125):
    """Load AJ Comments hate examples + not_hate balance."""
    df = pd.read_excel("/app/data/aj-comments/AJCommentsClassification-CF.xlsx")

    # Hate: languagecomment == -2 with confidence >= 0.75
    hate_mask = (df["languagecomment"] == -2) & (df["languagecomment:confidence"] >= 0.75)
    hate_df = df[hate_mask]

    # Not hate: languagecomment == -1
    not_hate_df = df[df["languagecomment"] == -1]

    # Take all usable hate, fill rest with not_hate
    n_hate = len(hate_df)
    n_not_hate = max(target - n_hate, 0)
    not_hate_sample = not_hate_df.sample(n=min(n_not_hate, len(not_hate_df)), random_state=42)

    rows = []
    for _, r in hate_df.iterrows():
        rows.append({
            "id": uuid.uuid4(),
            "text": str(r["body"]),
            "source_dataset": "aj_comments",
            "dialect": "mixed",
            "ground_truth_label": ContentLabel.hate.value,
            "hate_type": HateType.unknown.value,
            "created_at": datetime.utcnow(),
        })
    for _, r in not_hate_sample.iterrows():
        rows.append({
            "id": uuid.uuid4(),
            "text": str(r["body"]),
            "source_dataset": "aj_comments",
            "dialect": "mixed",
            "ground_truth_label": ContentLabel.not_hate.value,
            "hate_type": None,
            "created_at": datetime.utcnow(),
        })
    return rows


def main():
    with engine.connect() as conn:
        count = conn.execute(text("SELECT COUNT(*) FROM content_examples")).scalar()
        if count > 0:
            print(f"Already seeded ({count} rows). Skipping.")
            return

    print("Seeding content examples...")

    jhsc_rows = seed_jhsc()
    print(f"  Loaded {len(jhsc_rows)} rows from JHSC")

    letmi_rows = seed_letmi()
    print(f"  Loaded {len(letmi_rows)} rows from Let-Mi")

    mlma_rows = seed_mlma()
    print(f"  Loaded {len(mlma_rows)} rows from MLMA")

    aj_rows = seed_aj()
    print(f"  Loaded {len(aj_rows)} rows from AJ Comments")

    all_rows = jhsc_rows + letmi_rows + mlma_rows + aj_rows

    with engine.begin() as conn:
        conn.execute(insert(ContentExample), all_rows)

    print(f"Done. Seeded {len(all_rows)} content examples.")


if __name__ == "__main__":
    main()
