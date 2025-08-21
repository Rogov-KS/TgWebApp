"""
Точное воспроизведение структуры проекта и ошибки циклической зависимости.

Этот пример имитирует реальную структуру:
- entities/user/models.py
- ows/auth/models.py
- entities/assemblers/models.py
"""

import sys
import os
from typing import TYPE_CHECKING
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

# Имитируем структуру проекта
Base = declarative_base()

# entities/user/models.py
if TYPE_CHECKING:
    from .oauth2_models import OAuth2Token  # type: ignore


class User(Base):
    """Модель пользователя - точная копия из проекта."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, index=True, nullable=True)
    email = Column(String(255), unique=True, index=True, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Связи с другими таблицами
    oauth2_tokens = relationship("OAuth2Token", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username})>"


# ows/auth/models.py
if TYPE_CHECKING:
    from .user_models import User  # type: ignore


class OAuth2Token(Base):
    """Модель OAuth2 токена - точная копия из проекта."""

    __tablename__ = "oauth2_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    provider_name = Column(String(50), nullable=False)
    access_token = Column(String(500), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Связи
    user = relationship("User", back_populates="oauth2_tokens")

    def __repr__(self):
        return f"<OAuth2Token(id={self.id}, user_id={self.user_id})>"


def demonstrate_exact_error():
    """Демонстрирует точную ошибку из проекта."""

    print("🔍 Демонстрация точной ошибки из проекта")
    print("=" * 60)

    try:
        # Попытка создать таблицы
        from sqlalchemy import create_engine
        engine = create_engine("sqlite:///:memory:")

        # ПРОБЛЕМА: Здесь должна возникнуть ошибка
        Base.metadata.create_all(engine)
        print("✅ Таблицы созданы успешно")

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        print("\n📋 Анализ проблемы:")
        print("1. User и OAuth2Token определены в разных файлах")
        print("2. Оба используют TYPE_CHECKING для импорта друг друга")
        print("3. При создании таблиц SQLAlchemy не может найти OAuth2Token")
        print("4. Это происходит из-за циклической зависимости")


if __name__ == "__main__":
    demonstrate_exact_error()
