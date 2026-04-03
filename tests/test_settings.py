import pytest

from src.settings.db import DatabaseSettings
from src.settings.dorm import DormSettings


def test_database_settings_reads_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Check that DatabaseSettings reads the DB_URL environment variable."""
    monkeypatch.setenv("DB_URL", "sqlite:///test.db")
    settings = DatabaseSettings()
    assert settings.URL == "sqlite:///test.db"


def test_dorm_settings_reads_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Check that DormSettings reads the DORM_MIN_INDEX
    and DORM_MAX_INDEX environment variables.
    """
    monkeypatch.setenv("DORM_MIN_INDEX", "2")
    monkeypatch.setenv("DORM_MAX_INDEX", "9")
    settings = DormSettings()
    assert settings.MIN_INDEX == 2
    assert settings.MAX_INDEX == 9
