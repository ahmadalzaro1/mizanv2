from datetime import datetime
from typing import Literal
from uuid import UUID
from pydantic import BaseModel, field_validator


class CreateSessionRequest(BaseModel):
    strategy: str = "sequential"  # Default preserves current behavior; invalid values silently fall back to sequential


class SubmitLabelRequest(BaseModel):
    moderator_label: Literal["hate", "not_hate"]
    moderator_hate_type: str | None = None

    @field_validator("moderator_hate_type")
    @classmethod
    def validate_hate_type(cls, v: str | None, info) -> str | None:
        if info.data.get("moderator_label") == "hate" and not v:
            raise ValueError("moderator_hate_type is required when label is hate")
        if info.data.get("moderator_label") == "not_hate" and v:
            return None  # Clear hate_type if not_hate
        return v


class ContentExampleBrief(BaseModel):
    id: UUID
    text: str
    source_dataset: str
    dialect: str | None

    model_config = {"from_attributes": True}


class SessionItemResponse(BaseModel):
    id: UUID
    position: int
    content_example: ContentExampleBrief
    moderator_label: str | None
    moderator_hate_type: str | None
    is_correct: bool | None
    ground_truth_label: str | None
    ground_truth_hate_type: str | None
    labeled_at: datetime | None

    model_config = {"from_attributes": True}


class TrainingSessionResponse(BaseModel):
    id: UUID
    status: str
    total_items: int
    labeled_count: int
    correct_count: int | None
    created_at: datetime
    completed_at: datetime | None

    model_config = {"from_attributes": True}


class TrainingSessionDetailResponse(TrainingSessionResponse):
    items: list[SessionItemResponse]
