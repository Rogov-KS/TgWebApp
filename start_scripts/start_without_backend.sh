#!/bin/bash

# Функция для обработки сигналов завершения
cleanup() {
    echo "Получен сигнал завершения. Останавливаем все процессы..."
    kill $FRONTEND_PID $BOT_PID $CELERY_PID 2>/dev/null
    wait $FRONTEND_PID $BOT_PID $CELERY_PID 2>/dev/null
    echo "Все процессы остановлены."
    exit 0
}

# Устанавливаем обработчики сигналов
trap cleanup SIGINT SIGTERM

echo "Запуск всех компонентов приложения (кроме backend)..."

# Проверяем, что виртуальное окружение активировано
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "⚠️  Виртуальное окружение не активировано. Активируйте его перед запуском."
    echo "   source venv/bin/activate  # или путь к вашему виртуальному окружению"
    exit 1
fi

# Запуск frontend в фоновом режиме
echo "🚀 Запуск frontend..."
./start_scripts/start_frontend.sh &
FRONTEND_PID=$!
echo "Frontend запущен с PID: $FRONTEND_PID"

# Небольшая задержка для запуска frontend
sleep 3

# Запуск telegram bot в фоновом режиме
echo "🤖 Запуск telegram bot..."
./start_scripts/start_tg_bot.sh > /dev/null &
BOT_PID=$!
echo "Telegram bot запущен с PID: $BOT_PID"

# Небольшая задержка для запуска telegram bot
sleep 2

# Запуск Celery worker в фоновом режиме
echo "📧 Запуск Celery worker..."
./start_scripts/start_celery.sh > /dev/null &
CELERY_PID=$!
echo "Celery worker запущен с PID: $CELERY_PID"

# Небольшая задержка для запуска Celery
sleep 2

echo ""
echo "✅ Все компоненты запущены (кроме backend):"
echo "- Frontend PID: $FRONTEND_PID"
echo "- Telegram Bot PID: $BOT_PID"
echo "- Celery Worker PID: $CELERY_PID"
echo ""
echo "🌐 Frontend доступен по адресу: http://localhost:5173"
echo "🤖 Telegram Bot работает в фоновом режиме"
echo "📧 Celery Worker обрабатывает задачи"
echo ""
echo "Для остановки всех процессов нажмите Ctrl+C"

# Ожидание завершения всех процессов
wait $FRONTEND_PID $BOT_PID $CELERY_PID
