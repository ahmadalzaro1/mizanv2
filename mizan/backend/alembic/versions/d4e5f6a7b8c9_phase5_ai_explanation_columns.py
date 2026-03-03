"""phase5 ai explanation columns

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-03-02
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision: str = "d4e5f6a7b8c9"
down_revision: Union[str, None] = "c3d4e5f6a7b8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("session_items", sa.Column("ai_label", sa.String(20), nullable=True))
    op.add_column("session_items", sa.Column("ai_confidence", sa.Float(), nullable=True))
    op.add_column("session_items", sa.Column("ai_explanation_text", sa.Text(), nullable=True))
    op.add_column("session_items", sa.Column("ai_trigger_words", JSONB(), nullable=True))


def downgrade() -> None:
    op.drop_column("session_items", "ai_trigger_words")
    op.drop_column("session_items", "ai_explanation_text")
    op.drop_column("session_items", "ai_confidence")
    op.drop_column("session_items", "ai_label")
