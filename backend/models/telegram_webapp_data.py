from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.core.database import Base

if TYPE_CHECKING:
    from backend.models.user import User


class TelegramWebAppData(Base):
    """Модель данных Web App от Telegram."""

    __tablename__ = "telegram_webapp_data"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    init_data: Mapped[str] = mapped_column(Text)  # данные инициализации
    query_id: Mapped[str | None] = mapped_column(String(255))  # для платежей
    auth_date: Mapped[DateTime] = mapped_column(DateTime(timezone=True))
    hash: Mapped[str] = mapped_column(String(255))  # для проверки подлинности

    # Связь с пользователем
    user: Mapped["User"] = relationship("User", back_populates="webapp_data")

    def __repr__(self) -> str:
        return (
            f"<TelegramWebAppData(user_id={self.user_id}, "
            f"auth_date={self.auth_date})>"
        )
