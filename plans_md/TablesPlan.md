# План таблиц и CRUD методов для TgWebApp

## 1. Таблица `users` (Пользователи)

### Описание:
Основная таблица пользователей, содержащая информацию о пользователях Telegram.

### Поля:
- `id` (int, PK) - уникальный идентификатор
- `telegram_id` (int) - ID пользователя в Telegram
- `hashed_password` (str) - хешированный пароль
- `username` (str, nullable) - имя пользователя

- `first_name` (str) - имя
- `last_name` (str, nullable) - фамилия
- `language_code` (str, nullable) - код языка
- `is_bot` (bool) - является ли ботом
- `is_active` (bool) - активен ли пользователь
- `max_score` (int) - максимальный счет
- `created_at` (datetime) - дата создания
- `updated_at` (datetime, nullable) - дата обновления

### CRUD методы:
```python
# Аутентификация
POST /auth/register - регистрация нового пользователя
POST /auth/login - вход в систему
POST /auth/logout - выход из системы

# Управление пользователями
GET /users/ - получение списка всех пользователей
GET /users/{user_id} - получение информации о пользователе
PUT /users/{user_id} - обновление информации о пользователе
DELETE /users/{user_id} - удаление пользователя
GET /users/me - получение информации о текущем пользователе
```

---

## 2. Таблица `game_sessions` (Игровые сессии)

### Описание:
Хранит информацию о каждой игровой сессии пользователя.

### Поля:
- `id` (int, PK) - уникальный идентификатор сессии
- `user_id` (int, FK) - ID пользователя
- `game_type` (str) - тип игры ("snake", "tetris", etc.)
- `score` (int) - счет в игре
- `duration` (int) - продолжительность игры в секундах
- `level` (int) - уровень сложности
- `started_at` (datetime) - время начала игры
- `ended_at` (datetime, nullable) - время окончания игры
- `is_completed` (bool) - завершена ли игра
- `game_data` (JSON, nullable) - дополнительные данные игры

### CRUD методы:
```python
# Управление игровыми сессиями
POST /game-sessions/ - создание новой игровой сессии
GET /game-sessions/user/{user_id} - получение истории игр пользователя
GET /game-sessions/{session_id} - получение конкретной игровой сессии
PATCH /game-sessions/{session_id} - обновление сессии во время игры
PUT /game-sessions/{session_id}/complete - завершение игровой сессии
DELETE /game-sessions/{session_id} - удаление игровой сессии

# Специальные методы для игры в змейку
POST /game-sessions/snake/start - начало игры в змейку
PATCH /game-sessions/snake/{session_id}/update - обновление состояния игры
POST /game-sessions/snake/{session_id}/end - завершение игры в змейку
```

---

## 3. Таблица `game_settings` (Настройки игры)

### Описание:
Хранит персональные настройки игры для каждого пользователя.

### Поля:
- `id` (int, PK) - уникальный идентификатор
- `user_id` (int, FK) - ID пользователя
- `game_type` (str) - тип игры
- `difficulty` (str) - уровень сложности ("easy", "medium", "hard")
- `theme` (str) - тема оформления ("dark", "light", "colorful")
- `sound_enabled` (bool) - включен ли звук
- `vibration_enabled` (bool) - включена ли вибрация
- `controls` (JSON, nullable) - настройки управления

### CRUD методы:
```python
# Управление настройками игры
GET /game-settings/user/{user_id} - получение настроек пользователя
PUT /game-settings/user/{user_id} - создание/обновление настроек
DELETE /game-settings/user/{user_id} - сброс настроек к значениям по умолчанию
GET /game-settings/user/{user_id}/snake - получение настроек для змейки
PUT /game-settings/user/{user_id}/snake - обновление настроек змейки
```

---

## 4. Таблица `achievements` (Достижения)

### Описание:
Справочная таблица всех возможных достижений в игре.

### Поля:
- `id` (int, PK) - уникальный идентификатор
- `name` (str) - название достижения
- `description` (str) - описание достижения
- `icon` (str) - иконка достижения
- `condition_type` (str) - тип условия ("score", "games_count", "duration")
- `condition_value` (int) - значение для получения достижения
- `game_type` (str) - тип игры, к которому относится достижение

