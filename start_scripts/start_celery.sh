#!/bin/bash

# Скрипт для запуска Celery worker

# Проверяем, что виртуальное окружение активировано
source .venv/bin/activate

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

clear


echo "🚀 Запуск Celery worker и flower..."

# Запускаем Celery flower в фоне
echo "🌺 Запуск Celery flower..."
celery -A backend.celery_app.app:celery_app flower &
FLOWER_PID=$!

# Запускаем Celery worker в фоне
echo "⚙️ Запуск Celery worker..."
celery -A backend.celery_app.app:celery_app worker \
    --loglevel=INFO \
    --concurrency=2 \
    --pool=solo &
WORKER_PID=$!

echo "✅ Celery worker (PID: $WORKER_PID) и flower (PID: $FLOWER_PID) запущены"

# Ждем завершения любого из процессов
wait
