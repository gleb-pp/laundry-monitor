from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Pydantic v2 configuration
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Project root directory (automatically resolved relative to this file)
    PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent

    # Directory paths
    FRONTEND_DIR: Path = PROJECT_ROOT / "frontend"
    IMAGES_DIR: Path = FRONTEND_DIR / "images"

    # Specific image paths
    WASHER_IMAGE: Path = IMAGES_DIR / "st5.jpg"
    DRYER_IMAGE: Path = IMAGES_DIR / "st7.png"
    WASHER_CARD_IMAGE: Path = IMAGES_DIR / "st4.jpg"
    DRYER_CARD_IMAGE: Path = IMAGES_DIR / "sy1.png"

    # API configuration
    API_BASE_URL: str = "http://localhost:8000"

    TIMEOUT: int = 5


# Global settings instance (lazy initialization)
settings = Settings()
