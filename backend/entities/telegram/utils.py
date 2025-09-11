"""Утилиты для работы с Telegram авторизацией."""

import hashlib
import hmac
import json
import urllib.parse
from typing import Dict, Optional

from backend.core.config import settings
from backend.entities.telegram.schemas import TelegramInitData


def parse_telegram_init_data(init_data: str) -> TelegramInitData:
    """
    Парсит строку initData от Telegram Mini App.

    Args:
        init_data: Строка initData от Telegram

    Returns:
        TelegramInitData: Распарсенные данные

    Raises:
        ValueError: Если данные невалидны
    """
    try:
        # Парсим query string
        parsed_data = urllib.parse.parse_qs(init_data)

        # Извлекаем данные пользователя
        user_data = None
        if 'user' in parsed_data:
            user_json = parsed_data['user'][0]
            user_data = json.loads(user_json)

        # Создаем объект TelegramInitData
        init_data_obj = TelegramInitData(
            user=user_data,
            chat_instance=parsed_data.get('chat_instance', [None])[0],
            chat_type=parsed_data.get('chat_type', [None])[0],
            auth_date=int(parsed_data['auth_date'][0]),
            hash=parsed_data['hash'][0]
        )

        return init_data_obj

    except (KeyError, ValueError, json.JSONDecodeError) as e:
        raise ValueError(f"Невалидные данные Telegram: {e}") from e


def validate_telegram_init_data(init_data: str) -> bool:
    """
    Валидирует подлинность данных initData от Telegram.

    Args:
        init_data: Строка initData от Telegram

    Returns:
        bool: True если данные валидны, False иначе
    """
    try:
        # Парсим данные
        parsed_data = urllib.parse.parse_qs(init_data)

        # Извлекаем хеш
        received_hash = parsed_data.get('hash', [None])[0]
        if not received_hash:
            return False

        # Создаем строку для проверки (без hash параметра)
        check_string_parts = []
        for key, value in parsed_data.items():
            if key != 'hash':
                check_string_parts.append(f"{key}={value[0]}")

        check_string = '\n'.join(sorted(check_string_parts))

        # Создаем секретный ключ из токена бота
        secret_key = hmac.new(
            b"WebAppData",
            settings.TG_BOT_TOKEN.encode(),
            hashlib.sha256
        ).digest()

        # Вычисляем хеш
        calculated_hash = hmac.new(
            secret_key,
            check_string.encode(),
            hashlib.sha256
        ).hexdigest()

        # Сравниваем хеши
        return hmac.compare_digest(received_hash, calculated_hash)

    except Exception:
        return False


def is_telegram_data_fresh(
    auth_date: int, max_age_seconds: int = 86400
) -> bool:
    """
    Проверяет, не устарели ли данные авторизации.

    Args:
        auth_date: Unix timestamp времени авторизации
        max_age_seconds: Максимальный возраст данных в секундах
                     (по умолчанию 24 часа)

    Returns:
        bool: True если данные свежие, False иначе
    """
    import time
    current_time = int(time.time())
    return (current_time - auth_date) <= max_age_seconds


def extract_user_data_from_init_data(
    init_data: str
) -> Optional[Dict]:
    """
    Извлекает данные пользователя из initData.

    Args:
        init_data: Строка initData от Telegram

    Returns:
        Optional[Dict]: Данные пользователя или None
    """
    try:
        parsed_data = urllib.parse.parse_qs(init_data)
        if 'user' in parsed_data:
            return json.loads(parsed_data['user'][0])
        return None
    except Exception:
        return None
