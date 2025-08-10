from typing import Annotated

from pydantic import field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str

    SECRET_KEY: str
    ALGORITHM: str

    # Access token настройки
    ACCESS_TOKEN_COOKIE_NAME: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    # OAuth2 настройки

    OATH_GOOGLE_WEB_CLIENT_SECRET: str
    OATH_GOOGLE_WEB_CLIENT_ID: str

    OATH_YANDEX_WEB_CLIENT_SECRET: str
    OATH_YANDEX_WEB_CLIENT_ID: str

    # Refresh token настройки
    REFRESH_TOKEN_EXPIRE_DAYS: int
    REFRESH_TOKEN_COOKIE_NAME: str
    MAX_REFRESH_TOKENS_PER_USER: int

    # CORS настройки
    CORS_ORIGINS: Annotated[list[str], NoDecode]
    CORS_ALLOW_CREDENTIALS: bool
    CORS_ALLOW_METHODS: Annotated[list[str], NoDecode]
    CORS_ALLOW_HEADERS: Annotated[list[str], NoDecode]

    # Redis настройки
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int
    REDIS_PASSWORD: str | None = None

    # Celery настройки
    CELERY_BROKER_URL: str | None = None
    CELERY_RESULT_BACKEND: str | None = None

    # SMTP настройки
    SMTP_HOST: str
    SMTP_PORT: int = 587
    SMTP_USER: str
    SMTP_PASS: str

    # Кастомный валидатор для разбиения строки в список
    @field_validator(
        "CORS_ORIGINS",
        "CORS_ALLOW_METHODS",
        "CORS_ALLOW_HEADERS",
        mode="before",
    )
    @classmethod
    def parse_env_var(cls, src_value: str) -> list[str]:
        splited_lst = src_value.lstrip("[").rstrip("]").split(",")
        return [split_value.strip().strip('"') for split_value in splited_lst]

    @property
    def DATABASE_URL(self) -> str:  # noqa
        return (
            f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    @property
    def REDIS_URL(self) -> str:  # noqa
        if self.REDIS_PASSWORD:
            return (
                f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:"
                f"{self.REDIS_PORT}/{self.REDIS_DB}"
            )
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    @property
    def CELERY_BROKER_URL_PROPERTY(self) -> str:  # noqa
        return self.CELERY_BROKER_URL or self.REDIS_URL

    @property
    def CELERY_RESULT_BACKEND_PROPERTY(self) -> str:  # noqa
        return self.CELERY_RESULT_BACKEND or self.REDIS_URL

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # Игнорирует неизвестные переменные
    )

    def get_cors_attrs(self) -> dict:
        return {
            "allow_origins": self.CORS_ORIGINS,
            "allow_credentials": self.CORS_ALLOW_CREDENTIALS,
            "allow_methods": self.CORS_ALLOW_METHODS,
            "allow_headers": self.CORS_ALLOW_HEADERS,
        }

    def get_smtp_attrs(self) -> dict:
        return {
            "host": self.SMTP_HOST,
            "port": self.SMTP_PORT,
            "user": self.SMTP_USER,
            "pass": self.SMTP_PASS,
        }


def get_settings() -> Settings:
    """Получение настроек с кэшированием"""
    return Settings()


settings = get_settings()
