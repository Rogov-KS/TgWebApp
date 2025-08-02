#!/usr/bin/env python3
"""
Упрощенный тест валидации Telegram initData без зависимости от настроек.
"""

import hashlib
import hmac
import json
import time
import urllib.parse


def create_telegram_hash(data_string: str, bot_token: str) -> str:
    """Создает HMAC-SHA256 хеш для проверки подлинности данных Telegram."""
    secret_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()

    return hmac.new(secret_key, data_string.encode(), hashlib.sha256).hexdigest()


def validate_telegram_init_data(init_data: str, bot_token: str) -> dict:
    """Валидирует initData от Telegram Web App."""

    # Разбор initData на параметры
    parsed_data = urllib.parse.parse_qs(init_data)

    # Извлечение обязательных параметров
    auth_date_str = parsed_data.get("auth_date", [None])[0]
    hash_value = parsed_data.get("hash", [None])[0]

    if not auth_date_str or not hash_value:
        raise ValueError("Missing required parameters")

    # Проверка времени авторизации (24 часа)
    auth_date = int(auth_date_str)
    current_time = int(time.time())
    if current_time - auth_date > 86400:
        raise ValueError("Authentication expired")

    # Создание строки для хеширования (без hash параметра)
    data_check_string = []
    for key, value in parsed_data.items():
        if key != "hash":
            data_check_string.append(f"{key}={value[0]}")

    # Сортировка параметров по алфавиту
    data_check_string.sort()
    data_check_string_str = "\n".join(data_check_string)

    # Проверка HMAC-SHA256 подписи
    expected_hash = create_telegram_hash(data_check_string_str, bot_token)
    if not hmac.compare_digest(hash_value, expected_hash):
        raise ValueError("Invalid hash signature")

    # Извлечение данных пользователя
    user_data_str = parsed_data.get("user", [None])[0]
    if not user_data_str:
        raise ValueError("User data not found")

    try:
        user_data = json.loads(user_data_str)
    except json.JSONDecodeError:
        raise ValueError("Invalid user data JSON")

    return {
        "user": user_data,
        "auth_date": auth_date,
        "hash": hash_value,
    }


def create_valid_init_data(user_data: dict, bot_token: str = "test_bot_token") -> str:
    """Создает валидный initData с правильным хешем."""

    # Кодируем данные пользователя
    user_json = json.dumps(user_data, separators=(",", ":"))
    user_encoded = urllib.parse.quote(user_json)

    # Создаем auth_date (текущее время)
    auth_date = int(time.time())

    # Создаем строку для хеширования
    data_string = f"auth_date={auth_date}\nuser={user_encoded}"

    # Создаем хеш
    hash_value = create_telegram_hash(data_string, bot_token)

    # Формируем initData
    init_data = f"user={user_encoded}&auth_date={auth_date}&hash={hash_value}"

    return init_data


