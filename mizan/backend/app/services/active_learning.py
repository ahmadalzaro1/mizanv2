"""Active learning sampling strategies for training session creation.

Three strategies:
  sequential   — random order, exclude already-seen examples (current behavior)
  uncertainty  — examples closest to MARBERT confidence=0.5 (hardest for model)
  disagreement — examples with highest moderator error rate across all sessions
"""
import sqlalchemy as sa
from sqlalchemy.orm import Session
from sqlalchemy import func, case

from app.models.content_example import ContentExample
from app.models.training import TrainingSession, SessionItem, SamplingStrategy


def _excluded_ids_subquery(db: Session, user_id):
    """Subquery returning content_example IDs already seen by this user in any session."""
    return (
        db.query(SessionItem.content_example_id)
        .join(TrainingSession)
        .filter(TrainingSession.user_id == user_id)
        .subquery()
    )


def select_examples_sequential(
    db: Session, user_id, limit: int = 20
) -> list[ContentExample]:
    """Current behavior: random order, excludes examples this user has already seen."""
    excluded = _excluded_ids_subquery(db, user_id)
    return (
        db.query(ContentExample)
        .filter(~ContentExample.id.in_(excluded))
        .order_by(func.random())
        .limit(limit)
        .all()
    )


def select_examples_uncertainty(
    db: Session, user_id, limit: int = 20
) -> list[ContentExample]:
    """Select examples where MARBERT confidence is closest to 0.5.

    Sorts by ABS(ai_confidence - 0.5) ascending.
    Excludes rows with NULL ai_confidence (model not yet run).
    Returns empty list if no ai_confidence scores exist at all.
    """
    excluded = _excluded_ids_subquery(db, user_id)
    return (
        db.query(ContentExample)
        .filter(
            ~ContentExample.id.in_(excluded),
            ContentExample.ai_confidence.isnot(None),
        )
        .order_by(func.abs(ContentExample.ai_confidence - 0.5).asc())
        .limit(limit)
        .all()
    )


def select_examples_disagreement(
    db: Session, user_id, limit: int = 20
) -> list[ContentExample]:
    """Select examples with highest moderator error rate across ALL sessions.

    Ranks by wrong_count/total_count descending (most errors first).
    Falls back to uncertainty sampling when no labeled history exists.

    Uses case() with .is_(False) for NULL-safe boolean counting.
    """
    excluded = _excluded_ids_subquery(db, user_id)

    # Aggregate error rate per content_example across all moderators (not just current user)
    error_subq = (
        db.query(
            SessionItem.content_example_id,
            func.count(
                case((SessionItem.is_correct.is_(False), 1))
            ).label("wrong_count"),
            func.count(SessionItem.id).label("total_count"),
        )
        .filter(SessionItem.is_correct.isnot(None))
        .group_by(SessionItem.content_example_id)
        .subquery()
    )

    results = (
        db.query(ContentExample)
        .join(error_subq, ContentExample.id == error_subq.c.content_example_id)
        .filter(~ContentExample.id.in_(excluded))
        .order_by(
            (error_subq.c.wrong_count.cast(sa.Float) / error_subq.c.total_count).desc()
        )
        .limit(limit)
        .all()
    )

    # Fallback: no labeled history -> use uncertainty sampling instead
    if not results:
        return select_examples_uncertainty(db, user_id, limit)
    return results


def select_examples(
    db: Session, user_id, strategy: SamplingStrategy, limit: int = 20
) -> list[ContentExample]:
    """Dispatch to the correct strategy function."""
    if strategy == SamplingStrategy.uncertainty:
        return select_examples_uncertainty(db, user_id, limit)
    if strategy == SamplingStrategy.disagreement:
        return select_examples_disagreement(db, user_id, limit)
    return select_examples_sequential(db, user_id, limit)
