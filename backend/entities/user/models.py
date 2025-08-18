from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Boolean, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.core.database import Base

if TYPE_CHECKING:
    from backend.entities.game_session.models import GameSession
    from backend.ows.auth.models import OAuth2Token
    from backend.entities.refresh_token.models import RefreshToken


class User(Base):
    """Модель пользователя."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    telegram_id: Mapped[int | None] = mapped_column(
        BigInteger, unique=True, index=True, nullable=True
    )
    email: Mapped[str | None] = mapped_column(
        String(255), unique=True, index=True, nullable=True
    )
    username: Mapped[str | None] = mapped_column(
        String(255), unique=True, index=True, nullable=True
    )
    hashed_password: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
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
    oauth2_tokens: Mapped[list["OAuth2Token"]] = relationship(
        "OAuth2Token", back_populates="user"
    )
    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(
        "RefreshToken", back_populates="user"
    )

    def __repr__(self) -> str:
        return (
            f"<User(id={self.id}, username={self.username}, "
            f"email={self.email}, telegram_id={self.telegram_id})>"
        )
