from typing import TYPE_CHECKING

from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.core.database import Base

if TYPE_CHECKING:
    from backend.models.user_achievements import UserAchievement


class Achievement(Base):
    """Модель достижения."""

    __tablename__ = "achievements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    icon: Mapped[str | None] = mapped_column(String(255))  # путь к иконке
    condition_type: Mapped[str] = mapped_column(
        String(50)
    )  # "score", "games_played", "streak"
    condition_value: Mapped[int] = mapped_column(Integer)
    points: Mapped[int] = mapped_column(Integer, default=0)  # очки за достижение

    # Связь с достижениями пользователей
    user_achievements: Mapped[list["UserAchievement"]] = relationship(
        "UserAchievement", back_populates="achievement"
    )

    def __repr__(self) -> str:
        return f"<Achievement(id={self.id}, name={self.name})>"
