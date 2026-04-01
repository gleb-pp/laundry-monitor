from settings.db import DatabaseSettings, database_settings
from settings.dorm import DormSettings, dorm_settings


def test_dorm_settings_defaults():
    assert dorm_settings.min_dorm_number == 1
    assert dorm_settings.max_dorm_number == 7


def test_dorm_settings_prefix():
    assert DormSettings.model_config.get("env_prefix") == "dorm_"


def test_database_settings_defaults():
    assert database_settings.url == "sqlite:///:memory:"


def test_database_settings_prefix():
    assert DatabaseSettings.model_config.get("env_prefix") == "db_"