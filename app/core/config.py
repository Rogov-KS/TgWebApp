from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Telegram Snake Web App"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"

    # CORS настройки
    ALLOWED_HOSTS: list[str] = ["http://localhost:3000", "http://localhost:5173"]

    # База данных
    DATABASE_URL: str = "postgresql://user:password@localhost/tg_snake_db"

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # Telegram Bot
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_WEBHOOK_URL: str = ""

    # JWT
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Игровые настройки
    GAME_BOARD_SIZE: int = 20
    GAME_SPEED_MS: int = 200

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
