from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Boolean, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.core.database import Base

if TYPE_CHECKING:
    from backend.models.game_session import GameSession
    from backend.models.game_settings import GameSettings
    from backend.models.refresh_token import RefreshToken
    from backend.models.telegram_webapp_data import TelegramWebAppData
    from backend.models.user_achievements import UserAchievement


class User(Base):
    """Модель пользователя Telegram."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    username: Mapped[str | None] = mapped_column(String(255))
    first_name: Mapped[str] = mapped_column(String(255))
    last_name: Mapped[str | None] = mapped_column(String(255))
    language_code: Mapped[str | None] = mapped_column(String(10))
    is_bot: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    max_score: Mapped[int] = mapped_column(
        Integer, default=0
    )  # Максимальное количество очков
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Связи с другими таблицами
    game_sessions: Mapped[list["GameSession"]] = relationship(
        "GameSession", back_populates="user"
    )
    user_achievements: Mapped[list["UserAchievement"]] = relationship(
        "UserAchievement", back_populates="user"
    )
    game_settings: Mapped[list["GameSettings"]] = relationship(
        "GameSettings", back_populates="user"
    )
    webapp_data: Mapped[list["TelegramWebAppData"]] = relationship(
        "TelegramWebAppData", back_populates="user"
    )
    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(
        "RefreshToken", back_populates="user"
    )

    def __repr__(self) -> str:
        return (
            f"<User(id={self.id}, telegram_id={self.telegram_id}, "
            f"username={self.username})>"
        )
