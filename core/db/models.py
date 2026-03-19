from datetime import datetime
import enum

from sqlalchemy import Column, DateTime, Enum as SAEnum, Integer, JSON, String
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


def utcnow_naive() -> datetime:
    """Store UTC timestamps without tzinfo to match the current DB schema."""
    return datetime.utcnow()


class SeverityEnum(str, enum.Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class DriftEvent(Base):
    __tablename__ = "drift_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    service = Column(String, nullable=False)
    field = Column(String, nullable=False)
    expected = Column(String)
    actual = Column(String)
    severity = Column(SAEnum(SeverityEnum), nullable=False)
    risk_score = Column(Integer, default=0)
    resolved = Column(String, default="false")
    created_at = Column(DateTime, default=utcnow_naive)


class Snapshot(Base):
    __tablename__ = "snapshots"

    id = Column(Integer, primary_key=True, autoincrement=True)
    desired = Column(JSON, nullable=False)
    actual = Column(JSON, nullable=False)
    drift_count = Column(Integer, default=0)
    risk_score = Column(Integer, default=0)
    created_at = Column(DateTime, default=utcnow_naive)
