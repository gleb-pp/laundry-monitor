import sys
from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

import src.get_db
from src.main import app

SRC = Path(__file__).resolve().parents[1]
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


@pytest.fixture
def test_engine(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Generator[Engine, None, None]:
    """Create a temporary SQLite database."""
    db_path = tmp_path / "test.sqlite3"
    engine = create_engine(
        f"sqlite:///{db_path}",
        connect_args={"check_same_thread": False},
        echo=False,
    )
    testing_session_local = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )

    monkeypatch.setattr(src.get_db, "engine", engine)
    monkeypatch.setattr(src.get_db, "SessionLocal", testing_session_local)

    src.get_db.create_tables()
    src.get_db.create_initial_machines()

    yield engine

    engine.dispose()


@pytest.fixture
def db_session(test_engine: Engine) -> Generator[Session, None, None]:
    """Provide a database session for tests."""
    db = src.get_db.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client(test_engine: Engine) -> Generator[TestClient, None, None]:
    """Provide a TestClient for API testing."""
    with TestClient(app) as c:
        yield c
