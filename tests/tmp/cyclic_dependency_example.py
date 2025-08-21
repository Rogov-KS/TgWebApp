"""
Минимальный пример, воспроизводящий ошибку циклической зависимости в SQLAlchemy.

Ошибка: sqlalchemy.exc.InvalidRequestError: When initializing mapper Mapper[User(users)],
expression 'OAuth2Token' failed to locate a name ('OAuth2Token').
If this is a class name, consider adding this relationship() to the <class 'User'> class
after both dependent classes have been defined.
"""

from typing import TYPE_CHECKING
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

# ПРОБЛЕМА: Циклическая зависимость между User и OAuth2Token
# User импортирует OAuth2Token, а OAuth2Token импортирует User

if TYPE_CHECKING:
    from .oauth2_token import OAuth2Token  # type: ignore


class User(Base):
    """Модель пользователя с циклической зависимостью."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(255), unique=True)
    email = Column(String(255), unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # ПРОБЛЕМА: Здесь SQLAlchemy не может найти OAuth2Token
    # потому что он еще не импортирован или не определен
    oauth2_tokens = relationship("OAuth2Token", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username})>"


# Файл oauth2_token.py (отдельный файл)
class OAuth2Token(Base):
    """Модель OAuth2 токена с циклической зависимостью."""

    __tablename__ = "oauth2_tokens"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    provider_name = Column(String(50), nullable=False)
    access_token = Column(String(500), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Обратная связь с User
    user = relationship("User", back_populates="oauth2_tokens")

    def __repr__(self):
        return f"<OAuth2Token(id={self.id}, user_id={self.user_id})>"


def demonstrate_error():
    """Демонстрирует ошибку циклической зависимости."""
    try:
        # Попытка создать все таблицы
        from sqlalchemy import create_engine
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        print("✅ Таблицы созданы успешно")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        print("\nЭто происходит из-за циклической зависимости между моделями.")


if __name__ == "__main__":
    demonstrate_error()
