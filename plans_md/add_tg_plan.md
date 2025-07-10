# План интеграции Telegram Mini App

## Обзор
Данный план описывает все необходимые изменения для полноценной интеграции с Telegram Mini App, включая валидацию данных от Telegram, автоматическую авторизацию и адаптацию UI под Telegram Web App.

---

## 1. Backend изменения

### 1.1. Валидация Telegram Web App данных

#### Новые утилиты (backend/utils/telegram.py)
- **validate_telegram_init_data()** - проверка HMAC-SHA256 подписи initData
- **extract_user_data()** - парсинг данных пользователя из initData
- **validate_auth_date()** - проверка времени авторизации (не старше 24 часов)
- **create_telegram_hash()** - создание хеша для проверки подлинности

#### Алгоритм валидации:
1. Разбор initData на параметры
2. Сортировка параметров по алфавиту
3. Создание строки для хеширования
4. Проверка HMAC-SHA256 подписи с использованием Bot Token
5. Извлечение данных пользователя (id, first_name, username, photo_url)

### 1.2. Новые API эндпоинты

#### Telegram авторизация (backend/api/endpoints/telegram.py)
- **POST /auth/telegram** - авторизация через Telegram Web App
  - Принимает initData от фронтенда
  - Валидирует данные через validate_telegram_init_data()
  - Создает/обновляет пользователя в БД
  - Возвращает JWT токен для авторизации

- **POST /telegram/validate** - валидация данных от Telegram
  - Проверяет подлинность initData
  - Возвращает статус валидации и данные пользователя

- **GET /telegram/user** - получение данных пользователя из Telegram
  - Возвращает информацию о текущем пользователе Telegram

### 1.3. Обновление существующих моделей

#### Модель User (backend/models/user.py)
- Добавить поле `photo_url` (TEXT, nullable)
- Добавить поле `language_code` (VARCHAR(10), nullable)
- Добавить поле `is_premium` (BOOLEAN, default=False)
- Добавить поле `telegram_username` (VARCHAR(255), nullable)

#### Модель TelegramWebAppData (backend/models/telegram_webapp_data.py)
- Добавить поле `user_data` (JSON, nullable) - данные пользователя из Telegram
- Добавить поле `chat_data` (JSON, nullable) - данные чата
- Добавить поле `start_param` (VARCHAR(255), nullable) - параметр запуска

### 1.4. Новые схемы данных

#### Telegram схемы (backend/schemas/telegram.py)
- **TelegramInitData** - схема для валидации initData
- **TelegramUserData** - схема данных пользователя Telegram
- **TelegramAuthRequest** - схема запроса авторизации
- **TelegramAuthResponse** - схема ответа авторизации

### 1.5. Обновление конфигурации

#### Настройки (backend/core/config.py)
- Добавить `TELEGRAM_BOT_TOKEN` - токен бота для валидации
- Добавить `TELEGRAM_WEBAPP_URL` - URL Web App в Telegram
- Добавить `TELEGRAM_AUTH_TIMEOUT` - таймаут валидации (24 часа)

#### CORS настройки
- Добавить Telegram домены в CORS_ORIGINS:
  - https://web.telegram.org
  - https://t.me
  - https://telegram.me

### 1.6. Новые исключения

#### Исключения (backend/core/exception.py)
- **InvalidTelegramDataException** - неверные данные от Telegram
- **TelegramAuthExpiredException** - истекло время авторизации
- **TelegramValidationException** - ошибка валидации подписи

---

## 2. Frontend изменения

### 2.1. Интеграция Telegram Web App SDK

#### Инициализация (frontend/src/utils/telegram.ts)
- **initializeTelegramWebApp()** - инициализация Web App
- **getTelegramUser()** - получение данных пользователя
- **validateInitData()** - валидация initData на фронтенде
- **setupTelegramUI()** - настройка UI элементов Telegram

#### Telegram Web App API методы:
- `WebApp.initData` - получение данных инициализации
- `WebApp.initDataUnsafe` - получение небезопасных данных
- `WebApp.user` - данные пользователя
- `WebApp.themeParams` - параметры темы
- `WebApp.viewportHeight` - высота viewport

