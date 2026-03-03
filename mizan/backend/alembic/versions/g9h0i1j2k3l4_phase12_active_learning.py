"""phase12 active learning columns

Revision ID: g9h0i1j2k3l4
Revises: f8a9b0c1d2e3
Create Date: 2026-03-03

"""
from typing import Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "g9h0i1j2k3l4"
down_revision: Union[str, None] = "f8a9b0c1d2e3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Create enum type via raw SQL (project convention — avoids double-create)
    op.execute(
        "CREATE TYPE samplingstrategy AS ENUM ('sequential', 'uncertainty', 'disagreement')"
    )
    samplingstrategy = postgresql.ENUM(name="samplingstrategy", create_type=False)

    # 2. Add strategy column to training_sessions (default=sequential preserves existing rows)
    op.add_column(
        "training_sessions",
        sa.Column(
            "strategy",
            samplingstrategy,
            nullable=False,
            server_default="sequential",
        ),
    )

    # 3. Add ai_confidence to content_examples (nullable — populated by precompute script)
    op.add_column(
        "content_examples",
        sa.Column("ai_confidence", sa.Float(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("content_examples", "ai_confidence")
    op.drop_column("training_sessions", "strategy")
    op.execute("DROP TYPE IF EXISTS samplingstrategy")
