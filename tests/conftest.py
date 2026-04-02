from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"

for p in (ROOT, SRC):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import get_db
from main import app


@pytest.fixture()
def test_engine(tmp_path, monkeypatch):
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

    monkeypatch.setattr(get_db, "engine", engine)
    monkeypatch.setattr(get_db, "SessionLocal", testing_session_local)

    get_db.create_tables()
    get_db.create_initial_machines()

    yield engine

    engine.dispose()


@pytest.fixture()
def db_session(test_engine):
    db = get_db.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def client(test_engine):
    with TestClient(app) as c:
        yield c
