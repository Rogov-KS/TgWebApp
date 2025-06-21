from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship

from backend.core.database import Base


class Achievement(Base):
    """Модель достижения."""

    __tablename__ = "achievements"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    icon = Column(String(255), nullable=True)  # путь к иконке
    condition_type = Column(
        String(50), nullable=False
    )  # "score", "games_played", "streak"
    condition_value = Column(Integer, nullable=False)
    points = Column(Integer, default=0)  # очки за достижение

    # Связь с достижениями пользователей
    user_achievements = relationship("UserAchievement", back_populates="achievement")

    def __repr__(self) -> str:
        return f"<Achievement(id={self.id}, name={self.name})>"
