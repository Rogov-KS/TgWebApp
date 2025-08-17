from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from backend.prometheus.router import router


def init_prometheus(app: FastAPI) -> None:
    """Инициализирует Prometheus"""
    instrumentator = Instrumentator(
        should_group_status_codes=False,
        excluded_handlers=[".*admin.*", ".*openapi.*", ".*docs.*"],
    )
    instrumentator.instrument(app).expose(app)


__all__ = ["init_prometheus", "router"]
