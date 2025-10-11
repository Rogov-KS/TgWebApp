#!/bin/bash

# Скрипт для запуска Docker Compose с ngrok
# Автоматически получает URL'ы туннелей и обновляет .env файлы

set -e  # Остановить выполнение при ошибке

echo "🐳 Запуск Docker Compose с ngrok..."

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

# Функция для обновления .env файлов
update_env_files() {
    local backend_url=$1
    local frontend_url=$2

    echo "📝 Обновление env файлов..."

    # Обновляем .env-base
    local env_base_file="./configs/envs/.env-base"
    if [ -f "$env_base_file" ]; then
        echo "  Обновляем $env_base_file"
        # Обновляем VITE_NGROK_BACKEND_URL
        if grep -q "^VITE_NGROK_BACKEND_URL=" "$env_base_file" 2>/dev/null; then
            sed -i "s|^VITE_NGROK_BACKEND_URL=.*|VITE_NGROK_BACKEND_URL=$backend_url|" "$env_base_file"
        else
            echo "VITE_NGROK_BACKEND_URL=$backend_url" >> "$env_base_file"
        fi
        # Обновляем VITE_NGROK_FRONTEND_URL
        if grep -q "^VITE_NGROK_FRONTEND_URL=" "$env_base_file" 2>/dev/null; then
            sed -i "s|^VITE_NGROK_FRONTEND_URL=.*|VITE_NGROK_FRONTEND_URL=$frontend_url|" "$env_base_file"
        else
            echo "VITE_NGROK_FRONTEND_URL=$frontend_url" >> "$env_base_file"
        fi
        echo "✅ $env_base_file обновлен"
    else
        echo "⚠️  Файл $env_base_file не найден"
    fi

    # Создаем временный .env файл для Docker Compose
    local temp_env_file="./.env"
    echo "📝 Создание временного .env файла для Docker..."
    cat > "$temp_env_file" << EOF
# Временный .env файл для Docker Compose с ngrok
VITE_NGROK_BACKEND_URL=$backend_url
VITE_NGROK_FRONTEND_URL=$frontend_url
EOF
    echo "✅ Временный .env файл создан"
}

# Функция для очистки временных файлов
cleanup_temp_files() {
    echo "🧹 Очистка временных файлов..."
    if [ -f "./.env" ]; then
        rm "./.env"
        echo "✅ Временный .env файл удален"
    fi
}

# Функция для остановки Docker Compose
stop_docker() {
    echo "🛑 Остановка Docker Compose..."
    docker compose down
    echo "✅ Docker Compose остановлен"
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

    if ! command -v docker compose &> /dev/null; then
        echo "❌ docker compose не установлен"
        exit 1
    fi

    # Переходим в корневую директорию проекта
    cd "$(dirname "$0")/.."

    # Запускаем ngrok
    echo "🌐 Запуск ngrok..."
    ngrok start --all > /dev/null 2>&1 &
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
    backend_url=$(get_tunnel_url 8000)  # Backend на порту 8000
    frontend_url=$(get_tunnel_url 5173) # Frontend на порту 5173

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

    # Обновляем .env файлы
    update_env_files "$backend_url" "$frontend_url"

    # Запускаем Docker Compose
    echo "🐳 Запуск Docker Compose..."
    docker compose up --build

    # Ждем завершения Docker Compose (или прерывания)
    wait
}

# Обработка сигналов для корректного завершения
cleanup() {
    echo ""
    echo "🛑 Остановка всех сервисов..."

    # Останавливаем Docker Compose
    stop_docker

    # Очищаем временные файлы
    cleanup_temp_files

    # Останавливаем ngrok
    pkill -f "ngrok start" 2>/dev/null || true

    echo "✅ Все сервисы остановлены"
    exit 0
}

# Устанавливаем обработчики сигналов
trap cleanup SIGINT SIGTERM

# Запускаем основную логику
main "$@"
