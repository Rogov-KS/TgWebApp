# План разработки Telegram Mini-App "Snake"

## 0. Предпосылки
- Цель: реализовать мини-игру «Змейка», запускаемую внутри Telegram через кнопку `web_app` бота.
- Основные технологии:
  - **Фронтенд**: React JS, Telegram Web Apps SDK, TypeScript *(опционально)*, Vite, ESLint + Prettier.
  - **Бэкенд**: FastAPI + Python 3.11, Uvicorn, Postgres *(в перспективе)*, SQLModel/SQLAlchemy, Docker Compose.
  - CI/CD: GitHub Actions, Docker Hub/Fly.io.

---

## 1. Общая дорожная карта
1. Сбор требований и дизайн UX/UI.
2. Подготовка репозитория, базовой структуры каталогов, linters/formatters.
3. Настройка окружений (Miniconda/Mamba, env `tg_web_app` + uv, npm, pre-commit).
4. Реализация минимального вертикального среза:
   - пустой React-SPA, отдаваемый FastAPI (или nginx).
   - базовый эндпоинт `/health` на бэкенде.
5. Подключение Telegram Web Apps SDK, проверка хеш-подписи.
6. Разработка логики игры Snake на фронте.
7. Создание API для хранения результатов и JWT-авторизации.
8. Интеграция фронта с бэком.
9. Тестирование (unit + e2e).
10. Деплой и публикация.

---

## 2. План фронтенда (React)

### 2.1. Инициализация проекта
- `npm create vite@latest frontend -- --template react`  *(или CRA)*.
- Установка зависимостей: `telegram-web-app`, `react-router-dom`, `zustand`/`redux`, `axios`, `classnames`.
- Настройка ESLint, Prettier, Husky, lint-staged.

### 2.2. Архитектура фронта
- `src/
  ├─ assets/
  ├─ components/
  ├─ pages/
  ├─ hooks/
  ├─ services/ (API)
  └─ styles/`
- Использовать CSS-Modules или styled-components.
- Роутинг: `/` (главное меню), `/play` (игровое поле), `/scoreboard`.
- Хранилище состояния: выбор лёгкого решения (zustand, context, redux-toolkit).

### 2.3. Игровая логика
- Canvas-компонент `SnakeBoard` с `requestAnimationFrame`.
- Управление через onKeyDown / свайпы Telegram.
- Подсчёт очков, скорость игры, коллизии.

### 2.4. Интеграция с Telegram Web Apps SDK
- Инициализация объекта `window.Telegram.WebApp`.
- Отправка `WebApp.initData` на бэкенд для валидации.
- Использование кнопок MainButton и BackButton.

### 2.5. API-слой
- Модуль `services/api.ts` с axios-инстансом, авторизация через Bearer JWT.
- Методы: `POST /auth/telegram`, `POST /score`, `GET /score/top`.

### 2.6. Тесты и качество
- React Testing Library + Vitest/Jest.
- E2E: Playwright.

---

## 3. План бэкенда (FastAPI)

### 3.1. Инициализация
- Установить Miniconda/Mamba.
- Создать окружение `conda create -n tg_snake_web_app python=3.11 -y`.
- Активировать `conda activate tg_snake_web_app`.
- Установить **uv** для быстрой установки пакетов: `pip install uv`.
- Установка зависимостей Python через uv:
  ```bash
  uv pip install fastapi uvicorn[standard] sqlmodel python-telegram-bot("~=21.0") python-jose[cryptography] pytest ruff black mypy isort
  ```
- Добавить `alembic` для миграций (при выборе Postgres).

### 3.2. Структура пакета `backend/app`
```
app/
 ├─ main.py          # точка входа, FastAPI instance
 ├─ deps.py          # зависимости (Depends)
 ├─ core/
 │   ├─ config.py    # Pydantic-настройки
 │   └─ security.py  # JWT utils, проверка Telegram hash
 ├─ api/
 │   ├─ v1/
 │   │   ├─ endpoints/
 │   │   │   ├─ auth.py
 │   │   │   └─ scores.py
 │   │   └─ __init__.py
 │   └─ __init__.py
 ├─ models.py        # SQLModel сущности
 └─ schemas.py       # Pydantic-схемы
```

