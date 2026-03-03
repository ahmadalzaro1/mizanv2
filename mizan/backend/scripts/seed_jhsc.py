"""Bulk load all JHSC tweets into jhsc_tweets table."""

import sys

sys.path.insert(0, "/app")

import pandas as pd
from tqdm import tqdm
from sqlalchemy import text, Table, MetaData
from sqlalchemy.dialects.postgresql import insert as pg_insert
from app.database import engine

VALID_LABELS = {"negative", "neutral", "positive", "very positive"}
CHUNK_SIZE = 10_000
FILES = [
    "/app/data/jhsc/annotated-hatetweets-4-classes_train.csv",
    "/app/data/jhsc/annotated-hatetweets-4-classes_test.csv",
]


def main():
    with engine.connect() as conn:
        count = conn.execute(text("SELECT COUNT(*) FROM jhsc_tweets")).scalar()
        if count > 0:
            print(f"Already loaded ({count} rows). Skipping.")
            return

    print("Loading JHSC tweets...")
    total_inserted = 0

    for filepath in FILES:
        print(f"  Reading {filepath.split('/')[-1]}...")
        for chunk in tqdm(
            pd.read_csv(filepath, chunksize=CHUNK_SIZE),
            desc=f"  {filepath.split('/')[-1]}",
        ):
            rows = []
            for _, r in chunk.iterrows():
                label = str(r["Label"]).strip().lower()
                # Normalize underscore variant to match enum
                if label == "very_positive":
                    label = "very positive"
                if label not in VALID_LABELS:
                    continue
                tweet_text = r.get("new_tweet_content")
                if pd.isna(tweet_text):
                    tweet_text = None
                else:
                    tweet_text = str(tweet_text)
                rows.append({
                    "id": int(r["tweet_id"]),
                    "text": tweet_text,
                    "label": label,
                    "tweet_year": None,
                    "tweet_month": None,
                })

            if rows:
                with engine.begin() as conn:
                    metadata = MetaData()
                    jhsc_table = Table("jhsc_tweets", metadata, autoload_with=conn)
                    stmt = pg_insert(jhsc_table).on_conflict_do_nothing(
                        index_elements=["id"]
                    )
                    conn.execute(stmt, rows)
                total_inserted += len(rows)

    # Print final stats
    with engine.connect() as conn:
        total = conn.execute(text("SELECT COUNT(*) FROM jhsc_tweets")).scalar()
        print(f"\nDone. {total} rows in jhsc_tweets.")
        rows = conn.execute(
            text("SELECT label, COUNT(*) as cnt FROM jhsc_tweets GROUP BY label ORDER BY label")
        ).fetchall()
        for label, cnt in rows:
            print(f"  {label}: {cnt}")


if __name__ == "__main__":
    main()
