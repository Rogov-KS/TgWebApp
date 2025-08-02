# Telegram Bot для Snake Game

Этот бот предназначен для тестирования интеграции с Telegram Web App.

## 🚀 Быстрый старт

### 1. Создание бота в Telegram

1. Найдите [@BotFather](https://t.me/BotFather) в Telegram
2. Отправьте команду `/newbot`
3. Следуйте инструкциям для создания бота
4. Сохраните полученный токен

### 2. Настройка Web App

1. Отправьте команду `/setmenubutton` BotFather
2. Выберите вашего бота
3. Укажите URL вашего Web App (например: `https://your-domain.com`)
4. Укажите текст кнопки (например: "🎮 Начать игру")

### 3. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 4. Настройка переменных окружения

Создайте файл `.env` в папке `tg_bot`:

```env
# Токен вашего бота (получите у @BotFather)
TELEGRAM_BOT_TOKEN=your_bot_token_here

# URL вашего Web App
TELEGRAM_WEBAPP_URL=https://your-domain.com
```

### 5. Запуск бота

```bash
python bot.py
```

## 📋 Команды бота

- `/start` - Запустить игру
- `/help` - Справка
- `/info` - Информация об игре
- `/stats` - Статистика игрока

## 🔧 Настройка Web App

### В BotFather:

1. **Создание бота:**
   ```
   /newbot
   Snake Game Bot
   snake_game_bot
   ```

2. **Настройка Web App:**
   ```
   /setmenubutton
   @snake_game_bot
   https://your-domain.com
   🎮 Начать игру
   ```

3. **Дополнительные настройки:**
   ```
   /setdescription
   @snake_game_bot
   Классическая игра Snake в Telegram Web App

   /setabouttext
   @snake_game_bot
   Играйте в Snake прямо в Telegram!
   Автоматическая авторизация и сохранение результатов.
   ```

## 🌐 Развертывание Web App

### Для разработки (localhost):

1. Запустите backend:
   ```bash
   cd backend
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

2. Запустите frontend:
   ```bash
   cd frontend
   npm run dev
   ```

3. Используйте ngrok для туннелирования:
   ```bash
   ngrok http 3000
   ```

4. Установите Web App URL в BotFather:
   ```
   /setmenubutton
   @your_bot_username
   https://your-ngrok-url.ngrok.io
   🎮 Начать игру
   ```

### Для продакшена:

1. Разверните на VPS или облачном сервисе
2. Настройте домен и SSL сертификат
3. Обновите URL в BotFather

## 🔐 Безопасность

### Проверка Web App URL:

1. Убедитесь, что ваш домен добавлен в список разрешенных в BotFather
2. Используйте HTTPS для продакшена
3. Настройте CORS в backend для Telegram доменов

### Переменные окружения:

```env
# Backend
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_WEBAPP_URL=https://your-domain.com
TELEGRAM_AUTH_TIMEOUT=86400

# Frontend
VITE_TELEGRAM_BOT_USERNAME=your_bot_username
VITE_API_BASE_URL=https://your-domain.com/api
```

## 🧪 Тестирование

### 1. Тест бота:

```bash
cd tg_bot
python bot.py
```

### 2. Тест Web App:

1. Отправьте `/start` боту
2. Нажмите кнопку "🎮 Начать игру"
3. Проверьте авторизацию в Web App
4. Протестируйте игру

### 3. Тест API:

```bash
# Тест валидации
curl -X POST "http://localhost:8000/telegram/validate" \
  -H "Content-Type: application/json" \
  -d '{"init_data": "test_data"}'

# Тест авторизации
curl -X POST "http://localhost:8000/telegram/auth" \
  -H "Content-Type: application/json" \
  -d '{"init_data": "test_data"}'
```

## 📱 Особенности Web App

### Автоматическая авторизация:

- Пользователь автоматически авторизуется через Telegram
- Данные передаются в `initData`
- Backend валидирует подпись и создает пользователя

### UI адаптация:

- Используйте цвета Telegram темы
- Адаптируйте под размер окна
- Используйте Telegram UI элементы

### Обработка ошибок:

- Graceful fallback при недоступности Telegram
- Понятные сообщения об ошибках
- Логирование для отладки

## 🚨 Устранение неполадок

### Бот не отвечает:

1. Проверьте токен в `.env`
2. Убедитесь, что бот не заблокирован
3. Проверьте логи на ошибки

### Web App не открывается:

1. Проверьте URL в BotFather
2. Убедитесь, что сайт доступен
3. Проверьте SSL сертификат

### Ошибки авторизации:

1. Проверьте `TELEGRAM_BOT_TOKEN` в backend
2. Убедитесь, что токены совпадают
3. Проверьте время на сервере

### Проблемы с CORS:

1. Добавьте Telegram домены в CORS_ORIGINS
2. Проверьте настройки в `backend/core/config.py`
3. Убедитесь, что frontend доступен по HTTPS

## 📞 Поддержка

При возникновении проблем:

1. Проверьте логи бота и backend
2. Убедитесь в правильности настроек
3. Протестируйте каждый компонент отдельно
4. Обратитесь к документации Telegram Bot API