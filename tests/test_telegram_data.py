"""
Тестовые данные для проверки валидации Telegram initData.

Эти данные основаны на реальных примерах из документации Telegram Web App.
"""

# Пример валидного initData (для тестирования)
# Этот пример нужно будет обновить с реальным bot token
VALID_INIT_DATA = (
    "query_id=AAHdF6IQAAAAAN0XohDhrOrc&user=%7B%22id%22%3A123456789%2C%22first_name%22%3A%22John%22%2C%22last_name%22%3A%22Doe%22%2C%22username%22%3A%22johndoe%22%2C%22language_code%22%3A%22en%22%2C%22is_premium%22%3Atrue%2C%22photo_url%22%3A%22https%3A//t.me/i/userpic/320/johndoe.jpg%22%7D&auth_date=1640995200&hash=abc123def456"
)

# Пример initData с минимальными данными
MINIMAL_INIT_DATA = (
    "user=%7B%22id%22%3A123456789%2C%22first_name%22%3A%22John%22%7D&auth_date=1640995200&hash=abc123def456"
)

# Пример initData с премиум пользователем
PREMIUM_USER_INIT_DATA = (
    "user=%7B%22id%22%3A987654321%2C%22first_name%22%3A%22Alice%22%2C%22last_name%22%3A%22Smith%22%2C%22username%22%3A%22alicesmith%22%2C%22language_code%22%3A%22ru%22%2C%22is_premium%22%3Atrue%2C%22photo_url%22%3A%22https%3A//t.me/i/userpic/320/alicesmith.jpg%22%7D&auth_date=1640995200&hash=def456abc789"
)

# Пример initData с данными чата
CHAT_INIT_DATA = (
    "user=%7B%22id%22%3A555666777%2C%22first_name%22%3A%22Bob%22%2C%22last_name%22%3A%22Johnson%22%2C%22username%22%3A%22bobjohnson%22%2C%22language_code%22%3A%22en%22%2C%22is_premium%22%3Afalse%7D&chat=%7B%22id%22%3A-1001234567890%2C%22type%22%3A%22group%22%2C%22title%22%3A%22Test%20Group%22%7D&auth_date=1640995200&hash=ghi789def012"
)

# Пример initData с параметром запуска
START_PARAM_INIT_DATA = (
    "user=%7B%22id%22%3A111222333%2C%22first_name%22%3A%22Charlie%22%2C%22last_name%22%3A%22Brown%22%2C%22username%22%3A%22charliebrown%22%2C%22language_code%22%3A%22en%22%2C%22is_premium%22%3Afalse%7D&start_param=game_start&auth_date=1640995200&hash=jkl012ghi345"
)

# Невалидные примеры для тестирования ошибок
INVALID_HASH_INIT_DATA = (
    "user=%7B%22id%22%3A123456789%2C%22first_name%22%3A%22John%22%7D&auth_date=1640995200&hash=invalid_hash"
)

EXPIRED_AUTH_INIT_DATA = (
    "user=%7B%22id%22%3A123456789%2C%22first_name%22%3A%22John%22%7D&auth_date=1609459200&hash=abc123def456"
)

MISSING_USER_INIT_DATA = (
    "auth_date=1640995200&hash=abc123def456"
)

MISSING_HASH_INIT_DATA = (
    "user=%7B%22id%22%3A123456789%2C%22first_name%22%3A%22John%22%7D&auth_date=1640995200"
)

# Примеры декодированных данных пользователей
SAMPLE_USER_DATA = {
    "basic_user": {
        "id": 123456789,
        "first_name": "John",
        "last_name": "Doe",
        "username": "johndoe",
        "language_code": "en",
        "is_premium": True,
        "photo_url": "https://t.me/i/userpic/320/johndoe.jpg"
    },
    "minimal_user": {
        "id": 123456789,
        "first_name": "John",
        "last_name": None,
        "username": None,
        "language_code": None,
        "is_premium": False,
        "photo_url": None
    },
    "premium_user": {
        "id": 987654321,
        "first_name": "Alice",
        "last_name": "Smith",
        "username": "alicesmith",
        "language_code": "ru",
        "is_premium": True,
        "photo_url": "https://t.me/i/userpic/320/alicesmith.jpg"
    },
    "russian_user": {
        "id": 555666777,
        "first_name": "Иван",
        "last_name": "Петров",
        "username": "ivanpetrov",
        "language_code": "ru",
        "is_premium": False,
        "photo_url": None
    }
}

# Примеры данных чата
SAMPLE_CHAT_DATA = {
    "group_chat": {
        "id": -1001234567890,
        "type": "group",
        "title": "Test Group"
    },
    "private_chat": {
        "id": 123456789,
        "type": "private",
        "first_name": "John",
        "last_name": "Doe"
    }
}

# Функция для создания тестового initData с реальным хешем
def create_test_init_data(user_data: dict, bot_token: str = "test_bot_token") -> str:
    """
    Создает тестовый initData с валидным хешем.

    Args:
        user_data: Данные пользователя
        bot_token: Токен бота для создания хеша

    Returns:
        Строка initData с валидным хешем
    """
    import json
    import time
    import hashlib
    import hmac

    # Кодируем данные пользователя
    user_json = json.dumps(user_data, separators=(',', ':'))
    user_encoded = user_json.replace('"', '%22').replace(':', '%3A').replace(',', '%2C')

    # Создаем auth_date (текущее время)
    auth_date = int(time.time())

    # Создаем строку для хеширования
    data_string = f"auth_date={auth_date}\nuser={user_encoded}"

    # Создаем хеш
    secret_key = hmac.new(
        b"WebAppData",
        bot_token.encode(),
        hashlib.sha256
    ).digest()

    hash_value = hmac.new(
        secret_key,
        data_string.encode(),
        hashlib.sha256
    ).hexdigest()

    # Формируем initData
    init_data = f"user={user_encoded}&auth_date={auth_date}&hash={hash_value}"

    return init_data


# Примеры для тестирования различных сценариев
TEST_SCENARIOS = {
    "new_user": {
        "description": "Новый пользователь заходит впервые",
        "user_data": SAMPLE_USER_DATA["basic_user"],
        "expected_behavior": "Создание нового пользователя в БД"
    },
    "existing_user": {
        "description": "Существующий пользователь заходит снова",
        "user_data": SAMPLE_USER_DATA["premium_user"],
        "expected_behavior": "Обновление данных пользователя"
    },
    "premium_user": {
        "description": "Премиум пользователь",
        "user_data": SAMPLE_USER_DATA["premium_user"],
        "expected_behavior": "Установка флага is_premium"
    },
    "minimal_data": {
        "description": "Минимальные данные пользователя",
        "user_data": SAMPLE_USER_DATA["minimal_user"],
        "expected_behavior": "Создание пользователя с базовыми данными"
    },
    "russian_user": {
        "description": "Русскоязычный пользователь",
        "user_data": SAMPLE_USER_DATA["russian_user"],
        "expected_behavior": "Корректная обработка кириллицы"
    }
}