### 2.2. Обновление AuthContext

#### Модификация (frontend/src/contexts/AuthContext.tsx)
- Добавить метод `loginWithTelegram()` - авторизация через Telegram
- Добавить состояние `isTelegramAvailable` - доступность Telegram Web App
- Добавить метод `checkTelegramAuth()` - проверка авторизации через Telegram
- Обновить `checkAuth()` для поддержки Telegram авторизации

#### Новые типы (frontend/src/types/telegram.ts)
- **TelegramUser** - тип пользователя Telegram
- **TelegramInitData** - тип данных инициализации
- **TelegramThemeParams** - тип параметров темы

### 2.3. Адаптация UI под Telegram

#### Компоненты Telegram UI (frontend/src/components/Telegram/)
- **TelegramMainButton** - кнопка "Начать игру" в Telegram
- **TelegramBackButton** - кнопка возврата в чат
- **TelegramThemeProvider** - провайдер темы Telegram
- **TelegramViewport** - адаптация под размер окна Telegram

#### Адаптация существующих компонентов:
- **Game.tsx** - использование цветов Telegram темы
- **AuthModal.tsx** - поддержка автоматической авторизации
- **App.tsx** - инициализация Telegram Web App

### 2.4. Новые хуки

#### Telegram хуки (frontend/src/hooks/useTelegram.ts)
- **useTelegramWebApp()** - доступ к Telegram Web App API
- **useTelegramTheme()** - использование темы Telegram
- **useTelegramUser()** - получение данных пользователя
- **useTelegramAuth()** - авторизация через Telegram

### 2.5. Обновление API клиента

#### Модификация (frontend/src/api/client.ts)
- Добавить метод `telegramAuth()` - авторизация через Telegram
- Добавить метод `validateTelegramData()` - валидация данных
- Обновить обработку ошибок для Telegram-специфичных ошибок
- Добавить автоматическую отправку initData в заголовках

---

## 3. Миграции базы данных

### 3.1. Обновление таблицы users
```sql
-- Добавление Telegram-специфичных полей
ALTER TABLE users ADD COLUMN photo_url TEXT;
ALTER TABLE users ADD COLUMN language_code VARCHAR(10);
ALTER TABLE users ADD COLUMN is_premium BOOLEAN DEFAULT FALSE;
ALTER TABLE users ADD COLUMN telegram_username VARCHAR(255);

-- Индексы для производительности
CREATE INDEX idx_users_telegram_id ON users(telegram_id);
CREATE INDEX idx_users_telegram_username ON users(telegram_username);
```

### 3.2. Обновление таблицы telegram_webapp_data
```sql
-- Добавление новых полей
ALTER TABLE telegram_webapp_data ADD COLUMN user_data JSONB;
ALTER TABLE telegram_webapp_data ADD COLUMN chat_data JSONB;
ALTER TABLE telegram_webapp_data ADD COLUMN start_param VARCHAR(255);

-- Индексы для JSON полей
CREATE INDEX idx_telegram_webapp_data_user_data ON telegram_webapp_data USING GIN(user_data);
CREATE INDEX idx_telegram_webapp_data_chat_data ON telegram_webapp_data USING GIN(chat_data);
```

---

## 4. Конфигурация и переменные окружения

### 4.1. Backend переменные (.env)
```
# Telegram Bot настройки
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_WEBAPP_URL=https://your-domain.com
TELEGRAM_AUTH_TIMEOUT=86400

# CORS для Telegram
CORS_ORIGINS=["http://localhost:3000","https://your-domain.com","https://web.telegram.org","https://t.me"]
```

### 4.2. Frontend переменные (.env)
```
# Telegram Web App настройки
VITE_TELEGRAM_BOT_USERNAME=your_bot_username
VITE_API_BASE_URL=http://localhost:8000
VITE_TELEGRAM_WEBAPP_URL=https://your-domain.com
```

---

## 5. Безопасность

### 5.1. Валидация данных
- **HMAC-SHA256 проверка** - криптографическая проверка подписи
- **Временная валидация** - проверка времени авторизации
- **Параметрическая валидация** - проверка всех обязательных параметров

