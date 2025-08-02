#!/bin/bash

# Скрипт для запуска ngrok и всех сервисов
# Автоматически получает URL'ы туннелей и обновляет .env файл

set -e  # Остановить выполнение при ошибке

echo "🚀 Запуск полного стека приложения с ngrok..."

# Функция для ожидания готовности ngrok
wait_for_ngrok() {
    echo "⏳ Ожидание готовности ngrok API..."
    local max_attempts=30
    local attempt=1

    while [ $attempt -le $max_attempts ]; do
        if curl -s http://localhost:4040/api/tunnels > /dev/null 2>&1; then
            echo "✅ Ngrok API готов"
            return 0
        fi

        echo "Попытка $attempt/$max_attempts..."
        sleep 2
        attempt=$((attempt + 1))
    done

    echo "❌ Не удалось подключиться к ngrok API"
    return 1
}

# Функция для получения URL туннеля по порту
get_tunnel_url() {
    local port=$1
    local url=$(curl -s http://localhost:4040/api/tunnels | jq -r ".tunnels[] | select(.config.addr | contains(\":$port\")) | .public_url" | head -1)
    echo "$url"
}

# Функция для обновления .env файла
update_env_file() {
    local backend_url=$1
    local frontend_url=$2

    echo "📝 Обновление .env файла..."

    # Создаем .env файл, если его нет
    if [ ! -f .env ]; then
        touch .env
    fi

    # Обновляем или добавляем VITE_NGROK_BACKEND_URL
    if grep -q "^VITE_NGROK_BACKEND_URL=" .env 2>/dev/null; then
        # Если переменная существует, заменяем её значение
        sed -i "s|^VITE_NGROK_BACKEND_URL=.*|VITE_NGROK_BACKEND_URL=$backend_url|" .env
    else
        # Если переменной нет, добавляем её
        echo "VITE_NGROK_BACKEND_URL=$backend_url" >> .env
    fi

    # Обновляем или добавляем VITE_NGROK_FRONTEND_URL
    if grep -q "^VITE_NGROK_FRONTEND_URL=" .env 2>/dev/null; then
        # Если переменная существует, заменяем её значение
        sed -i "s|^VITE_NGROK_FRONTEND_URL=.*|VITE_NGROK_FRONTEND_URL=$frontend_url|" .env
    else
        # Если переменной нет, добавляем её
        echo "VITE_NGROK_FRONTEND_URL=$frontend_url" >> .env
    fi

    echo "✅ .env файл обновлен"
}

# Функция для запуска сервисов в фоне
start_services() {
    echo "🚀 Запуск сервисов..."

    # Запуск frontend
    echo "🎨 Запуск frontend..."
    ./start_scripts/start_frontend.sh &
    local frontend_pid=$!
    echo "Frontend запущен с PID: $frontend_pid"

    # Ждем немного для запуска frontend
    sleep 3

    # Запуск telegram bot
    echo "🤖 Запуск telegram bot..."
    ./start_scripts/start_tg_bot.sh &
    local bot_pid=$!
    echo "Telegram bot запущен с PID: $bot_pid"

    # Ждем немного для запуска telegram bot
    sleep 3

    # Запуск backend
    echo "📡 Запуск backend..."
    ./start_scripts/start_backend.sh &
    local backend_pid=$!
    echo "Backend запущен с PID: $backend_pid"

    # Ждем немного для запуска telegram bot
    sleep 3


    # Сохраняем PID'ы для возможности остановки
    echo $backend_pid > .backend.pid
    echo $frontend_pid > .frontend.pid
    echo $bot_pid > .bot.pid

    echo ""
    echo "🎉 Все сервисы запущены!"
    echo "📊 PID'ы процессов:"
    echo "  Backend: $backend_pid"
    echo "  Frontend: $frontend_pid"
    echo "  Telegram Bot: $bot_pid"
    echo ""
    echo "🌐 URL'ы:"
    echo "  Backend: $backend_url"
    echo "  Frontend: $frontend_url"
    echo ""
    echo "Для убийства всех запущенных процессов выполните: ./start_scripts/kill_all_processes.sh"
}

# Основная логика
main() {
    # Проверяем наличие необходимых утилит
    if ! command -v jq &> /dev/null; then
        echo "❌ jq не установлен. Установите: sudo apt install jq"
        exit 1
    fi

    if ! command -v ngrok &> /dev/null; then
        echo "❌ ngrok не установлен"
        exit 1
    fi

    # Переходим в корневую директорию проекта
    cd "$(dirname "$0")/.."

    # Запускаем ngrok
    echo "🌐 Запуск ngrok..."
    ngrok start --all &
    local ngrok_pid=$!
    echo "Ngrok запущен с PID: $ngrok_pid"

    # Ждем готовности ngrok API
    if ! wait_for_ngrok; then
        echo "❌ Не удалось запустить ngrok"
        kill $ngrok_pid 2>/dev/null || true
        exit 1
    fi

    # Ждем создания туннелей
    echo "⏳ Ожидание создания туннелей..."
    sleep 5

    # Получаем URL'ы туннелей
    echo "🔍 Получение URL'ов туннелей..."
    backend_url=$(get_tunnel_url 8000)
    frontend_url=$(get_tunnel_url 5173)

    if [ -z "$backend_url" ] || [ "$backend_url" = "null" ]; then
        echo "❌ Не удалось получить URL backend туннеля"
        kill $ngrok_pid 2>/dev/null || true
        exit 1
    fi

    if [ -z "$frontend_url" ] || [ "$frontend_url" = "null" ]; then
        echo "❌ Не удалось получить URL frontend туннеля"
        kill $ngrok_pid 2>/dev/null || true
        exit 1
    fi

    echo "✅ URL'ы получены:"
    echo "  Backend: $backend_url"
    echo "  Frontend: $frontend_url"

    # Обновляем .env файл
    update_env_file "$backend_url" "$frontend_url"

    # Запускаем все сервисы
    start_services

    # Ждем завершения ngrok (или прерывания)
    wait $ngrok_pid
}

# Обработка сигналов для корректного завершения
cleanup() {
    echo ""
    echo "🛑 Остановка всех сервисов..."

    # Останавливаем процессы по PID'ам
    if [ -f .backend.pid ]; then
        kill $(cat .backend.pid) 2>/dev/null || true
        rm .backend.pid
    fi

    if [ -f .frontend.pid ]; then
        kill $(cat .frontend.pid) 2>/dev/null || true
        rm .frontend.pid
    fi

    if [ -f .bot.pid ]; then
        kill $(cat .bot.pid) 2>/dev/null || true
        rm .bot.pid
    fi

    # Останавливаем ngrok
    pkill -f "ngrok start" 2>/dev/null || true

    echo "✅ Все сервисы остановлены"
    exit 0
}

# Устанавливаем обработчики сигналов
trap cleanup SIGINT SIGTERM

# Запускаем основную логику
main "$@"