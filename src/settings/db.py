from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    """Database settings."""

    url: str = "sqlite:///:memory:"

    model_config = SettingsConfigDict(env_prefix="db_")


database_settings = DatabaseSettings()
