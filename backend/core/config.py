import json
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
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    AUTH_COOKIE_NAME: str

    # CORS настройки
    CORS_ORIGINS: Annotated[list[str], NoDecode]
    CORS_ALLOW_CREDENTIALS: bool
    CORS_ALLOW_METHODS: Annotated[list[str], NoDecode]
    CORS_ALLOW_HEADERS: Annotated[list[str], NoDecode]

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

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        # case_sensitive=False,  # Позволяет использовать переменные в любом регистре
        extra="ignore",  # Игнорирует неизвестные переменные
    )


def get_settings() -> Settings:
    """Получение настроек с кэшированием"""
    return Settings()


settings = get_settings()
# settings = Settings()

if __name__ == "__main__":
    print(json.dumps(settings.model_dump(), indent=4))
