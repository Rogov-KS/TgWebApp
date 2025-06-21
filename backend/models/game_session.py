from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from backend.core.database import Base

if TYPE_CHECKING:
    from backend.models.user import User


class GameSession(Base):
    """Модель игровой сессии."""

    __tablename__ = "game_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    game_type: Mapped[str] = mapped_column(String(50))  # "snake", "tetris", etc.
    score: Mapped[int] = mapped_column(Integer, default=0)
    duration: Mapped[int] = mapped_column(Integer, default=0)  # в секундах
    level: Mapped[int] = mapped_column(Integer, default=1)
    started_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    ended_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True))
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    game_data: Mapped[dict[str, Any] | None] = mapped_column(
        JSON
    )  # дополнительные данные игры

    # Связь с пользователем
    user: Mapped["User"] = relationship("User", back_populates="game_sessions")

    def __repr__(self) -> str:
        return (
            f"<GameSession(id={self.id}, user_id={self.user_id}, "
            f"game_type={self.game_type}, score={self.score})>"
        )
