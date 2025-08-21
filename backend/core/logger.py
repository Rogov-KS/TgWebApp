from datetime import UTC, datetime
import logging
from pathlib import Path

from pythonjsonlogger.json import JsonFormatter

from backend.core.config import settings


class CustomJsonFormatter(JsonFormatter):
    """Форматтер для логирования в формате JSON"""

    def add_fields(
        self,
        log_record: dict,
        record: logging.LogRecord,
        message_dict: dict,
    ) -> None:
        super().add_fields(log_record, record, message_dict)
        if not log_record.get("timestamp"):
            now = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            log_record["timestamp"] = now
        if log_record.get("level"):
            log_record["level"] = log_record["level"].upper()
        else:
            log_record["level"] = record.levelname


formatter = CustomJsonFormatter(
    "%(timestamp)s %(level)s %(message)s %(module)s %(funcName)s"
)

logger = logging.getLogger()

logHandler = logging.StreamHandler()

logHandler.setFormatter(formatter)
logger.addHandler(logHandler)
logger.setLevel(settings.LOG_LEVEL)


def setup_logging() -> None:
    """Настройка базовой конфигурации логирования с использованием
    python-json-logger"""
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    # Создаем форматтер для JSON логов
    json_formatter = CustomJsonFormatter(
        "%(timestamp)s %(message)s %(level)s %(name)s "
        "%(module)s %(funcName)s %(lineno)d"
    )

    # Настраиваем корневой логгер
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.LOG_LEVEL))

    # Очищаем существующие обработчики
    root_logger.handlers.clear()

    # Создаем обработчик для файла
    log_file_path = f"{logs_dir}/app_log.json"
    file_handler = logging.FileHandler(log_file_path, encoding="utf-8")
    file_handler.setFormatter(json_formatter)
    file_handler.setLevel(getattr(logging, settings.LOG_LEVEL))

    # Создаем обработчик для консоли
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(json_formatter)
    console_handler.setLevel(getattr(logging, settings.LOG_LEVEL))

    # Добавляем обработчики к корневому логгеру
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)


def get_logger(name: str) -> logging.Logger:
    """Получение логгера с указанным именем"""
    return logging.getLogger(name)
