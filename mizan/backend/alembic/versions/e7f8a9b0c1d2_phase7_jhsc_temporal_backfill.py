"""Phase 7: JHSC temporal backfill from Snowflake IDs

Revision ID: e7f8a9b0c1d2
Revises: d4e5f6a7b8c9
Create Date: 2026-03-02
"""
from alembic import op

revision = "e7f8a9b0c1d2"
down_revision = "d4e5f6a7b8c9"
branch_labels = None
depends_on = None

TWITTER_EPOCH_MS = 1288834974657


def upgrade() -> None:
    # Backfill tweet_year and tweet_month from Twitter Snowflake IDs
    # Formula: timestamp_ms = (tweet_id >> 22) + 1288834974657
    op.execute(f"""
        UPDATE jhsc_tweets
        SET tweet_year = EXTRACT(YEAR FROM TO_TIMESTAMP(((id >> 22) + {TWITTER_EPOCH_MS}) / 1000.0))::INTEGER,
            tweet_month = EXTRACT(MONTH FROM TO_TIMESTAMP(((id >> 22) + {TWITTER_EPOCH_MS}) / 1000.0))::INTEGER
        WHERE tweet_year IS NULL
    """)

    # Add NOT NULL constraints now that all rows have values
    op.alter_column("jhsc_tweets", "tweet_year", nullable=False)
    op.alter_column("jhsc_tweets", "tweet_month", nullable=False)


def downgrade() -> None:
    op.alter_column("jhsc_tweets", "tweet_month", nullable=True)
    op.alter_column("jhsc_tweets", "tweet_year", nullable=True)
    op.execute("UPDATE jhsc_tweets SET tweet_year = NULL, tweet_month = NULL")
