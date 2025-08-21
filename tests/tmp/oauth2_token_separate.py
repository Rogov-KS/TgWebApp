"""
Отдельный файл с моделью OAuth2Token для демонстрации циклической зависимости.
"""

from typing import TYPE_CHECKING
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

if TYPE_CHECKING:
    from .real_cyclic_example import User


class OAuth2Token(Base):
    """Модель OAuth2 токена в отдельном файле."""

    __tablename__ = "oauth2_tokens"

    id = Column(Integer, primary_key=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    provider_name = Column(String(50), nullable=False)
    access_token = Column(String(500), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Обратная связь с User
    user = relationship("User", back_populates="oauth2_tokens")

    def __repr__(self):
        return f"<OAuth2Token(id={self.id}, user_id={self.user_id})>"
