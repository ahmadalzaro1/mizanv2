import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


class Institution(Base):
    __tablename__ = "institutions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    users = relationship("User", back_populates="institution")
