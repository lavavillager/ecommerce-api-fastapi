"""Конфигурация приложения через переменные окружения (Pydantic Settings)."""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Глобальные настройки приложения."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # Приложение
    PROJECT_NAME: str = "ecommerce-api-fastapi"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = False

    # База данных
    DATABASE_URL: str = (
        "postgresql+psycopg2://postgres:postgres@db:5432/ecommerce"
    )

    # JWT
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 часа

    # Первый администратор (создаётся при сидировании)
    FIRST_ADMIN_EMAIL: str = "admin@example.com"
    FIRST_ADMIN_PASSWORD: str = "admin12345"


@lru_cache
def get_settings() -> Settings:
    """Кэшированный доступ к настройкам."""
    return Settings()


settings = get_settings()
