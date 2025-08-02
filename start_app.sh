#!/bin/bash

# Функция для обработки сигналов завершения
cleanup() {
    echo "Получен сигнал завершения. Останавливаем все процессы..."
    kill $BACKEND_PID $FRONTEND_PID $BOT_PID 2>/dev/null
    wait $BACKEND_PID $FRONTEND_PID $BOT_PID 2>/dev/null
    echo "Все процессы остановлены."
    exit 0
}

# Устанавливаем обработчики сигналов
trap cleanup SIGINT SIGTERM

echo "Запуск всех компонентов приложения..."

# Запуск backend в фоновом режиме
echo "Запуск backend..."
./start_backend.sh &
BACKEND_PID=$!
echo "Backend запущен с PID: $BACKEND_PID"

# Небольшая задержка для запуска backend
sleep 2

# Запуск frontend в фоновом режиме
echo "Запуск frontend..."
./start_frontend.sh &
FRONTEND_PID=$!
echo "Frontend запущен с PID: $FRONTEND_PID"

# Небольшая задержка для запуска frontend
sleep 2

# Запуск telegram bot в фоновом режиме
echo "Запуск telegram bot..."
./start_tg_bot.sh &
BOT_PID=$!
echo "Telegram bot запущен с PID: $BOT_PID"

echo ""
echo "Все компоненты запущены:"
echo "- Backend PID: $BACKEND_PID"
echo "- Frontend PID: $FRONTEND_PID"
echo "- Telegram Bot PID: $BOT_PID"
echo ""
echo "Для остановки всех процессов нажмите Ctrl+C"

# Ожидание завершения всех процессов
wait $BACKEND_PID $FRONTEND_PID $BOT_PID