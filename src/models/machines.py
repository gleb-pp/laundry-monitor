from sqlalchemy import (
    Enum,
    Integer,
    Text,
    CheckConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column
from src.models.base import Base
from src.settings import dorm_settings


class Machine(Base):
    """SQLAlchemy model for machines."""

    __tablename__ = "machines"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    dormitory: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    type: Mapped[str] = mapped_column(
        Enum("washing", "drying", name="machine_type"),
        nullable=False,
        default="washing"
    )

    __table_args__ = (
        CheckConstraint(
            f"dormitory BETWEEN {dorm_settings.min_dorm_number} AND {dorm_settings.max_dorm_number}"
        ),
    )
