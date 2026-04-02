from datetime import UTC, datetime

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    Integer,
)
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base
from src.schemas.machines import MachineReportStatus


class Report(Base):
    """SQLAlchemy model for reports."""

    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    machine_id: Mapped[int] = mapped_column(
        ForeignKey("machines.id", ondelete="CASCADE"), nullable=False,
    )
    status: Mapped[MachineReportStatus] = mapped_column(
        Enum(MachineReportStatus, name="machine_report_status"),
        nullable=False,
        default=MachineReportStatus.FREE,
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )
    time_remaining: Mapped[int] = mapped_column(Integer, nullable=True)
