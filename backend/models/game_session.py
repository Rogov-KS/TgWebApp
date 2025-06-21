from sqlalchemy import JSON, Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from backend.core.database import Base


class GameSession(Base):
    """Модель игровой сессии."""

    __tablename__ = "game_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    game_type = Column(String(50), nullable=False)  # "snake", "tetris", etc.
    score = Column(Integer, default=0)
    duration = Column(Integer, default=0)  # в секундах
    level = Column(Integer, default=1)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    ended_at = Column(DateTime(timezone=True), nullable=True)
    is_completed = Column(Boolean, default=False)
    game_data = Column(JSON, nullable=True)  # дополнительные данные игры

    # Связь с пользователем
    user = relationship("User", back_populates="game_sessions")

    def __repr__(self) -> str:
        return (
            f"<GameSession(id={self.id}, user_id={self.user_id}, "
            f"game_type={self.game_type}, score={self.score})>"
        )
