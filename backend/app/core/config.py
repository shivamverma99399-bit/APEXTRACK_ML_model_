from typing import List, Optional, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Centralized application configuration using Pydantic Settings.
    Environment variables override default values.
    """

    APP_NAME: str = "ApexTrack AI API"
    APP_DESCRIPTION: str = "Backend API for AI-powered live track condition analysis."
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"

    API_V1_PREFIX: str = "/api/v1"

    # Hugging Face / ML Model Configuration
    HF_MODEL_ID: Optional[str] = "yuvrajengines/apextrack-track-condition-v2"
    MODEL_ID: Optional[str] = ""
    MODEL_PATH: Optional[str] = ""
    HF_TOKEN: Optional[str] = None

    # Temporal Trend & History Configuration
    TREND_MIN_CONFIDENCE: float = 0.55
    MAX_HISTORY: int = 20

    # Image upload configuration
    MAX_IMAGE_SIZE_MB: int = 10
    ALLOWED_IMAGE_EXTENSIONS: List[str] = [".jpg", ".jpeg", ".png", ".webp"]
    ALLOWED_MIME_TYPES: List[str] = [
        "image/jpeg",
        "image/jpg",
        "image/png",
        "image/webp",
    ]

    # CORS configuration
    ALLOWED_ORIGINS: Union[List[str], str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "*",
    ]

    # Logging level
    LOG_LEVEL: str = "INFO"

    # Development/Testing isolated mock flag (disabled by default in production)
    ENABLE_MOCK_PREDICTOR: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_allowed_origins(cls, v: Union[List[str], str]) -> List[str]:
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    @property
    def max_image_size_bytes(self) -> int:
        return self.MAX_IMAGE_SIZE_MB * 1024 * 1024


settings = Settings()
