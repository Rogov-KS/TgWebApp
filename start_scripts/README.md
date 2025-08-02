# Скрипты запуска

## Новые скрипты

### `start_all_with_ngrok.sh`
Полный скрипт для запуска всего стека приложения с автоматической настройкой ngrok.

**Что делает:**
1. Запускает `ngrok start --all`
2. Ждет готовности ngrok API
3. Получает URL'ы туннелей для backend (порт 8000) и frontend (порт 5173)
4. Обновляет `.env` файл с полученными URL'ами
5. Запускает backend, frontend и telegram bot в фоновом режиме
6. Сохраняет PID'ы процессов для возможности остановки

**Использование:**
```bash
./start_scripts/start_all_with_ngrok.sh
```

**Требования:**
- Установленный `ngrok`
- Установленный `jq` (для парсинга JSON): `sudo apt install jq`
- Установленный `curl`

### `stop_all.sh`
Скрипт для остановки всех сервисов.

**Что делает:**
1. Останавливает backend, frontend и telegram bot по PID'ам
2. Останавливает ngrok
3. Очищает оставшиеся процессы по имени

**Использование:**
```bash
./start_scripts/stop_all.sh
```

## Существующие скрипты

### `start_backend.sh`
Запускает только backend сервер.

### `start_frontend.sh`
Запускает только frontend с автоматическим обновлением `vite.config.ts`.

### `start_tg_bot.sh`
Запускает только telegram bot.

### `start_app.sh`
Запускает backend и frontend без ngrok.

## Примеры использования

### Запуск полного стека с ngrok
```bash
# Запуск всех сервисов
./start_scripts/start_all_with_ngrok.sh

# Остановка всех сервисов
./start_scripts/stop_all.sh
```

### Запуск отдельных сервисов
```bash
# Только backend
./start_scripts/start_backend.sh

# Только frontend
./start_scripts/start_frontend.sh

# Только telegram bot
./start_scripts/start_tg_bot.sh
```

## Структура .env файла

После запуска `start_all_with_ngrok.sh` в корне проекта будет создан/обновлен `.env` файл:

```env
# Ngrok URLs
VITE_NGROK_BACKEND_URL=https://xxxx-xx-xx-xx-xx.ngrok.io
VITE_NGROK_FRONTEND_URL=https://yyyy-yy-yy-yy-yy.ngrok.io

# Другие переменные окружения (если есть)
```

## Устранение неполадок

### Ngrok не запускается
1. Убедитесь, что ngrok установлен: `ngrok version`
2. Проверьте, что порты 8000 и 5173 свободны
3. Убедитесь, что у вас есть активная сессия ngrok

### jq не установлен
```bash
sudo apt install jq
```

### Процессы не останавливаются
```bash
# Принудительная остановка всех процессов
pkill -f "python.*main.py"
pkill -f "npm.*dev"
pkill -f "ngrok"
```

## Логи

Все процессы запускаются в фоновом режиме. Для просмотра логов используйте:

```bash
# Логи backend
tail -f backend.log

# Логи frontend (в терминале frontend)
# Логи ngrok (в веб-интерфейсе http://localhost:4040)
```