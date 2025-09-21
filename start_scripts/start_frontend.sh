#!/bin/bash

# Функция для отображения справки
show_help() {
    echo "Использование: $0 [ОПЦИИ]"
    echo ""
    echo "Опции:"
    echo "  -p, --port PORT    Указать порт для запуска frontend (по умолчанию: 5173)"
    echo "  -h, --help         Показать эту справку"
    echo ""
    echo "Примеры:"
    echo "  $0                 # Запуск с портом по умолчанию (5173)"
    echo "  $0 -p 3000         # Запуск на порту 3000"
    echo "  $0 --port 8080     # Запуск на порту 8080"
}

# Значение порта по умолчанию
PORT=5173

# Обработка аргументов командной строки
while [[ $# -gt 0 ]]; do
    case $1 in
        -p|--port)
            PORT="$2"
            shift 2
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            echo "Неизвестная опция: $1"
            echo "Используйте -h или --help для получения справки"
            exit 1
            ;;
    esac
done

# Проверяем, что порт является числом
if ! [[ "$PORT" =~ ^[0-9]+$ ]]; then
    echo "Ошибка: Порт должен быть числом. Получено: $PORT"
    exit 1
fi

# Проверяем диапазон портов
if [ "$PORT" -lt 1024 ] || [ "$PORT" -gt 65535 ]; then
    echo "Ошибка: Порт должен быть в диапазоне 1024-65535. Получено: $PORT"
    exit 1
fi

echo "Запуск frontend на порту: $PORT"

cd frontend

if [ -f "../.env" ]; then
    # Получаем переменную из .env
    export VITE_NGROK_FRONTEND_URL_SH=$(grep "^VITE_NGROK_FRONTEND_URL=" ../.env | cut -d'=' -f2 | sed 's|^https://||')
    echo "Найдена переменная VITE_NGROK_FRONTEND_URL: $VITE_NGROK_FRONTEND_URL_SH"

    # Обновляем vite.config.ts с новым значением
    if [ ! -z "$VITE_NGROK_FRONTEND_URL_SH" ]; then
        sed -i "s/allowedHosts: \[.*\]/allowedHosts: [\"$VITE_NGROK_FRONTEND_URL_SH\"]/" vite.config.ts
        echo "Обновлен vite.config.ts с новым allowedHosts: $VITE_NGROK_FRONTEND_URL_SH"
    fi
else
    echo "Файл .env не найден в корне проекта"
fi

clear

# Запускаем npm run dev с указанным портом
npm run dev -- --port $PORT
