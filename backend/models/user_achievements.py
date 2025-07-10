from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from backend.core.database import Base

if TYPE_CHECKING:
    from backend.models.achievements import Achievement
    from backend.models.user import User


class UserAchievement(Base):
    """Модель достижений пользователей."""

    __tablename__ = "user_achievements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    achievement_id: Mapped[int] = mapped_column(Integer, ForeignKey("achievements.id"))
    earned_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    is_new: Mapped[bool] = mapped_column(Boolean, default=True)  # для уведомлений

    # Связи
    user: Mapped["User"] = relationship("User", back_populates="user_achievements")
    achievement: Mapped["Achievement"] = relationship(
        "Achievement", back_populates="user_achievements"
    )

    def __repr__(self) -> str:
        return (
            f"<UserAchievement(user_id={self.user_id}, "
            f"achievement_id={self.achievement_id})>"
        )
