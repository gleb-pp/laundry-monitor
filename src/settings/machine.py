from pydantic_settings import BaseSettings, SettingsConfigDict


class MachineSettings(BaseSettings):
    """Machine settings."""

    HOURS_TO_FINISH: int = 4

    model_config = SettingsConfigDict(env_prefix="MACHINE_")


machine_settings = MachineSettings()
