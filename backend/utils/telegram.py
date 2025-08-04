from datetime import datetime
import hashlib
import hmac
import json
from typing import Any
import urllib.parse

from backend.core.config import settings
from backend.core.exception import (
    InvalidTelegramDataException,
    TelegramAuthExpiredException,
    TelegramValidationException,
)


def create_telegram_hash(data_string: str) -> str:
    """
    Создает HMAC-SHA256 хеш для проверки подлинности данных Telegram.

    Args:
        data_string: Строка данных для хеширования

    Returns:
        Хеш в hex формате
    """
    if not settings.TELEGRAM_BOT_TOKEN:
        raise TelegramValidationException()

    secret_key = hmac.new(
        b"WebAppData", settings.TELEGRAM_BOT_TOKEN.encode(), hashlib.sha256
    ).digest()

    return hmac.new(secret_key, data_string.encode(), hashlib.sha256).hexdigest()


def validate_auth_date(auth_date: int) -> None:
    """
    Проверяет время авторизации (не старше 24 часов).

    Args:
        auth_date: Unix timestamp времени авторизации

    Raises:
        TelegramAuthExpiredException: Если время истекло
    """
    current_time = datetime.utcnow().timestamp()
    if current_time - auth_date > settings.TELEGRAM_AUTH_TIMEOUT:
        raise TelegramAuthExpiredException()


def extract_user_data(parsed_data: dict[str, Any]) -> dict[str, Any]:
    """
    Извлекает данные пользователя из распарсенных данных.

    Args:
        parsed_data: Словарь с распарсенными данными

    Returns:
        Словарь с данными пользователя

    Raises:
        InvalidTelegramDataException: Если данные пользователя отсутствуют
    """
    user_data_str = parsed_data.get("user", [None])[0]
    if not user_data_str:
        raise InvalidTelegramDataException()

    # Парсим JSON данные пользователя
    try:
        user_data = json.loads(user_data_str)
    except json.JSONDecodeError:
        raise InvalidTelegramDataException()

    return {
        "id": user_data.get("id"),
        "first_name": user_data.get("first_name"),
        "last_name": user_data.get("last_name"),
        "username": user_data.get("username"),
        "language_code": user_data.get("language_code"),
        "is_premium": user_data.get("is_premium", False),
        "photo_url": user_data.get("photo_url"),
    }


def validate_telegram_init_data(init_data: str) -> dict[str, Any]:
    """
    Валидирует initData от Telegram Web App.

    Args:
        init_data: Строка initData от Telegram

    Returns:
        Словарь с валидированными данными

    Raises:
        TelegramValidationException: Если валидация не прошла
        InvalidTelegramDataException: Если данные некорректны
        TelegramAuthExpiredException: Если время авторизации истекло
    """
    try:
        # Разбор initData на параметры
        parsed_data = urllib.parse.parse_qs(init_data)

        # Извлечение обязательных параметров
        auth_date_str = parsed_data.get("auth_date", [None])[0]
        hash_value = parsed_data.get("hash", [None])[0]

        if not auth_date_str or not hash_value:
            raise InvalidTelegramDataException()

        # Проверка времени авторизации
        auth_date = int(auth_date_str)
        validate_auth_date(auth_date)

        # Создание строки для хеширования (без hash параметра)
        data_check_string = []
        for key, value in parsed_data.items():
            if key != "hash":
                data_check_string.append(f"{key}={value[0]}")

        # Сортировка параметров по алфавиту
        data_check_string.sort()
        data_check_string_str = "\n".join(data_check_string)

        # Проверка HMAC-SHA256 подписи
        expected_hash = create_telegram_hash(data_check_string_str)
        if not hmac.compare_digest(hash_value, expected_hash):
            raise TelegramValidationException()

        # Извлечение данных пользователя
        user_data = extract_user_data(parsed_data)

        return {
            "user": user_data,
            "auth_date": auth_date,
            "hash": hash_value,
            "chat_data": parsed_data.get("chat", [None])[0],
            "start_param": parsed_data.get("start_param", [None])[0],
        }

    except (ValueError, KeyError):
        raise InvalidTelegramDataException()
    except Exception as e:
        if isinstance(
            e,
            (
                InvalidTelegramDataException,
                TelegramAuthExpiredException,
                TelegramValidationException,
            ),
        ):
            raise
        raise InvalidTelegramDataException()


def parse_telegram_init_data(init_data: str) -> dict[str, Any]:
    """
    Парсит initData и возвращает структурированные данные.

    Args:
        init_data: Строка initData от Telegram

    Returns:
        Словарь с распарсенными данными
    """
    parsed_data = urllib.parse.parse_qs(init_data)

    # Преобразование списков в одиночные значения
    result = {}
    for key, value in parsed_data.items():
        if len(value) == 1:
            result[key] = value[0]
        else:
            result[key] = value

    return result