### 5.2. Защита от атак
- **CSRF защита** - использование SameSite cookies
- **XSS защита** - валидация всех входящих данных
- **Rate limiting** - ограничение частоты запросов

### 5.3. Обработка ошибок
- **Graceful fallback** - работа без Telegram при ошибках
- **Логирование ошибок** - детальное логирование для отладки
- **Пользовательские уведомления** - понятные сообщения об ошибках

---

## 6. Тестирование

### 6.1. Backend тесты
- **Unit тесты валидации** - тестирование validate_telegram_init_data()
- **Интеграционные тесты** - полный цикл авторизации через Telegram
- **Тесты безопасности** - проверка защиты от подделки данных

### 6.2. Frontend тесты
- **Тесты интеграции** - проверка работы с Telegram Web App SDK
- **Fallback тесты** - проверка работы без Telegram
- **UI тесты** - проверка адаптации под темы Telegram

### 6.3. E2E тесты
- **Сценарии авторизации** - полный цикл через Telegram
- **Сценарии игры** - игра с сохранением результатов
- **Сценарии ошибок** - обработка различных ошибок

---

## 7. Документация

### 7.1. README обновления
- **Настройка Telegram Bot** - инструкции по созданию и настройке бота
- **Переменные окружения** - полный список необходимых переменных
- **Деплой** - инструкции по развертыванию с поддержкой Telegram

### 7.2. API документация
- **Telegram эндпоинты** - документация новых API методов
- **Схемы данных** - описание новых типов данных
- **Примеры использования** - примеры запросов и ответов

---

## 8. Дополнительные возможности

### 8.1. Интеграция с Bot API
- **Webhook обработка** - получение событий от Telegram Bot
- **Отправка уведомлений** - отправка результатов в чат
- **Инлайн кнопки** - кнопки для быстрого доступа к игре

### 8.2. Социальные функции
- **Поделиться результатом** - отправка результата в чат
- **Вызов друзей** - приглашение друзей поиграть
- **Рейтинг друзей** - сравнение результатов с друзьями

### 8.3. Персонализация
- **Использование аватара** - отображение фото профиля
- **Языковые настройки** - адаптация под язык пользователя
- **Премиум функции** - специальные возможности для Premium пользователей

---

## 9. План реализации

### Этап 1: Базовая интеграция (1-2 недели)
1. Реализация валидации Telegram данных на backend
2. Создание новых API эндпоинтов
3. Базовая интеграция Telegram Web App SDK на frontend
4. Миграции базы данных

### Этап 2: UI адаптация (1 неделя)
1. Адаптация компонентов под Telegram UI
2. Реализация автоматической авторизации
3. Настройка тем и цветов

### Этап 3: Тестирование и полировка (1 неделя)
1. Написание тестов
2. Обработка ошибок и edge cases
3. Оптимизация производительности

### Этап 4: Документация и деплой (3-5 дней)
1. Обновление документации
2. Настройка CI/CD
3. Деплой и мониторинг

---

## 10. Критические моменты

### 10.1. Безопасность
- **Критически важно** правильно реализовать валидацию HMAC-SHA256
- **Никогда не хранить** Bot Token в коде или публичных репозиториях
- **Всегда валидировать** все данные от Telegram

### 10.2. Производительность
- **Кэширование** результатов валидации
- **Оптимизация** запросов к базе данных
- **Lazy loading** компонентов Telegram

### 10.3. Пользовательский опыт
- **Graceful fallback** при недоступности Telegram
- **Быстрая загрузка** приложения
- **Понятные ошибки** для пользователей

---

## 11. Мониторинг и аналитика

### 11.1. Метрики для отслеживания
- **Количество авторизаций** через Telegram
- **Успешность валидации** данных
- **Время отклика** API
- **Ошибки валидации** и их причины

### 11.2. Логирование
- **Детальные логи** процесса валидации
- **Ошибки безопасности** с контекстом
- **Пользовательские действия** для аналитики

---

## 12. Заключение

Данный план обеспечивает полную интеграцию с Telegram Mini App, включая безопасную авторизацию, адаптацию UI и обработку ошибок. Реализация должна происходить поэтапно с тщательным тестированием каждого компонента.
