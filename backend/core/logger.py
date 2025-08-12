import logging
from pathlib import Path


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
