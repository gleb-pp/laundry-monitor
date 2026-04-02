from sqlalchemy import (
    CheckConstraint,
    Enum,
    Integer,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base
from src.schemas.machines import MachineType
from src.settings import dorm_settings


class Machine(Base):
    """SQLAlchemy model for machines."""

    __tablename__ = "machines"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    dormitory: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    type: Mapped[MachineType] = mapped_column(
        Enum(MachineType, name="machine_type"),
        nullable=False,
        default=MachineType.WASHING,
    )

    __table_args__ = (
        CheckConstraint(
            f"dormitory BETWEEN {dorm_settings.MIN_INDEX} "
            f"AND {dorm_settings.MAX_INDEX}",
        ),
    )
