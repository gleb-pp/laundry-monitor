from pydantic_settings import BaseSettings, SettingsConfigDict


class DormSettings(BaseSettings):
    """Dorm settings."""

    MIN_INDEX: int = 1
    MAX_INDEX: int = 7

    model_config = SettingsConfigDict(env_prefix="DORM_")


dorm_settings = DormSettings()
