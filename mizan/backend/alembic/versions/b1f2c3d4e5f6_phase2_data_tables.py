"""phase2 data tables

Revision ID: b1f2c3d4e5f6
Revises: a998e4136824
Create Date: 2026-03-02
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "b1f2c3d4e5f6"
down_revision: Union[str, None] = "a998e4136824"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create enum types via raw SQL to avoid SQLAlchemy double-creation
    op.execute("CREATE TYPE contentlabel AS ENUM ('hate', 'offensive', 'not_hate', 'spam')")
    op.execute(
        "CREATE TYPE hatetype AS ENUM ("
        "'race', 'religion', 'ideology', 'gender', 'disability', "
        "'social_class', 'tribalism', 'refugee_related', "
        "'political_affiliation', 'unknown')"
    )
    op.execute("CREATE TYPE jhsclabel AS ENUM ('negative', 'neutral', 'positive', 'very positive')")

    contentlabel = postgresql.ENUM(name="contentlabel", create_type=False)
    hatetype = postgresql.ENUM(name="hatetype", create_type=False)
    jhsclabel = postgresql.ENUM(name="jhsclabel", create_type=False)

    op.create_table(
        "content_examples",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("source_dataset", sa.String(50), nullable=False),
        sa.Column("dialect", sa.String(50), nullable=True),
        sa.Column("ground_truth_label", contentlabel, nullable=False),
        sa.Column("hate_type", hatetype, nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "jhsc_tweets",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("text", sa.Text(), nullable=True),
        sa.Column("label", jhsclabel, nullable=False),
        sa.Column("tweet_year", sa.Integer(), nullable=True),
        sa.Column("tweet_month", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index("ix_jhsc_tweets_year_month", "jhsc_tweets", ["tweet_year", "tweet_month"])
    op.create_index("ix_jhsc_tweets_label", "jhsc_tweets", ["label"])


def downgrade() -> None:
    op.drop_index("ix_jhsc_tweets_label", table_name="jhsc_tweets")
    op.drop_index("ix_jhsc_tweets_year_month", table_name="jhsc_tweets")
    op.drop_table("jhsc_tweets")
    op.drop_table("content_examples")
    sa.Enum(name="jhsclabel").drop(op.get_bind())
    sa.Enum(name="hatetype").drop(op.get_bind())
    sa.Enum(name="contentlabel").drop(op.get_bind())
