"""
Демонстрация ошибки циклической зависимости в SQLAlchemy.

Запустите этот скрипт, чтобы увидеть ошибку:
python tests/tmp/demonstrate_error.py
"""


def demonstrate_cyclic_dependency_error():
    """Демонстрирует ошибку циклической зависимости."""

    print("🔍 Демонстрация ошибки циклической зависимости в SQLAlchemy")
    print("=" * 60)

    try:
        # Попытка импорта моделей с циклической зависимостью
        from .user_model import User
        from .oauth2_token_model import OAuth2Token

        print("✅ Модели импортированы успешно")

        # Попытка создать таблицы
        from sqlalchemy import create_engine
        from .user_model import Base

        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        print("✅ Таблицы созданы успешно")

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        print("\n📋 Анализ проблемы:")
        print("1. User импортирует OAuth2Token")
        print("2. OAuth2Token импортирует User")
        print("3. При инициализации User SQLAlchemy не может найти OAuth2Token")
        print("4. Это происходит из-за циклической зависимости")

        print("\n💡 Решения:")
        print("1. Использовать строковые имена в relationship()")
        print("2. Импортировать модели в правильном порядке")
        print("3. Использовать lazy loading")
        print("4. Создать отдельный файл для импорта всех моделей")


def demonstrate_solution():
    """Демонстрирует правильное решение."""

    print("\n🔧 Демонстрация правильного решения")
    print("=" * 60)

    try:
        # Правильное решение: импорт всех моделей в одном месте
        from .solution_models import User, OAuth2Token, Base

        print("✅ Модели импортированы успешно")

        # Создание таблиц
        from sqlalchemy import create_engine
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        print("✅ Таблицы созданы успешно")

        print("\n🎉 Проблема решена!")

    except Exception as e:
        print(f"❌ Ошибка в решении: {e}")


if __name__ == "__main__":
    demonstrate_cyclic_dependency_error()
    demonstrate_solution()
