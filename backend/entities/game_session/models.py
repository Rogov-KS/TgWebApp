from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from backend.core.database import Base

if TYPE_CHECKING:
    from backend.entities.user.models import UserDB


class GameSessionDB(Base):
    """Модель игровой сессии."""

    __tablename__ = "game_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
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
    user: Mapped["UserDB"] = relationship("UserDB", back_populates="game_sessions")

    def __repr__(self) -> str:
        return (
            f"<GameSessionDB(id={self.id}, user_id={self.user_id}, "
            f"score={self.score}, duration={self.duration}, "
            f"level={self.level}, started_at={self.started_at}, "
            f"ended_at={self.ended_at}, is_completed={self.is_completed})>"
        )
