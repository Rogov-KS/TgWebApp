# План разработки бэкенда для Telegram Snake Web App

## Текущее состояние
- ✅ Базовая структура FastAPI приложения
- ❌ Настройка CORS для Telegram доменов
- ✅ Заготовки эндпоинтов (auth, game, telegram)
- ✅ Настройка линтеров и форматирования
- ❌ Модели данных и схемы
- ❌ Валидация Telegram Web App
- ❌ База данных и миграции
- ❌ JWT авторизация
- ❌ API для сохранения результатов

---

## 1. Анализ требований от фронтенда

### 1.1. Данные, которые отправляет фронтенд
Из анализа кода фронтенда видно, что нужно обрабатывать:

**При завершении игры:**
- Финальный счет (score: number)
- ID уровня (level: string) - level-1, level-2, etc.
- Скорость игры (gameSpeed: number) в мс
- Данные пользователя из Telegram Web App (initData: string)

**Для таблицы лидеров:**
- Получение топ-10 результатов
- Фильтрация по уровню
- Информация о пользователе (имя, аватар)

### 1.2. Интеграция с Telegram Web App
- Валидация `initData` от Telegram
- Извлечение данных пользователя (id, first_name, username, photo_url)
- Автоматическая авторизация через Telegram

---

## 2. Архитектура бэкенда

### 2.1. Структура базы данных
**Таблица users:**
- id (SERIAL PRIMARY KEY)
- telegram_id (BIGINT UNIQUE NOT NULL)
- username (VARCHAR(255))
- first_name (VARCHAR(255))
- last_name (VARCHAR(255))
- photo_url (TEXT)
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)

**Таблица game_scores:**
- id (SERIAL PRIMARY KEY)
- user_id (INTEGER REFERENCES users(id))
- score (INTEGER NOT NULL)
- level_id (VARCHAR(50) NOT NULL)
- game_speed (INTEGER)
- game_duration (INTEGER)
- created_at (TIMESTAMP)

**Индексы для производительности:**
- idx_game_scores_user_id
- idx_game_scores_level_id
- idx_game_scores_score (DESC)
- idx_game_scores_created_at (DESC)

### 2.2. Модели SQLAlchemy
- User (backend/models/user.py)
- GameScore (backend/models/game_score.py)

### 2.3. Pydantic схемы
- UserBase, UserCreate, UserResponse (backend/schemas/user.py)
- GameScoreCreate, GameScoreResponse, LeaderboardResponse (backend/schemas/game.py)
- TelegramInitData (backend/schemas/telegram.py)

---

## 3. Основные компоненты

### 3.1. Валидация Telegram Web App
**Файл: backend/core/telegram.py**
- Функция validate_telegram_init_data() - проверка подписи данных
- Функция extract_user_data() - извлечение данных пользователя
- Алгоритм валидации согласно документации Telegram

### 3.2. JWT авторизация
**Файл: backend/core/security.py**
- Функция create_access_token() - создание JWT токенов
- Функция verify_token() - проверка JWT токенов
- Настройка времени жизни токенов

### 3.3. Зависимости (Dependencies)
**Файл: backend/deps.py**
- Функция get_current_user() - получение текущего пользователя
- HTTPBearer для аутентификации
- Обработка ошибок авторизации

---

## 4. API эндпоинты

### 4.1. Авторизация (/api/v1/auth)
- POST /telegram - авторизация через Telegram Web App
- GET /me - получение информации о текущем пользователе

### 4.2. Игровые результаты (/api/v1/game)
- POST /score - сохранение результата игры
- GET /leaderboard - получение таблицы лидеров
- GET /user/scores - получение результатов конкретного пользователя

### 4.3. Telegram интеграция (/api/v1/telegram)
- POST /validate - валидация данных от Telegram Web App

---

## 5. База данных

### 5.1. Настройка подключения
**Файл: app/db/session.py**
- Создание engine для подключения к PostgreSQL
- Функция get_session() для dependency injection
- Настройка пула соединений

### 5.2. Миграции с Alembic
- Инициализация Alembic
- Создание начальной миграции
- Настройка автоматических миграций

---

## 6. Настройка CORS

### 6.1. Telegram домены
Добавить в ALLOWED_HOSTS:
- https://web.telegram.org
- https://t.me
- https://telegram.me
- Локальные домены для разработки