def test_validation():
    """Тестирует валидацию initData."""

    print("🧪 Тестирование валидации Telegram initData")
    print("=" * 50)

    bot_token = "test_bot_token"

    # Тестовые данные пользователей
    test_users = [
        {
            "id": 123456789,
            "first_name": "John",
            "last_name": "Doe",
            "username": "johndoe",
            "language_code": "en",
            "is_premium": True,
            "photo_url": "https://t.me/i/userpic/320/johndoe.jpg",
        },
        {
            "id": 987654321,
            "first_name": "Alice",
            "last_name": "Smith",
            "username": "alicesmith",
            "language_code": "ru",
            "is_premium": False,
            "photo_url": None,
        },
        {
            "id": 555666777,
            "first_name": "Иван",
            "last_name": "Петров",
            "username": "ivanpetrov",
            "language_code": "ru",
            "is_premium": True,
            "photo_url": None,
        },
    ]

    # Тест 1: Валидные данные
    print("\n✅ Тест 1: Валидные данные")
    for i, user_data in enumerate(test_users, 1):
        try:
            init_data = create_valid_init_data(user_data, bot_token)
            result = validate_telegram_init_data(init_data, bot_token)
            print(f"   Пользователь {i}: ✅ Успешно валидирован")
            print(f"      ID: {result['user']['id']}")
            print(f"      Имя: {result['user']['first_name']}")
            print(f"      Премиум: {result['user']['is_premium']}")
        except Exception as e:
            print(f"   Пользователь {i}: ❌ Ошибка валидации: {e}")

    # Тест 2: Невалидный хеш
    print("\n❌ Тест 2: Невалидный хеш")
    try:
        invalid_data = "user=%7B%22id%22%3A123456789%2C%22first_name%22%3A%22John%22%7D&auth_date=1640995200&hash=invalid_hash"
        validate_telegram_init_data(invalid_data, bot_token)
        print("   ❌ Ожидалась ошибка, но валидация прошла успешно")
    except ValueError as e:
        if "Invalid hash signature" in str(e):
            print("   ✅ Правильно отловлена ошибка невалидного хеша")
        else:
            print(f"   ❌ Неожиданная ошибка: {e}")
    except Exception as e:
        print(f"   ❌ Неожиданная ошибка: {e}")

    # Тест 3: Истекшее время авторизации
    print("\n⏰ Тест 3: Истекшее время авторизации")
    try:
        # Создаем данные с прошлым временем
        old_user_data = {"id": 123456789, "first_name": "John"}
        old_auth_date = int(time.time()) - 86401  # Более 24 часов назад
        user_json = json.dumps(old_user_data, separators=(",", ":"))
        user_encoded = urllib.parse.quote(user_json)

        # Создаем хеш для старых данных
        data_string = f"auth_date={old_auth_date}\nuser={user_encoded}"
        hash_value = create_telegram_hash(data_string, bot_token)

        expired_data = (
            f"user={user_encoded}&auth_date={old_auth_date}&hash={hash_value}"
        )
        validate_telegram_init_data(expired_data, bot_token)
        print("   ❌ Ожидалась ошибка истекшего времени, но валидация прошла успешно")
    except ValueError as e:
        if "Authentication expired" in str(e):
            print("   ✅ Правильно отловлена ошибка истекшего времени")
        else:
            print(f"   ❌ Неожиданная ошибка: {e}")
    except Exception as e:
        print(f"   ❌ Неожиданная ошибка: {e}")

    # Тест 4: Отсутствующие обязательные поля
    print("\n🚫 Тест 4: Отсутствующие обязательные поля")
    try:
        missing_hash_data = "user=%7B%22id%22%3A123456789%2C%22first_name%22%3A%22John%22%7D&auth_date=1640995200"
        validate_telegram_init_data(missing_hash_data, bot_token)
        print("   ❌ Ожидалась ошибка отсутствующего хеша, но валидация прошла успешно")
    except ValueError as e:
        if "Missing required parameters" in str(e):
            print("   ✅ Правильно отловлена ошибка отсутствующих данных")
        else:
            print(f"   ❌ Неожиданная ошибка: {e}")
    except Exception as e:
        print(f"   ❌ Неожиданная ошибка: {e}")

    # Тест 5: Невалидный JSON в данных пользователя
    print("\n📝 Тест 5: Невалидный JSON в данных пользователя")
    try:
        invalid_json_data = "user=invalid_json&auth_date=1640995200&hash=abc123"
        validate_telegram_init_data(invalid_json_data, bot_token)
        print("   ❌ Ожидалась ошибка невалидного JSON, но валидация прошла успешно")
    except ValueError as e:
        if "Invalid user data JSON" in str(e):
            print("   ✅ Правильно отловлена ошибка невалидного JSON")
        else:
            print(f"   ❌ Неожиданная ошибка: {e}")
    except Exception as e:
        print(f"   ❌ Неожиданная ошибка: {e}")


def test_hash_creation():
    """Тестирует создание хеша."""

    print("\n🔐 Тестирование создания хеша")
    print("=" * 30)

    # Тестовые данные
    data_string = "auth_date=1640995200\nuser=%7B%22id%22%3A123456789%7D"
    bot_token = "test_bot_token"

    try:
        hash_value = create_telegram_hash(data_string, bot_token)
        print(f"✅ Хеш успешно создан: {hash_value[:16]}...")

        # Проверяем, что хеш имеет правильную длину (64 символа для SHA256)
        if len(hash_value) == 64:
            print("✅ Длина хеша корректна")
        else:
            print(f"❌ Неожиданная длина хеша: {len(hash_value)}")

    except Exception as e:
        print(f"❌ Ошибка создания хеша: {e}")


def main():
    """Основная функция тестирования."""

    print("🚀 Запуск тестов валидации Telegram initData")
    print("=" * 60)

    # Тестируем создание хеша
    test_hash_creation()

    # Тестируем валидацию
    test_validation()

    print("\n" + "=" * 60)
    print("🏁 Тестирование завершено")


if __name__ == "__main__":
    main()
