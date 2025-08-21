"""
Правильное решение циклической зависимости в SQLAlchemy.

Ключевые принципы:
1. Все модели используют одну и ту же Base
2. Импорт всех моделей происходит в правильном порядке
3. Используются строковые имена в relationship()
"""

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

# Общая Base для всех моделей
Base = declarative_base()


class User(Base):
    """Модель пользователя - правильное решение."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(255), unique=True)
    email = Column(String(255), unique=True)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    # ✅ Правильно: используем строковое имя
    oauth2_tokens = relationship("OAuth2Token", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username})>"


class OAuth2Token(Base):
    """Модель OAuth2 токена - правильное решение."""

    __tablename__ = "oauth2_tokens"

    id = Column(Integer, primary_key=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    provider_name = Column(String(50), nullable=False)
    access_token = Column(String(500), nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    # ✅ Правильно: используем строковое имя
    user = relationship("User", back_populates="oauth2_tokens")

    def __repr__(self):
        return f"<OAuth2Token(id={self.id}, user_id={self.user_id})>"


# ✅ Правильно: все модели определены в одном файле
# или импортированы в правильном порядке