### 3.3. Основные задачи
1. **Хеш-валидация Telegram**: реализовать алгоритм проверки `initData`.
2. **Авторизация**: `POST /auth/telegram` возвращает `access_token`, создает/находит пользователя.
3. **Сущность Score**:
   - `score: int`, `user_id: int`, `created_at`.
   - `POST /score` сохраняет результат.
   - `GET /score/top?limit=10` выдаёт таблицу лидеров.
4. **CORS & HTTPS**: настройка CORS для домена `https://t.me/…`.
5. **OpenAPI & документация**: скрыть приватные эндпоинты.
6. **Тесты**: PyTest, coverage > 90 %.

### 3.4. Запуск и деплой
- Локально: `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`.
- Dockerfile + Docker Compose (Postgres, backend, nginx/static или фронт).

---

## 4. Инфраструктура и CI/CD
1. `.gitignore`, `pre-commit` (black, isort, flake8).
2. GitHub Actions:
   - lint + test на push.
   - build Docker images, push to registry.
3. Деплой на Fly.io или Railway:
   - отдельные сервисы `web` (backend) и `static` (frontend build).
4. Мониторинг и логирование: Sentry, Grafana Loki.

---

## 5. Линтеры и форматирование

| Язык | Инструмент | Назначение |
|------|------------|------------|
| Python | **ruff** | статический анализ, style & autofix (замена flake8/isort) |
|  | **black** | автоформатирование кода |
|  | **mypy** | проверка типов |
|  | **isort** | сортировка импортов (если не пользоваться встроенным в ruff) |
| JavaScript/TypeScript | **ESLint** | Lint JS/TS, правила Airbnb + React |
|  | **Prettier** | форматирование кода, интеграция с ESLint через `eslint-config-prettier` |
|  | **Stylelint** | проверка CSS/SCSS или styled-components |

### Pre-commit интеграция
- Файл `.pre-commit-config.yaml` (Python инструменты) + hook `prettier` для фронта.
- Установка: `pre-commit install` в активированном conda-окружении.
- Для фронтенда Husky/lint-staged запускает `npm run lint` и `npm run format`.

Содержимое `.pre-commit-config.yaml` (минимально):
```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.4.6
    hooks:
      - id: ruff
  - repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
      - id: black
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: end-of-file-fixer
      - id: check-added-large-files
  - repo: local
    hooks:
      - id: prettier
        name: prettier frontend
        entry: npm run format
        language: system
        types: [javascript, typescript, json, yaml, css, scss]
```

---

## 6. Распределение по спринтам
| Спринт | Задачи |
|--------|--------|
| 1 (0-1 неделя) | Анализ требований, прототип UI, инициализация репо, структура каталогов. |
| 2 | Поднять FastAPI, `/health`, интеграция Telegram hash, базовый React с SDK. |
| 3 | Реализовать игру Snake локально без бэка, добавить таблицу результатов в памяти. |
| 4 | Подключить БД, создать модели, эндпоинты auth/score. |
| 5 | Интеграция фронта с API, JWT, отладка. |
| 6 | Тесты, CI/CD, Docker, деплой staging. |
| 7 | Полировка UI/UX, анимации, международзация. |
| 8 | Продовый релиз, маркетинг, поддержка. |

---

## 7. Следующие шаги (to-do)
- [ ] Инициализировать Vite + React в `frontend/`.
- [ ] Добавить базовый `main.py` FastAPI с `/health` и Dockerfile.
- [ ] Настроить pre-commit и GitHub Actions.
- [ ] Реализовать валидацию `initData` Telegram.
- [ ] Начать разработку SnakeBoard компонента.
