# Тесты для GameSessionDAO

## Описание

Этот модуль содержит unit-тесты для `GameSessionDAO` - класса для работы с игровыми сессиями в базе данных.

## Структура тестов

### TestGameSessionDAO

Основной класс тестов, который включает в себя:

#### TestCreate
- `test_create_game_session_success` - тест успешного создания игровой сессии
- `test_create_game_session_minimal_data` - тест создания с минимальными данными

#### TestGetOneOrNone
- `test_get_game_session_by_id_success` - тест получения сессии по ID
- `test_get_game_session_by_id_not_found` - тест получения несуществующей сессии
- `test_get_game_session_by_user_id` - тест получения сессии по user_id

#### TestGetAll
- `test_get_all_game_sessions` - тест получения всех сессий
- `test_get_game_sessions_by_user_id` - тест получения сессий пользователя
- `test_get_completed_game_sessions` - тест получения завершенных сессий

#### TestUpdate
- `test_update_game_session_success` - тест успешного обновления
- `test_update_game_session_not_found` - тест обновления несуществующей сессии
- `test_update_game_session_empty_filters` - тест с пустыми фильтрами
- `test_update_game_session_empty_data` - тест с пустыми данными

#### TestDelete
- `test_delete_game_session_success` - тест успешного удаления
- `test_delete_game_session_not_found` - тест удаления несуществующей сессии

#### TestGetMaxScore
- `test_get_user_max_score_success` - тест получения максимального счета
- `test_get_user_max_score_user_with_no_sessions` - тест для пользователя без сессий
- `test_get_user_max_score_invalid_user_id_zero` - тест с user_id = 0
- `test_get_user_max_score_invalid_user_id_negative` - тест с отрицательным user_id
- `test_get_user_max_score_invalid_user_id_type` - тест с неправильным типом user_id
- `test_get_user_max_score_multiple_users` - тест для нескольких пользователей

## Запуск тестов

```bash
# Запуск всех тестов GameSessionDAO
python -m pytest tests/backend/unit/entities/game_session/test_dao.py -v

# Запуск конкретного теста
python -m pytest tests/backend/unit/entities/game_session/test_dao.py::TestGameSessionDAO::TestCreate::test_create_game_session_success -v

# Запуск с покрытием
python -m pytest tests/backend/unit/entities/game_session/test_dao.py --cov=backend.entities.game_session.dao --cov-report=html
```

## Фикстуры

Тесты используют следующие фикстуры:
- `get_async_test_db_session` - сессия базы данных
- `dao` - экземпляр GameSessionDAO
- `test_user` - тестовый пользователь
- `test_users` - несколько тестовых пользователей
- `test_game_session` - тестовая игровая сессия
- `test_game_sessions` - несколько тестовых игровых сессий
- `game_session_data` - данные для создания сессии
- `multiple_game_sessions_data` - данные для нескольких сессий

## Покрытие

Тесты покрывают:
- ✅ Все базовые методы CRUD (create, read, update, delete)
- ✅ Специфичный метод `get_user_max_score`
- ✅ Валидацию входных данных
- ✅ Обработку ошибок
- ✅ Граничные случаи
- ✅ Различные сценарии использования
