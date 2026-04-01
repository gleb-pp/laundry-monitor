from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    """Database settings."""

    URL: str = "sqlite:///:memory:"

    model_config = SettingsConfigDict(env_prefix="DB_")


database_settings = DatabaseSettings()
