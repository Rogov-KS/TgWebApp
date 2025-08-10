# Celery App Module

Модуль для асинхронных задач, выполняемых с помощью Celery.

## Структура

```
celery_app/
├── __init__.py
├── app.py              # Конфигурация Celery
├── tasks/
│   ├── __init__.py
│   └── email.py        # Email задачи
├── templates/
│   └── welcome_email.html  # Email шаблоны
└── README.md
```

## Email Tasks

### send_welcome_email

Отправляет приветственное письмо новому пользователю при регистрации.

**Параметры:**
- `user_email` (str): Email пользователя
- `username` (str): Имя пользователя

**Возвращает:**
- `dict`: Результат выполнения задачи

**Особенности:**
- Автоматические повторные попытки (до 3 раз)
- Экспоненциальная задержка между попытками
- Логирование всех операций
- Не прерывает регистрацию при ошибке

## Использование

### Запуск задачи

```python
from backend.celery_app.tasks.email import send_welcome_email

# Асинхронный запуск
result = send_welcome_email.delay(
    user_email="user@example.com",
    username="username"
)

# Получение результата
print(result.get())
```

### Мониторинг

```bash
# Просмотр активных задач
celery -A backend.celery_app.app inspect active

# Просмотр статистики
celery -A backend.celery_app.app inspect stats

# Запуск Flower для веб-интерфейса
celery -A backend.celery_app.app flower
```

## Конфигурация

Настройки находятся в `backend/core/config.py`:

- `SMTP_HOST`: SMTP сервер
- `SMTP_PORT`: Порт SMTP
- `SMTP_USERNAME`: Имя пользователя
- `SMTP_PASSWORD`: Пароль
- `EMAIL_FROM`: Email отправителя
- `EMAIL_FROM_NAME`: Имя отправителя

## Шаблоны

Email шаблоны находятся в `backend/celery_app/templates/`:

- `welcome_email.html`: Приветственное письмо

## Обработка ошибок

Все ошибки логируются и не прерывают основной процесс регистрации пользователя.
