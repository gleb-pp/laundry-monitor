from datetime import UTC, datetime

from sqlalchemy import (
    Enum,
    Integer,
    DateTime,
    ForeignKey,
)
from sqlalchemy.orm import Mapped, mapped_column
from schemas.machines import MachineReportStatus

from models.base import Base


class Report(Base):
    """SQLAlchemy model for reports."""

    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )
    machine_id: Mapped[int] = mapped_column(
        ForeignKey("machines.id", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[MachineReportStatus] = mapped_column(
        Enum(MachineReportStatus, name="machine_report_status"),
        nullable=False,
        default=MachineReportStatus.FREE
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )
    time_remaining: Mapped[int] = mapped_column(Integer, nullable=True)
