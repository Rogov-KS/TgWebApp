#!/bin/bash

echo "🛑 Принудительная остановка всех процессов проекта..."

# Функция для вывода информации о процессах
show_processes_info() {
    local process_name=$1
    local pids=$(pgrep -f "$process_name" 2>/dev/null)

    if [ -n "$pids" ]; then
        echo "📋 Найдены процессы $process_name:"
        for pid in $pids; do
            ps -p $pid -o pid,ppid,cmd --no-headers 2>/dev/null || echo "  PID $pid (процесс недоступен)"
        done
        return 0
    else
        echo "ℹ️  Процессы $process_name не найдены"
        return 1
    fi
}

# Функция для завершения процессов по имени
kill_processes_by_name() {
    local process_name=$1
    local pids=$(pgrep -f "$process_name" 2>/dev/null)

    if [ -n "$pids" ]; then
        echo "🔄 Останавливаем процессы $process_name (PID: $pids)..."
        kill -9 $pids 2>/dev/null || true
        echo "✅ Процессы $process_name остановлены"
    else
        echo "ℹ️  Процессы $process_name не найдены"
    fi
}

# Функция для завершения процессов по порту
kill_processes_by_port() {
    local port=$1
    local pids=$(lsof -ti:$port 2>/dev/null)

    if [ -n "$pids" ]; then
        echo "🔄 Останавливаем процессы на порту $port (PID: $pids)..."
        kill -9 $pids 2>/dev/null || true
        echo "✅ Процессы на порту $port остановлены"
    else
        echo "ℹ️  Процессы на порту $port не найдены"
    fi
}

# Функция для получения всех портов backend из конфигурации
get_backend_ports() {
    # Пытаемся получить порт из main.py
    local main_port=$(grep -o "port=[0-9]*" backend/main.py 2>/dev/null | head -1 | cut -d'=' -f2)
    if [ -n "$main_port" ]; then
        echo "$main_port"
    else
        echo "8000"  # Порт по умолчанию
    fi

    # Добавляем другие возможные порты для backend
    echo "8001"
    echo "8002"
    echo "8003"
    echo "8004"
    echo "8005"
}

# Функция для получения всех портов frontend из конфигурации
get_frontend_ports() {
    # Пытаемся получить порт из package.json или vite.config.ts
    local package_port=$(grep -o '"dev":.*--port [0-9]*' frontend/package.json 2>/dev/null | grep -o '[0-9]*' | head -1)
    if [ -n "$package_port" ]; then
        echo "$package_port"
    else
        echo "5173"  # Порт по умолчанию для Vite
    fi

    # Добавляем другие возможные порты для frontend
    echo "5174"
    echo "5175"
    echo "5176"
    echo "5177"
    echo "5178"
    echo "5179"
    echo "5180"
}

# Получаем все возможные порты
BACKEND_PORTS=($(get_backend_ports))
FRONTEND_PORTS=($(get_frontend_ports))

echo "🔍 Проверяемые порты:"
echo "  Backend: ${BACKEND_PORTS[*]}"
echo "  Frontend: ${FRONTEND_PORTS[*]}"

# Показываем информацию о процессах перед остановкой
echo ""
echo "📊 Информация о процессах перед остановкой:"

# Процессы по PID файлам
if [ -f .backend.pid ]; then
    pid=$(cat .backend.pid)
    echo "📋 Backend (PID файл):"
    ps -p $pid -o pid,ppid,cmd --no-headers 2>/dev/null || echo "  PID $pid (процесс недоступен)"
fi

if [ -f .frontend.pid ]; then
    pid=$(cat .frontend.pid)
    echo "📋 Frontend (PID файл):"
    ps -p $pid -o pid,ppid,cmd --no-headers 2>/dev/null || echo "  PID $pid (процесс недоступен)"
fi

if [ -f .bot.pid ]; then
    pid=$(cat .bot.pid)
    echo "📋 Telegram Bot (PID файл):"
    ps -p $pid -o pid,ppid,cmd --no-headers 2>/dev/null || echo "  PID $pid (процесс недоступен)"
fi

# Процессы по имени
echo ""
show_processes_info "python.*main.py"
show_processes_info "python.*bot.py"
show_processes_info "node.*vite"
show_processes_info "ngrok"

# Процессы по портам
echo ""
echo "📋 Процессы на портах:"
for port in "${BACKEND_PORTS[@]}"; do
    lsof -i:$port 2>/dev/null | grep LISTEN || echo "  Порт $port: нет активных процессов"
done

for port in "${FRONTEND_PORTS[@]}"; do
    lsof -i:$port 2>/dev/null | grep LISTEN || echo "  Порт $port: нет активных процессов"
done

echo ""
echo "🛑 Начинаем остановку процессов..."

# Останавливаем процессы по PID файлам (если есть)
if [ -f .backend.pid ]; then
    pid=$(cat .backend.pid)
    echo "🔄 Останавливаем backend (PID: $pid)..."
    kill -9 $pid 2>/dev/null || true
    rm .backend.pid
    echo "✅ Backend остановлен"
fi

if [ -f .frontend.pid ]; then
    pid=$(cat .frontend.pid)
    echo "🔄 Останавливаем frontend (PID: $pid)..."
    kill -9 $pid 2>/dev/null || true
    rm .frontend.pid
    echo "✅ Frontend остановлен"
fi

if [ -f .bot.pid ]; then
    pid=$(cat .bot.pid)
    echo "🔄 Останавливаем telegram bot (PID: $pid)..."
    kill -9 $pid 2>/dev/null || true
    rm .bot.pid
    echo "✅ Telegram bot остановлен"
fi

# Останавливаем процессы по имени
kill_processes_by_name "python.*main.py"
kill_processes_by_name "python.*bot.py"
kill_processes_by_name "node.*vite"
kill_processes_by_name "ngrok"

# Останавливаем процессы по всем возможным портам
echo ""
echo "🔄 Остановка процессов на всех портах backend..."
for port in "${BACKEND_PORTS[@]}"; do
    kill_processes_by_port $port
done

echo ""
echo "🔄 Остановка процессов на всех портах frontend..."
for port in "${FRONTEND_PORTS[@]}"; do
    kill_processes_by_port $port
done

# Дополнительная очистка - убиваем все процессы Python и Node, связанные с проектом
echo ""
echo "🧹 Дополнительная очистка процессов проекта..."

# Убиваем все процессы Python, связанные с проектом
pids=$(pgrep -f "python.*TgWebApp" 2>/dev/null)
if [ -n "$pids" ]; then
    echo "🔄 Останавливаем процессы Python проекта (PID: $pids)..."
    kill -9 $pids 2>/dev/null || true
    echo "✅ Процессы Python проекта остановлены"
fi

# Убиваем все процессы Node, связанные с проектом
pids=$(pgrep -f "node.*TgWebApp" 2>/dev/null)
if [ -n "$pids" ]; then
    echo "🔄 Останавливаем процессы Node проекта (PID: $pids)..."
    kill -9 $pids 2>/dev/null || true
    echo "✅ Процессы Node проекта остановлены"
fi

echo ""
echo "✅ Все процессы проекта остановлены!"

# Показываем, что осталось
echo ""
echo "📊 Текущие процессы проекта:"
ps aux | grep -E "(python|node)" | grep -v grep | grep TgWebApp || echo "Процессы проекта не найдены"

echo ""
echo "🎉 Очистка завершена!"