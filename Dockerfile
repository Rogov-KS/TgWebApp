FROM python:3.12-slim

# Устанавливаем uv
RUN pip install uv

# Создаем пользователя celery для безопасного запуска
RUN groupadd -r celery && useradd -r -g celery celery

RUN mkdir /app
WORKDIR /app

# Копируем файлы зависимостей
COPY pyproject.toml uv.lock README.md ./

# Устанавливаем зависимости с помощью uv
RUN uv pip install --system .

# Копируем остальной код
COPY . .

# Изменяем владельца файлов на пользователя celery
RUN chown -R celery:celery /app

# Переключаемся на пользователя celery
USER celery

CMD ["gunicorn", "backend.main:app", "--workers", "3", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind=0.0.0.0:8000"]
