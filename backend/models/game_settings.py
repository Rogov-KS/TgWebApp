from sqlalchemy import JSON, Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from backend.core.database import Base


class GameSettings(Base):
    """Модель настроек игры пользователя."""

    __tablename__ = "game_settings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    game_type = Column(String(50), nullable=False)  # "snake", "tetris", etc.
    difficulty = Column(String(20), default="medium")  # "easy", "medium", "hard"
    theme = Column(String(20), default="dark")  # "dark", "light", "colorful"
    sound_enabled = Column(Boolean, default=True)
    vibration_enabled = Column(Boolean, default=True)
    controls = Column(JSON, nullable=True)  # настройки управления

    # Связь с пользователем
    user = relationship("User", back_populates="game_settings")

    def __repr__(self) -> str:
        return (
            f"<GameSettings(user_id={self.user_id}, "
            f"game_type={self.game_type}, difficulty={self.difficulty})>"
        )
