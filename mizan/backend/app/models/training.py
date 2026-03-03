import uuid
import enum
from datetime import datetime
from sqlalchemy import Column, Float, Integer, Boolean, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.content_example import HateType


class SessionStatus(str, enum.Enum):
    in_progress = "in_progress"
    completed = "completed"


class ModeratorLabel(str, enum.Enum):
    hate = "hate"
    not_hate = "not_hate"


class SamplingStrategy(str, enum.Enum):
    sequential = "sequential"
    uncertainty = "uncertainty"
    disagreement = "disagreement"


class TrainingSession(Base):
    __tablename__ = "training_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    institution_id = Column(UUID(as_uuid=True), ForeignKey("institutions.id"), nullable=True)
    status = Column(Enum(SessionStatus), default=SessionStatus.in_progress, nullable=False)
    total_items = Column(Integer, default=20, nullable=False)
    correct_count = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    strategy = Column(
        Enum(SamplingStrategy, name="samplingstrategy", create_constraint=False),
        default=SamplingStrategy.sequential,
        nullable=False,
        server_default="sequential",
    )

    user = relationship("User")
    items = relationship("SessionItem", back_populates="session", order_by="SessionItem.position")


class SessionItem(Base):
    __tablename__ = "session_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("training_sessions.id", ondelete="CASCADE"), nullable=False)
    content_example_id = Column(UUID(as_uuid=True), ForeignKey("content_examples.id"), nullable=False)
    position = Column(Integer, nullable=False)
    moderator_label = Column(Enum(ModeratorLabel), nullable=True)
    moderator_hate_type = Column(Enum(HateType), nullable=True)
    is_correct = Column(Boolean, nullable=True)
    labeled_at = Column(DateTime, nullable=True)

    # Phase 5: AI explanation
    ai_label = Column(String(20), nullable=True)
    ai_confidence = Column(Float, nullable=True)
    ai_explanation_text = Column(Text, nullable=True)
    ai_trigger_words = Column(JSONB, nullable=True)

    session = relationship("TrainingSession", back_populates="items")
    content_example = relationship("ContentExample")
