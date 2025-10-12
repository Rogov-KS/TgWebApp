#!/bin/bash

# Скрипт для запуска Docker Compose с ngrok
# Автоматически получает URL туннелей и обновляет .env файлы

set -e  # Остановить выполнение при ошибке

echo "🐳 Запуск Docker Compose с ngrok..."

# Функция для запуска ngrok
start_ngrok() {
    echo "🌐 Запуск ngrok..."

    # Запускаем ngrok в фоне
    ngrok start --all --config ~/.config/ngrok/ngrok.yml > /tmp/ngrok.log 2>&1 &
    local ngrok_pid=$!
    echo "ngrok запущен с PID: $ngrok_pid"

    # Ждем, чтобы ngrok инициализировался
    sleep 5

    # Возвращаем PID для отслеживания
    echo $ngrok_pid
}

# Функция для получения URL туннеля через ngrok API
get_ngrok_url() {
    local port=$1
    local max_attempts=10
    local attempt=1

    while [ $attempt -le $max_attempts ]; do
        local url=$(curl -s http://localhost:4040/api/tunnels 2>/dev/null | jq -r ".tunnels[] | select(.config.addr==\"http://localhost:$port\") | .public_url" | grep https | head -1)

        if [ -n "$url" ] && [ "$url" != "null" ]; then
            echo $url
            return 0
        fi

        sleep 2
        attempt=$((attempt + 1))
    done

    return 1
}

# Функция для обновления .env файлов
update_env_files() {
    local backend_url=$1
    local frontend_url=$2
    local env_file="./configs/envs/.env-base"

    echo "📝 Обновление переменных в $env_file..."

    # Создаем временный файл с обновленными значениями
    local temp_file=$(mktemp)

    # Обрабатываем файл построчно
    while IFS= read -r line; do
        if [[ $line == VITE_BACKEND_URL=* ]]; then
            echo "VITE_BACKEND_URL=${backend_url}/api/v1/"
        elif [[ $line == VITE_NGROK_FRONTEND_URL=* ]]; then
            echo "VITE_NGROK_FRONTEND_URL=${frontend_url}"
        elif [[ $line == VITE_NGROK_BACKEND_URL=* ]]; then
            echo "VITE_NGROK_BACKEND_URL=${backend_url}"
        else
            echo "$line"
        fi
    done < "$env_file" > "$temp_file"

    # Заменяем оригинальный файл
    mv "$temp_file" "$env_file"

    echo "✅ Переменные обновлены в $env_file"
}

# Функция для восстановления оригинальных значений
restore_env_files() {
    local env_file="./configs/envs/.env-base"

    echo "🔄 Восстановление оригинальных значений в $env_file..."

    # Восстанавливаем VITE_BACKEND_URL
    if grep -q "^VITE_BACKEND_URL=" "$env_file" 2>/dev/null; then
        sed -i "s|^VITE_BACKEND_URL=.*|VITE_BACKEND_URL=http://localhost:8000/api/v1/|" "$env_file"
    fi

    # Очищаем ngrok URLs
    if grep -q "^VITE_NGROK_FRONTEND_URL=" "$env_file" 2>/dev/null; then
        sed -i "s|^VITE_NGROK_FRONTEND_URL=.*|VITE_NGROK_FRONTEND_URL=|" "$env_file"
    fi

    if grep -q "^VITE_NGROK_BACKEND_URL=" "$env_file" 2>/dev/null; then
        sed -i "s|^VITE_NGROK_BACKEND_URL=.*|VITE_NGROK_BACKEND_URL=|" "$env_file"
    fi

    echo "✅ Оригинальные значения восстановлены"
}

# Функция для очистки временных файлов
cleanup_temp_files() {
    echo "🧹 Очистка временных файлов..."
    if [ -f "/tmp/ngrok.log" ]; then
        rm "/tmp/ngrok.log"
        echo "✅ Временный лог ngrok удален"
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
    if ! command -v ngrok &> /dev/null; then
        echo "❌ ngrok не установлен. Установите ngrok"
        exit 1
    fi

    if ! command -v jq &> /dev/null; then
        echo "❌ jq не установлен. Установите jq для работы с JSON"
        exit 1
    fi

    if ! command -v docker compose &> /dev/null; then
        echo "❌ docker compose не установлен"
        exit 1
    fi

    # Переходим в корневую директорию проекта
    cd "$(dirname "$0")/.."

    # Запускаем ngrok
    echo "🌐 Запуск ngrok для frontend и backend..."
    local ngrok_pid=$(start_ngrok)

    # Получаем URL туннелей
    echo "🔍 Получение URL туннелей..."
    frontend_url=$(get_ngrok_url 5173)
    backend_url=$(get_ngrok_url 9000)

    if [ -z "$frontend_url" ] || [ -z "$backend_url" ]; then
        echo "❌ Не удалось получить URL туннелей"
        pkill -f "ngrok" 2>/dev/null || true
        exit 1
    fi

    echo "✅ URL'ы получены:"
    echo "  Frontend: $frontend_url"
    echo "  Backend: $backend_url"

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

    # Останавливаем ngrok
    pkill -f "ngrok" 2>/dev/null || true

    # Восстанавливаем оригинальные значения
    restore_env_files

    # Очищаем временные файлы
    cleanup_temp_files

    echo "✅ Все сервисы остановлены"
    exit 0
}

# Устанавливаем обработчики сигналов
trap cleanup SIGINT SIGTERM

# Запускаем основную логику
main "$@"
