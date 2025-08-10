#!/bin/bash

# Скрипт для запуска Celery worker

# Проверяем, что виртуальное окружение активировано
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "Виртуальное окружение не активировано. Активируйте его перед запуском."
    exit 1
fi

# Проверяем, что Redis запущен
if ! command -v redis-cli &> /dev/null; then
    echo "Redis не установлен или не найден в PATH"
    exit 1
fi

# Проверяем подключение к Redis
if ! redis-cli ping &> /dev/null; then
    echo "Redis не запущен. Запустите Redis перед запуском Celery worker"
    exit 1
fi

echo "🚀 Запуск Celery worker..."

# Запускаем Celery worker
celery -A backend.celery_app.app:celery_app worker \
    --loglevel=INFO \
    --concurrency=2 \
    --pool=solo
