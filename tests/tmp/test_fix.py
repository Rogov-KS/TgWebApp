"""
Тест для проверки исправления циклической зависимости.
"""

import sys
import os

# Добавляем путь к проекту
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))


def test_models_import():
    """Тест импорта моделей без циклических зависимостей."""

    print("🧪 Тестирование импорта моделей...")

    try:
        # Импорт всех моделей
        from backend.entities.assemblers.models import (
            User,
            GameSession,
            RefreshToken,
            OAuth2Token
        )
        print("✅ Все модели импортированы успешно")

        # Проверка создания таблиц
        from backend.core.database import Base
        from sqlalchemy import create_engine

        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        print("✅ Таблицы созданы успешно")

        print("\n🎉 Проблема циклической зависимости решена!")
        return True

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False


if __name__ == "__main__":
    success = test_models_import()
    sys.exit(0 if success else 1)
