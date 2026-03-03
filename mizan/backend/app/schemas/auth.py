import re
from typing import Annotated
from pydantic import BaseModel, field_validator
from uuid import UUID
from app.models.user import UserRole

# Minimal email regex: local@domain.tld — allows .local and other non-IANA TLDs
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", re.IGNORECASE)


def _validate_email(value: str) -> str:
    if not isinstance(value, str):
        raise ValueError("Email must be a string")
    value = value.strip().lower()
    if not _EMAIL_RE.match(value):
        raise ValueError("Invalid email address format")
    return value


class LoginRequest(BaseModel):
    email: str
    password: str

    @field_validator("email", mode="before")
    @classmethod
    def validate_email(cls, v: str) -> str:
        return _validate_email(v)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: UUID
    email: str
    full_name: str
    role: UserRole
    institution_id: UUID | None

    model_config = {"from_attributes": True}


class CreateModeratorRequest(BaseModel):
    email: str
    full_name: str
    password: str
    role: UserRole = UserRole.moderator
    institution_id: UUID | None = None  # required when super_admin creates a user

    @field_validator("email", mode="before")
    @classmethod
    def validate_email(cls, v: str) -> str:
        return _validate_email(v)
