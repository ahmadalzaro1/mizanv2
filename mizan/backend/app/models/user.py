import uuid
import enum
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


class UserRole(str, enum.Enum):
    super_admin = "super_admin"
    admin = "admin"
    moderator = "moderator"


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), nullable=False, unique=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.moderator)
    institution_id = Column(
        UUID(as_uuid=True),
        ForeignKey("institutions.id", ondelete="CASCADE"),
        nullable=True,
    )
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    institution = relationship("Institution", back_populates="users")
