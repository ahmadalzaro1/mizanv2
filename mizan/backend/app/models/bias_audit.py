import uuid
from datetime import datetime
from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.database import Base


class BiasAuditRun(Base):
    __tablename__ = "bias_audit_runs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    computed_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    total_examples = Column(Integer, nullable=False)
    duration_ms = Column(Integer, nullable=False)
    results = Column(JSONB, nullable=False)
