# Настройка отправки email писем

## Обзор

В проекте реализована система отправки приветственных писем при регистрации новых пользователей с использованием Celery и Redis.

## Архитектура

- **Celery**: Асинхронная обработка задач
- **Redis**: Брокер сообщений и хранилище результатов
- **aiosmtplib**: Асинхронная отправка email
- **Jinja2**: Шаблонизация email писем
- **Flower**: Веб-интерфейс для мониторинга Celery

## Настройка

### 1. Установка зависимостей

Зависимости уже добавлены в `pyproject.toml`:
- `celery>=5.5.3`
- `aiosmtplib>=4.0.1`
- `jinja2>=3.1.6`
- `flower>=2.0.1`

### 2. Настройка переменных окружения

Добавьте следующие переменные в `.env` файл:

```bash
# Redis настройки
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# Email настройки (Gmail пример)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_USE_TLS=true
SMTP_USE_SSL=false
EMAIL_FROM=your-email@gmail.com
EMAIL_FROM_NAME=TgWebApp
```

### 3. Настройка Gmail

Для использования Gmail:

1. Включите двухфакторную аутентификацию
2. Создайте пароль приложения:
   - Перейдите в настройки Google аккаунта
   - Безопасность → Пароли приложений
   - Создайте новый пароль для "Почта"
3. Используйте этот пароль в `SMTP_PASSWORD`

### 4. Запуск Redis

```bash
# Ubuntu/Debian
sudo apt-get install redis-server
sudo systemctl start redis-server

# macOS
brew install redis
brew services start redis

# Проверка
redis-cli ping
```

### 5. Запуск Celery worker

```bash
# Из корневой директории проекта
./start_scripts/start_celery.sh

# Или вручную
cd backend
celery -A backend.celery_app.app worker --loglevel=info
```

### 6. Запуск Flower (опционально)

```bash
# Веб-интерфейс для мониторинга Celery
celery -A backend.celery_app.app flower --port=5555
```

## Использование

### Отправка приветственного письма

При регистрации нового пользователя автоматически отправляется приветственное письмо:

```python
from backend.celery_app.tasks.email import send_welcome_email

# Запуск задачи
send_welcome_email.delay(
    user_email="user@example.com",
    username="username"
)
```

### Мониторинг задач

```bash
# Просмотр активных задач
celery -A backend.celery_app.app inspect active

# Просмотр статистики
celery -A backend.celery_app.app inspect stats

# Просмотр очередей
celery -A backend.celery_app.app inspect queues

# Веб-интерфейс Flower
# Откройте http://localhost:5555 в браузере
```

## Структура файлов

```
backend/
├── celery_app/
│   ├── __init__.py
│   ├── app.py              # Конфигурация Celery
│   ├── tasks/
│   │   ├── __init__.py
│   │   └── email.py        # Email задачи
│   ├── templates/
│   │   └── welcome_email.html  # Шаблон письма
│   └── README.md
├── core/
│   └── config.py           # Настройки email
└── api/endpoints/
    └── auth.py             # Интеграция с регистрацией
```

## Шаблоны писем

Шаблоны находятся в `backend/celery_app/templates/` и используют Jinja2:

- `welcome_email.html`: Приветственное письмо для новых пользователей

## Обработка ошибок

- Автоматические повторные попытки (до 3 раз)
- Экспоненциальная задержка между попытками
- Логирование всех ошибок
- Не прерывает регистрацию пользователя при ошибке отправки

## Тестирование

### Локальное тестирование

1. Запустите Redis
2. Запустите Celery worker
3. Зарегистрируйте нового пользователя
4. Проверьте логи Celery worker

### Проверка email

```python
# В Python shell
from backend.celery_app.tasks.email import send_welcome_email

result = send_welcome_email.delay("test@example.com", "testuser")
print(result.get())  # Результат выполнения
```

## Troubleshooting

### Проблемы с Redis

```bash
# Проверка статуса Redis
redis-cli ping

# Очистка всех данных (осторожно!)
redis-cli flushall
```

### Проблемы с Celery

```bash
# Перезапуск worker
pkill -f celery
celery -A backend.celery_app.app worker --loglevel=info

# Проверка логов
tail -f celery.log
```

### Проблемы с email

1. Проверьте настройки SMTP
2. Убедитесь, что пароль приложения правильный
3. Проверьте логи Celery worker
4. Убедитесь, что email не попадает в спам

## Производительность

- Worker использует 2 процесса по умолчанию
- Задачи выполняются асинхронно
- Redis обеспечивает быструю обработку очередей
- Автоматическая очистка завершенных задач

## Безопасность

- Пароли приложений для email
- TLS/SSL шифрование
- Валидация email адресов
- Логирование без чувствительных данных

## Flower - Веб-интерфейс

Flower предоставляет веб-интерфейс для мониторинга Celery:

- Просмотр активных задач
- Статистика выполнения
- Мониторинг worker'ов
- Управление задачами

Запуск: `celery -A backend.celery_app.app flower --port=5555`
