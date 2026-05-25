from functools import lru_cache
from pathlib import Path
from typing import List, Tuple, Type, Union

from pydantic import field_validator
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        **kwargs,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        class SafeDotEnvSettings:
            def __call__(self) -> dict:
                try:
                    return dotenv_settings()
                except OSError:
                    return {}

        return (init_settings, env_settings, SafeDotEnvSettings())

    # App
    APP_NAME: str = "AeroHub"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"
    ROOT_PATH: str = ""  # Set to "/cinema" in production via env var

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24h for airplane offline use

    # Database
    DATABASE_URL: str

    # CORS — accepts JSON array or comma-separated string
    CORS_ORIGINS: Union[List[str], str] = ["http://localhost:3000"]
    CORS_ALLOW_ALL: bool = False

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            import json
            try:
                return json.loads(v)
            except Exception:
                return [i.strip() for i in v.split(",")]
        return v

    # Media
    MEDIA_ROOT: Path = Path("/app/media")
    MAX_UPLOAD_SIZE_MB: int = 50

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/aerohub.log"

    # Airplane / offline
    OFFLINE_MODE: bool = True
    AIRPLANE_WIFI_SUBNET: str = "192.168.1.0/24"

    @property
    def max_upload_bytes(self) -> int:
        return self.MAX_UPLOAD_SIZE_MB * 1024 * 1024


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
