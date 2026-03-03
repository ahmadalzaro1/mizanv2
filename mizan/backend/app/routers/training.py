import json
import logging
from datetime import datetime
from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy import func, update
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.content_example import ContentExample
from app.models.training import (
    TrainingSession, SessionItem, SessionStatus, ModeratorLabel, SamplingStrategy,
)
from app.models.content_example import HateType
from app.schemas.training import (
    SubmitLabelRequest, CreateSessionRequest,
)
from app.services.active_learning import select_examples

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/training", tags=["training"])


def _serialize_item(item: SessionItem) -> dict:
    """Serialize a SessionItem to response dict. Ground truth only revealed after labeling."""
    ce = item.content_example
    result = {
        "id": item.id,
        "position": item.position,
        "content_example": {
            "id": ce.id,
            "text": ce.text,
            "source_dataset": ce.source_dataset,
            "dialect": ce.dialect,
        },
        "moderator_label": item.moderator_label.value if item.moderator_label else None,
        "moderator_hate_type": item.moderator_hate_type.value if item.moderator_hate_type else None,
        "is_correct": item.is_correct,
        "labeled_at": item.labeled_at,
        # Anti-cheat: only reveal ground truth after moderator has labeled
        "ground_truth_label": None,
        "ground_truth_hate_type": None,
    }
    if item.moderator_label is not None:
        result["ground_truth_label"] = ce.ground_truth_label.value if ce.ground_truth_label else None
        result["ground_truth_hate_type"] = ce.hate_type.value if ce.hate_type else None
        # Phase 5: AI explanation
        result["ai_label"] = item.ai_label
        result["ai_confidence"] = item.ai_confidence
        result["ai_explanation_text"] = item.ai_explanation_text
        result["ai_trigger_words"] = item.ai_trigger_words
    return result


def _serialize_session(session: TrainingSession, include_items: bool = False) -> dict:
    """Serialize a TrainingSession."""
    labeled_count = sum(1 for i in session.items if i.moderator_label is not None)
    correct_count = sum(1 for i in session.items if i.is_correct is True)
    result = {
        "id": session.id,
        "status": session.status.value,
        "total_items": session.total_items,
        "labeled_count": labeled_count,
        "correct_count": correct_count,
        "created_at": session.created_at,
        "completed_at": session.completed_at,
        "strategy": session.strategy.value if session.strategy else "sequential",
    }
    if include_items:
        result["items"] = [_serialize_item(item) for item in session.items]
    return result


@router.post("/sessions", status_code=201)
def create_session(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
    request: CreateSessionRequest = Body(default_factory=CreateSessionRequest),
):
    # Parse strategy — invalid values default to sequential
    try:
        strategy = SamplingStrategy(request.strategy)
    except ValueError:
        strategy = SamplingStrategy.sequential

    examples = select_examples(db, current_user.id, strategy)

    if len(examples) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="\u0644\u0627 \u062a\u0648\u062c\u062f \u0623\u0645\u062b\u0644\u0629 \u0645\u062a\u0627\u062d\u0629",
        )

    session = TrainingSession(
        user_id=current_user.id,
        institution_id=current_user.institution_id,
        status=SessionStatus.in_progress,
        total_items=len(examples),
        strategy=strategy,
    )
    db.add(session)
    db.flush()

    for i, example in enumerate(examples, start=1):
        item = SessionItem(
            session_id=session.id,
            content_example_id=example.id,
            position=i,
        )
        db.add(item)

    db.commit()
    db.refresh(session)

    # Eagerly load items with content_examples for serialization
    session = (
        db.query(TrainingSession)
        .options(joinedload(TrainingSession.items).joinedload(SessionItem.content_example))
        .filter(TrainingSession.id == session.id)
        .first()
    )

    return _serialize_session(session, include_items=True)


