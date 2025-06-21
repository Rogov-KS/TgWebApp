from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.core.database import Base

if TYPE_CHECKING:
    from backend.models.user import User


class GameSettings(Base):
    """Модель настроек игры пользователя."""

    __tablename__ = "game_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    game_type: Mapped[str] = mapped_column(String(50))  # "snake", "tetris", etc.
    difficulty: Mapped[str] = mapped_column(
        String(20), default="medium"
    )  # "easy", "medium", "hard"
    theme: Mapped[str] = mapped_column(
        String(20), default="dark"
    )  # "dark", "light", "colorful"
    sound_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    vibration_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    controls: Mapped[dict[str, Any] | None] = mapped_column(
        JSON
    )  # настройки управления

    # Связь с пользователем
    user: Mapped["User"] = relationship("User", back_populates="game_settings")

    def __repr__(self) -> str:
        return (
            f"<GameSettings(user_id={self.user_id}, "
            f"game_type={self.game_type}, difficulty={self.difficulty})>"
        )