### CRUD методы:
```python
# Управление достижениями (только для администраторов)
GET /achievements/ - получение списка всех достижений
GET /achievements/{achievement_id} - получение информации о достижении
POST /achievements/ - создание нового достижения
PUT /achievements/{achievement_id} - обновление достижения
DELETE /achievements/{achievement_id} - удаление достижения
```

---

## 5. Таблица `user_achievements` (Достижения пользователей)

### Описание:
Связующая таблица между пользователями и их достижениями.

### Поля:
- `id` (int, PK) - уникальный идентификатор
- `user_id` (int, FK) - ID пользователя
- `achievement_id` (int, FK) - ID достижения
- `earned_at` (datetime) - дата получения достижения
- `is_new` (bool) - новое ли достижение (для уведомлений)

### CRUD методы:
```python
# Управление достижениями пользователей
GET /user-achievements/user/{user_id} - получение достижений пользователя
GET /user-achievements/user/{user_id}/new - получение новых достижений
PATCH /user-achievements/user/{user_id}/{achievement_id} - отметка как прочитанное
POST /user-achievements/user/{user_id}/check - проверка и выдача новых достижений
```

---

## 6. Таблица `telegram_webapp_data` (Данные Telegram WebApp)

### Описание:
Хранит данные, полученные от Telegram WebApp при инициализации.

### Поля:
- `id` (int, PK) - уникальный идентификатор
- `user_id` (int, FK) - ID пользователя
- `init_data` (str) - данные инициализации
- `user_data` (JSON, nullable) - данные пользователя из Telegram
- `chat_data` (JSON, nullable) - данные чата
- `start_param` (str, nullable) - параметр запуска
- `auth_date` (datetime) - дата авторизации
- `hash` (str) - хеш для проверки подлинности

### CRUD методы:
```python
# Управление данными Telegram WebApp
POST /telegram-webapp-data/ - сохранение данных инициализации
GET /telegram-webapp-data/user/{user_id} - получение данных пользователя
DELETE /telegram-webapp-data/user/{user_id} - удаление данных
```

---

## Дополнительные API методы

### Рейтинг (Leaderboard):
```python
# Рейтинг игроков
GET /leaderboard/snake - топ игроков по счету в змейке
GET /leaderboard/snake/duration - топ игроков по времени игры
GET /leaderboard/snake/user/{user_id}/position - позиция пользователя в рейтинге
GET /leaderboard/snake/weekly - недельный рейтинг
GET /leaderboard/snake/monthly - месячный рейтинг
```

### Статистика:
```python
# Статистика игр
GET /statistics/user/{user_id} - статистика пользователя
GET /statistics/global - общая статистика игры
GET /statistics/snake - статистика игры в змейку
GET /statistics/user/{user_id}/snake - статистика пользователя в змейке
```

### Игровые данные для змейки:
```python
# Специфичные для змейки методы
POST /snake/game/start - начало новой игры
PATCH /snake/game/{session_id}/move - обработка движения змейки
POST /snake/game/{session_id}/food - генерация новой еды
POST /snake/game/{session_id}/collision - обработка столкновений
GET /snake/game/{session_id}/state - получение текущего состояния игры
```

---

## Приоритеты реализации

### Высокий приоритет:
1. **Game Sessions CRUD** - основная функциональность для сохранения результатов игр
2. **Game Settings CRUD** - настройки пользователя
3. **Leaderboard API** - рейтинг игроков

### Средний приоритет:
4. **User Achievements CRUD** - система достижений
5. **Statistics API** - статистика игр

### Низкий приоритет:
6. **Achievements CRUD** - управление достижениями (для админов)
7. **Telegram WebApp Data CRUD** - дополнительные данные Telegram

---

## Особенности реализации

### Для игры в змейку клиент может отправлять:
- **При старте**: `game_type`, `level`, `difficulty`
- **Во время игры**: `score`, `duration`, `game_data` (позиция змейки, еда, препятствия)
- **При завершении**: `final_score`, `duration`, `is_completed`, `game_data` (статистика)

### Автоматические действия:
- Проверка и выдача достижений при достижении определенных условий
- Обновление `max_score` пользователя при новом рекорде
- Расчет позиции в рейтинге при завершении игры
