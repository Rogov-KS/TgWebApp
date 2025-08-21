"""
Правильный пример циклической зависимости в SQLAlchemy.

Эта ошибка возникает в реальных проектах, когда:
1. Модели находятся в разных файлах
2. Каждая модель импортирует другую в TYPE_CHECKING
3. При создании таблиц SQLAlchemy не может найти связанные модели
"""

import sys
import os
from typing import TYPE_CHECKING
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

# Создаем отдельные Base для демонстрации проблемы
Base1 = declarative_base()
Base2 = declarative_base()


# Файл 1: user_models.py
if TYPE_CHECKING:
    from .oauth2_models import OAuth2Token  # type: ignore


class User(Base1):
    """Модель пользователя в отдельном файле."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(255), unique=True)
    email = Column(String(255), unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Связь с OAuth2Token
    oauth2_tokens = relationship("OAuth2Token", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username})>"


# Файл 2: oauth2_models.py
if TYPE_CHECKING:
    from .user_models import User  # type: ignore


class OAuth2Token(Base2):
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

    # Связь с User
    user = relationship("User", back_populates="oauth2_tokens")

    def __repr__(self):
        return f"<OAuth2Token(id={self.id}, user_id={self.user_id})>"


def demonstrate_cyclic_dependency():
    """Демонстрирует циклическую зависимость."""

    print("🔍 Демонстрация циклической зависимости")
    print("=" * 60)

    try:
        # Попытка создать таблицы для User
        from sqlalchemy import create_engine
        engine = create_engine("sqlite:///:memory:")

        print("Попытка создать таблицы для User...")
        Base1.metadata.create_all(engine)
        print("✅ Таблицы User созданы успешно")

    except Exception as e:
        print(f"❌ Ошибка при создании таблиц User: {e}")
        print("\n📋 Причина ошибки:")
        print("1. User ссылается на OAuth2Token в relationship")
        print("2. OAuth2Token не импортирован в этом контексте")
        print("3. SQLAlchemy не может найти OAuth2Token при инициализации")
        print("4. Это классическая циклическая зависимость")


def demonstrate_solution():
    """Демонстрирует правильное решение."""

    print("\n🔧 Демонстрация правильного решения")
    print("=" * 60)

    try:
        # Правильное решение: общая Base и правильный порядок импорта
        from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
        from sqlalchemy.ext.declarative import declarative_base
        from sqlalchemy.orm import relationship

        Base = declarative_base()

        class User(Base):
            __tablename__ = "users"
            id = Column(Integer, primary_key=True)
            username = Column(String(255), unique=True)
            email = Column(String(255), unique=True)
            created_at = Column(DateTime(timezone=True), server_default=func.now())
            oauth2_tokens = relationship("OAuth2Token", back_populates="user")

        class OAuth2Token(Base):
            __tablename__ = "oauth2_tokens"
            id = Column(Integer, primary_key=True)
            user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
            provider_name = Column(String(50), nullable=False)
            access_token = Column(String(500), nullable=False)
            created_at = Column(DateTime(timezone=True), server_default=func.now())
            user = relationship("User", back_populates="oauth2_tokens")

        # Создание таблиц
        from sqlalchemy import create_engine
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        print("✅ Таблицы созданы успешно с правильным решением")

    except Exception as e:
        print(f"❌ Ошибка в решении: {e}")


if __name__ == "__main__":
    demonstrate_cyclic_dependency()
    demonstrate_solution()
