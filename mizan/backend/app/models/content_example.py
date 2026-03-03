import uuid
import enum
from datetime import datetime
from sqlalchemy import Column, Float, String, Text, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


class ContentLabel(str, enum.Enum):
    hate = "hate"
    offensive = "offensive"
    not_hate = "not_hate"
    spam = "spam"


class HateType(str, enum.Enum):
    race = "race"
    religion = "religion"
    ideology = "ideology"
    gender = "gender"
    disability = "disability"
    social_class = "social_class"
    tribalism = "tribalism"
    refugee_related = "refugee_related"
    political_affiliation = "political_affiliation"
    unknown = "unknown"


class ContentExample(Base):
    __tablename__ = "content_examples"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    text = Column(Text, nullable=False)
    source_dataset = Column(String(50), nullable=False)
    dialect = Column(String(50), nullable=True)
    ground_truth_label = Column(
        Enum(ContentLabel, name="contentlabel", create_constraint=True),
        nullable=False,
    )
    hate_type = Column(
        Enum(HateType, name="hatetype", create_constraint=True),
        nullable=True,
    )
    ai_confidence = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
