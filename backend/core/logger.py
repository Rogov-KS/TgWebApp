import logging
from pathlib import Path
from pythonjsonlogger import jsonlogger
from datetime import datetime

from backend.core.config import settings


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """Форматтер для логирования в JSON"""
    def add_fields(self, log_record: dict, record: logging.LogRecord, message_dict: dict) -> None:
        """Добавление полей в лог"""
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        if not log_record.get("timestamp"):
            now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            log_record["timestamp"] = now
        if log_record.get("level"):
            log_record["level"] = log_record["level"].upper()
        else:
            log_record["level"] = record.levelname


# formatter = CustomJsonFormatter(
#     "%(timestamp)s %(level)s %(message)s %(module)s %(funcName)s"
# )

# logger = logging.getLogger()

# logHandler = logging.StreamHandler()

# logHandler.setFormatter(formatter)
# logger.addHandler(logHandler)
# logger.setLevel(settings.LOG_LEVEL)


def setup_logging() -> None:
    """Настройка базовой конфигурации логирования"""
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        handlers=[
            logging.FileHandler(f"{logs_dir}/bot_log.txt", encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )


def get_logger(name: str) -> logging.Logger:
    """Получение логгера с указанным именем"""
    return logging.getLogger(name)
