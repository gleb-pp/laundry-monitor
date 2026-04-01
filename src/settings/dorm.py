from pydantic_settings import BaseSettings, SettingsConfigDict


class DormSettings(BaseSettings):
    """Dorm settings."""

    min_dorm_number: int = 1
    max_dorm_number: int = 7

    model_config = SettingsConfigDict(env_prefix="dorm_")


dorm_settings = DormSettings()