### 6.2. Настройка middleware
- Обновить CORS middleware в main.py
- Настроить credentials и методы
- Добавить заголовки для Telegram Web App

---

## 7. Тестирование

### 7.1. Unit тесты
- tests/test_telegram.py - тесты валидации Telegram
- tests/test_auth.py - тесты авторизации
- tests/test_game.py - тесты игровой логики

### 7.2. Интеграционные тесты
- tests/test_api.py - полный цикл API
- Тесты с реальной базой данных

---

## 8. Безопасность

### 8.1. Валидация данных
- Проверка initData от Telegram
- Валидация JWT токенов
- Rate limiting для API
- CORS настройки для Telegram доменов

### 8.2. Обработка ошибок
- Кастомные исключения
- Логирование ошибок
- Безопасные сообщения об ошибках

---

## 9. Мониторинг и логирование

### 9.1. Логирование
- Настройка базового логирования
- Логирование запросов и ответов
- Логирование ошибок

### 9.2. Метрики
- Количество игр в день
- Средний счет по уровням
- Популярные уровни
- Активные пользователи

---

## 10. Деплой

### 10.1. Docker
- Dockerfile для Python приложения
- Многоэтапная сборка
- Оптимизация размера образа

### 10.2. Docker Compose
- PostgreSQL контейнер
- Backend контейнер
- Настройка переменных окружения
- Volumes для данных

---

## 11. Следующие шаги (приоритет)

### Высокий приоритет:
1. Настроить CORS для Telegram доменов
2. Создать модели данных (User, GameScore)
3. Реализовать валидацию Telegram initData
4. Настроить подключение к базе данных
5. Создать JWT авторизацию
6. Реализовать эндпоинт /auth/telegram
7. Реализовать эндпоинт /game/score
8. Реализовать эндпоинт /game/leaderboard

### Средний приоритет:
9. Добавить тесты
10. Настроить миграции
11. Добавить обработку ошибок
12. Настроить логирование

### Низкий приоритет:
13. Добавить метрики
14. Настроить Docker
15. Настроить CI/CD
16. Добавить документацию API

---

## 12. Интеграция с фронтендом

### 12.1. Обновление фронтенда
Фронтенд нужно обновить для:
- Отправки initData при авторизации
- Сохранения результатов через API
- Отображения таблицы лидеров
- Обработки JWT токенов

### 12.2. API клиент
- Создать класс ApiClient
- Методы для авторизации, сохранения результатов, получения лидерборда
- Обработка ошибок и токенов

---

## 13. Переменные окружения

### 13.1. Обязательные переменные
- TELEGRAM_BOT_TOKEN - токен бота от @BotFather
- SECRET_KEY - секретный ключ для JWT
- DATABASE_URL - URL подключения к PostgreSQL

### 13.2. Опциональные переменные
- DEBUG - режим отладки
- ACCESS_TOKEN_EXPIRE_MINUTES - время жизни токенов
- REDIS_URL - URL для Redis (если понадобится)

---

## 14. Структура файлов

```
backend/
├── main.py              # Точка входа FastAPI
├── core/
│   ├── config.py        # Настройки приложения
│   ├── database.py      # Подключение к БД
│   ├── security.py      # JWT авторизация
│   └── telegram.py      # Валидация Telegram
├── api/
│   ├── router.py        # Главный роутер
│   └── endpoints/
│       ├── auth.py      # Авторизация
│       ├── game.py      # Игровая логика
│       └── telegram.py  # Telegram интеграция
├── models/
│   ├── user.py          # Модель пользователя
│   └── game_score.py    # Модель результатов
├── schemas/
│   ├── user.py          # Схемы пользователя
│   ├── game.py          # Схемы игры
│   └── telegram.py      # Схемы Telegram
├── crud/
│   ├── user.py          # CRUD операции для пользователей
│   └── game_score.py    # CRUD операции для результатов
├── deps.py              # Зависимости
└── utils/               # Утилиты
```

---

## 15. Критические моменты

### 15.1. Валидация Telegram
- Критически важно правильно реализовать валидацию initData
- Следовать официальной документации Telegram
- Тестировать с реальными данными от Telegram

### 15.2. Безопасность
- Никогда не хранить токен бота в коде
- Использовать HTTPS в продакшене
- Валидировать все входящие данные

### 15.3. Производительность
- Индексы в базе данных для быстрых запросов
- Пагинация для больших списков
- Кэширование популярных запросов
