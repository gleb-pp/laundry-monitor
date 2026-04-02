from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from models import Base, Machine
from schemas import MachineType
from settings import database_settings

engine = create_engine(
    database_settings.URL,
    connect_args={"check_same_thread": False},
    echo=True,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Session generator for database operations."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables() -> None:
    """Create database tables based on the defined models."""
    Base.metadata.create_all(bind=engine)


def create_initial_machines() -> None:
    """Create initial machines in the database."""
    with SessionLocal() as db:
        if db.query(Machine).count() == 0:
            machines = [
                Machine(dormitory=1,
                        name="Washer 1",
                        type=MachineType.WASHING),
                Machine(dormitory=1,
                        name="Dryer 1",
                        type=MachineType.DRYING),
                Machine(dormitory=2,
                        name="Washer 2",
                        type=MachineType.WASHING),
                Machine(dormitory=2,
                        name="Dryer 2",
                        type=MachineType.DRYING),
            ]
            db.add_all(machines)
            db.commit()
