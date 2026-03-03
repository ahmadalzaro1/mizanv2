"""phase3 training tables

Revision ID: c3d4e5f6a7b8
Revises: b1f2c3d4e5f6
Create Date: 2026-03-02
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "c3d4e5f6a7b8"
down_revision: Union[str, None] = "b1f2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create new enum types via raw SQL (project convention)
    op.execute("CREATE TYPE sessionstatus AS ENUM ('in_progress', 'completed')")
    op.execute("CREATE TYPE moderatorlabel AS ENUM ('hate', 'not_hate')")

    sessionstatus = postgresql.ENUM(name="sessionstatus", create_type=False)
    moderatorlabel = postgresql.ENUM(name="moderatorlabel", create_type=False)
    hatetype = postgresql.ENUM(name="hatetype", create_type=False)

    op.create_table(
        "training_sessions",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("institution_id", sa.UUID(), nullable=True),
        sa.Column("status", sessionstatus, nullable=False, server_default="in_progress"),
        sa.Column("total_items", sa.Integer(), nullable=False, server_default="20"),
        sa.Column("correct_count", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["institution_id"], ["institutions.id"]),
    )

    op.create_table(
        "session_items",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("session_id", sa.UUID(), nullable=False),
        sa.Column("content_example_id", sa.UUID(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("moderator_label", moderatorlabel, nullable=True),
        sa.Column("moderator_hate_type", hatetype, nullable=True),
        sa.Column("is_correct", sa.Boolean(), nullable=True),
        sa.Column("labeled_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["session_id"], ["training_sessions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["content_example_id"], ["content_examples.id"]),
    )


def downgrade() -> None:
    op.drop_table("session_items")
    op.drop_table("training_sessions")
    op.execute("DROP TYPE IF EXISTS moderatorlabel")
    op.execute("DROP TYPE IF EXISTS sessionstatus")
    # NOTE: hatetype already exists from Phase 2 — do NOT drop it here
