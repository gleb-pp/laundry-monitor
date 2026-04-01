from sqlalchemy import (
    Enum,
    Integer,
    Text,
    CheckConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column
from models.base import Base
from settings import dorm_settings
from schemas.machines import MachineType


class Machine(Base):
    """SQLAlchemy model for machines."""

    __tablename__ = "machines"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    dormitory: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    type: Mapped[MachineType] = mapped_column(
        Enum(MachineType, name="machine_type"),
        nullable=False,
        default=MachineType.WASHING
    )

    __table_args__ = (
        CheckConstraint(
            f"dormitory BETWEEN {dorm_settings.MIN_INDEX} AND {dorm_settings.MAX_INDEX}"
        ),
    )
