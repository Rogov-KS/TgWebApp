from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from backend.core.database import Base


class TelegramWebAppData(Base):
    """Модель данных Web App от Telegram."""

    __tablename__ = "telegram_webapp_data"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    init_data = Column(Text, nullable=False)  # данные инициализации
    query_id = Column(String(255), nullable=True)  # для платежей
    auth_date = Column(DateTime(timezone=True), nullable=False)
    hash = Column(String(255), nullable=False)  # для проверки подлинности

    # Связь с пользователем
    user = relationship("User", back_populates="webapp_data")

    def __repr__(self) -> str:
        return (
            f"<TelegramWebAppData(user_id={self.user_id}, "
            f"auth_date={self.auth_date})>"
        )
