from datetime import UTC, datetime

from sqlalchemy import (
    Enum,
    Integer,
    DateTime,
    ForeignKey,
)
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base


class Report(Base):
    """SQLAlchemy model for reports."""

    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    machine_id: Mapped[int] = mapped_column(
        ForeignKey("courses.course_id", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[str] = mapped_column(
        Enum("free", "busy", "unavailable", name="machine_status"),
        nullable=False,
        default="free"
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime, nullable=True, default=datetime.now(tz=UTC),
    )
    time_remaining: Mapped[int] = mapped_column(Integer, nullable=True)
