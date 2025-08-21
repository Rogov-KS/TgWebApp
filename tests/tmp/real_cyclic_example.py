"""
Реальный пример, воспроизводящий ошибку циклической зависимости в SQLAlchemy.

Эта ошибка возникает, когда:
1. User импортирует OAuth2Token в TYPE_CHECKING
2. OAuth2Token импортирует User в TYPE_CHECKING
3. Но при создании таблиц SQLAlchemy не может найти OAuth2Token
"""

from typing import TYPE_CHECKING
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

# ПРОБЛЕМА: Циклический импорт в TYPE_CHECKING
if TYPE_CHECKING:
    from .oauth2_token_separate import OAuth2Token


class User(Base):
    """Модель пользователя с циклической зависимостью."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(255), unique=True)
    email = Column(String(255), unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # ПРОБЛЕМА: SQLAlchemy не может найти OAuth2Token
    # потому что он определен в другом файле и еще не импортирован
    oauth2_tokens = relationship("OAuth2Token", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username})>"


def demonstrate_error():
    """Демонстрирует ошибку циклической зависимости."""
    try:
        # Попытка создать таблицы только для User
        from sqlalchemy import create_engine
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        print("✅ Таблицы созданы успешно")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        print("\nЭто происходит потому что:")
        print("1. User ссылается на OAuth2Token в relationship")
        print("2. OAuth2Token не импортирован в этом файле")
        print("3. SQLAlchemy не может найти OAuth2Token при инициализации")


if __name__ == "__main__":
    demonstrate_error()
