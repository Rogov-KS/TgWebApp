# Анализ ошибки SQLAlchemy - Минимальный пример

## Проблема

Ошибка: `sqlalchemy.exc.InvalidRequestError: When initializing mapper Mapper[User(users)], expression 'OAuth2Token' failed to locate a name ('OAuth2Token')`

## Важное замечание

После попыток воспроизвести ошибку в минимальном примере, выяснилось, что **проблема НЕ в циклической зависимости SQLAlchemy**.

Современные версии SQLAlchemy (2.0+) корректно обрабатывают циклические зависимости при использовании:
- Строковых имен в relationship()
- TYPE_CHECKING для импортов
- Правильного порядка импорта моделей

## Реальная причина ошибки

Скорее всего, проблема в одном из следующих факторов:

### 1. Отсутствующие зависимости
```
ModuleNotFoundError: No module named 'fastapi_versioning'
```

### 2. Неправильный порядок импорта в проекте
- Модели импортируются до полной инициализации SQLAlchemy
- Отсутствует импорт всех моделей в assemblers/models.py

### 3. Проблемы с конфигурацией
- Неправильные переменные окружения
- Проблемы с подключением к базе данных

## Файлы в примере

### Демонстрационные файлы:
- `cyclic_dependency_example.py` - базовый пример (не воспроизводит ошибку)
- `proper_cyclic_example.py` - расширенный пример (не воспроизводит ошибку)
- `solution_models.py` - правильное решение

### Тестовые файлы:
- `test_fix.py` - тест для проверки исправления

## Решения для вашего проекта

### 1. Установить отсутствующие зависимости
```bash
pip install fastapi-versioning
```

### 2. Проверить порядок импорта в assemblers/models.py
```python
# Правильный порядок
from backend.entities.user.models import User
from backend.entities.game_session.models import GameSession
from backend.entities.refresh_token.models import RefreshToken
from backend.ows.auth.models import OAuth2Token
```

### 3. Убедиться, что все модели импортируются
В `backend/core/database.py` или `backend/main.py`:
```python
# Импорт всех моделей для правильной инициализации
import backend.entities.assemblers.models  # noqa: F401
```

## Диагностика

Для точной диагностики проблемы нужно:

1. Показать полный стек ошибки
2. Проверить все зависимости проекта
3. Убедиться в правильности конфигурации
4. Проверить порядок импорта моделей

## Вывод

Циклическая зависимость в SQLAlchemy - это не проблема в современных версиях.
Реальная причина ошибки лежит в других аспектах проекта.
