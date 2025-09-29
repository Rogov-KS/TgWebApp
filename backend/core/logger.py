from datetime import datetime, timezone
import json
import logging
from pathlib import Path
from typing import Any, Dict

from pythonjsonlogger.json import JsonFormatter

from backend.core.config import settings


class CustomJsonFormatter(JsonFormatter):
    """Форматтер для логирования в формате JSON"""

    def add_fields(
        self,
        log_record: Dict[str, Any],
        record: logging.LogRecord,
        message_dict: Dict[str, Any],
    ) -> None:
        super().add_fields(log_record, record, message_dict)
        if not log_record.get("timestamp"):
            now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            log_record["timestamp"] = now
        if log_record.get("level"):
            log_record["level"] = log_record["level"].upper()
        else:
            log_record["level"] = record.levelname

        # Переименовываем ключ "message" в "MESSAGE"
        if "message" in log_record:
            log_record["MESSAGE"] = log_record.pop("message")


class PrettyJsonFormatter(CustomJsonFormatter):
    """Форматтер для красивого вывода JSON в консоль с отступами"""

    def format(self, record: logging.LogRecord) -> str:
        """Форматирует лог-запись в красивый JSON с отступами"""
        # Получаем JSON строку от родительского класса
        json_str = super().format(record)

        try:
            # Парсим JSON и форматируем с отступами
            json_obj = json.loads(json_str)
            return json.dumps(
                json_obj, indent=2, ensure_ascii=False
            )
        except (json.JSONDecodeError, TypeError):
            # Если не удалось распарсить как JSON,
            # возвращаем оригинальную строку
            return json_str


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

    # Создаем обработчик для консоли с красивым форматированием
    console_handler = logging.StreamHandler()
    pretty_formatter = PrettyJsonFormatter(
        "%(timestamp)s %(message)s %(level)s %(name)s "
        "%(module)s %(funcName)s %(lineno)d"
    )
    console_handler.setFormatter(pretty_formatter)
    console_handler.setLevel(getattr(logging, settings.LOG_LEVEL))

    # Добавляем обработчики к корневому логгеру
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)


def get_logger(name: str) -> logging.Logger:
    """Получение логгера с указанным именем"""
    return logging.getLogger(name)