@router.get("/sessions")
def list_sessions(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    sessions = (
        db.query(TrainingSession)
        .options(joinedload(TrainingSession.items))
        .filter(TrainingSession.user_id == current_user.id)
        .order_by(TrainingSession.created_at.desc())
        .all()
    )
    return {"sessions": [_serialize_session(s) for s in sessions]}


@router.get("/strategies/availability")
def get_strategy_availability(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    """Return which sampling strategies are currently available.

    uncertainty requires at least one content_example with ai_confidence set.
    disagreement requires at least one session_item with is_correct populated.
    """
    has_confidence = (
        db.query(ContentExample)
        .filter(ContentExample.ai_confidence.isnot(None))
        .first()
    ) is not None

    has_labeled_history = (
        db.query(SessionItem)
        .filter(SessionItem.is_correct.isnot(None))
        .first()
    ) is not None

    return {
        "sequential": True,
        "uncertainty": has_confidence,
        "disagreement": has_labeled_history,
    }


@router.get("/sessions/{session_id}")
def get_session(
    session_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    session = (
        db.query(TrainingSession)
        .options(joinedload(TrainingSession.items).joinedload(SessionItem.content_example))
        .filter(
            TrainingSession.id == session_id,
            TrainingSession.user_id == current_user.id,
        )
        .first()
    )
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return _serialize_session(session, include_items=True)


@router.put("/sessions/{session_id}/items/{item_id}")
def submit_label(
    session_id: UUID,
    item_id: UUID,
    request: SubmitLabelRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    # Verify session ownership
    session = (
        db.query(TrainingSession)
        .options(joinedload(TrainingSession.items).joinedload(SessionItem.content_example))
        .filter(
            TrainingSession.id == session_id,
            TrainingSession.user_id == current_user.id,
        )
        .first()
    )
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Find the item
    item = next((i for i in session.items if i.id == item_id), None)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    # Update label
    item.moderator_label = ModeratorLabel(request.moderator_label)
    if request.moderator_label == "hate" and request.moderator_hate_type:
        item.moderator_hate_type = HateType(request.moderator_hate_type)
    else:
        item.moderator_hate_type = None
    item.labeled_at = datetime.utcnow()

    # Compute is_correct using binary mapping:
    # Ground truth hate/offensive -> treated as "hate"
    # Ground truth not_hate/spam -> treated as "not_hate"
    gt = item.content_example.ground_truth_label.value
    if gt in ("hate", "offensive"):
        gt_binary = "hate"
    else:
        gt_binary = "not_hate"
    item.is_correct = (request.moderator_label == gt_binary)

    # Phase 10: AI classification (explanation generated asynchronously via SSE)
    ce = item.content_example
    try:
        from app.main import model_manager
        if model_manager is not None and model_manager.is_loaded:
            from app.core.config import settings

            ai_result = model_manager.classify_with_explanation(
                ce.text, code_mixed_threshold=settings.code_mixed_threshold
            )
            item.ai_label = ai_result["label"]
            item.ai_confidence = ai_result["confidence"]
            item.ai_trigger_words = ai_result["top_tokens"]
            # ai_explanation_text left as None — generated via SSE endpoint
    except Exception:
        logger.warning("AI classification failed", exc_info=True)

    # Check if all items are now labeled
    all_labeled = all(i.moderator_label is not None for i in session.items)
    if all_labeled:
        session.status = SessionStatus.completed
        session.completed_at = datetime.utcnow()
        session.correct_count = sum(1 for i in session.items if i.is_correct is True)

    db.commit()
    db.refresh(item)

    return _serialize_item(item)


@router.get("/sessions/{session_id}/items/{item_id}/explanation-stream")
async def stream_explanation(
    session_id: UUID,
    item_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    """Stream LLM-generated Arabic explanation for a labeled item via SSE.

    Called by frontend AFTER submit_label completes. Returns token-by-token
    SSE events. Saves accumulated explanation to DB on completion.
    """
    # Fetch item with content_example BEFORE the generator (avoid session lifetime issues)
    session = (
        db.query(TrainingSession)
        .options(joinedload(TrainingSession.items).joinedload(SessionItem.content_example))
        .filter(
            TrainingSession.id == session_id,
            TrainingSession.user_id == current_user.id,
        )
        .first()
    )
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    item = next((i for i in session.items if i.id == item_id), None)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    if item.moderator_label is None:
        raise HTTPException(status_code=400, detail="Item not yet labeled")

    # If explanation already cached, return it as a single token event
    if item.ai_explanation_text:
        async def cached_generator():
            yield f"data: {json.dumps({'token': item.ai_explanation_text, 'cached': True})}\n\n"
            yield f"data: {json.dumps({'done': True})}\n\n"
        return StreamingResponse(
            cached_generator(),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
        )

    # Extract all needed data before generator (prevent DetachedInstanceError)
    ce = item.content_example
    tweet_text = ce.text
    ai_label = item.ai_label or "not_hate"
    ai_confidence = item.ai_confidence or 0.5
    ai_top_tokens = item.ai_trigger_words or []
    hate_type = ce.hate_type.value if ce.hate_type else None
    moderator_label = item.moderator_label.value
    item_id_val = item.id

    async def event_generator():
        from app.services.llm_explanation import generate_stream

        full_text = ""
        is_fallback = False

        try:
            async for token in generate_stream(
                tweet_text=tweet_text,
                ai_label=ai_label,
                ai_confidence=ai_confidence,
                ai_top_tokens=ai_top_tokens,
                hate_type=hate_type,
                moderator_label=moderator_label,
            ):
                full_text += token
                yield f"data: {json.dumps({'token': token})}\n\n"

        except Exception as e:
            logger.warning("Explanation stream error, falling back", exc_info=True)
            from app.services.llm_explanation import generate_explanation
            fallback = generate_explanation(ai_label, ai_confidence, ai_top_tokens, hate_type)
            full_text = fallback
            is_fallback = True
            yield f"data: {json.dumps({'token': fallback, 'fallback': True})}\n\n"

        # Save accumulated text to DB (use direct SQL update to avoid session issues)
        try:
            db.execute(
                update(SessionItem)
                .where(SessionItem.id == item_id_val)
                .values(ai_explanation_text=full_text)
            )
            db.commit()
        except Exception:
            logger.warning("Failed to save explanation to DB", exc_info=True)

        yield f"data: {json.dumps({'done': True, 'fallback': is_fallback})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
    )
