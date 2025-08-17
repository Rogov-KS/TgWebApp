from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from sqladmin import Admin
from fastapi_versioning import VersionedFastAPI

from backend.entities.assemblers.routers import include_routers_into_app
from backend.core.logger import get_logger, setup_logging
from backend.ows.auth.cleanup import start_cleanup_task
from backend.cache_redis.main import init_cache
from backend.core.database import engine
from backend.admin_page.main import add_views_into_admin
from backend.admin_page.auth import authentication_backend
from backend.middlewares import add_middlewares
from backend.sentry import init_sentry
from backend.prometheus import init_prometheus


logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """События при запуске и завершении работы приложения"""
    # Событие при запуске приложения
    logger.info("Starting the application...", extra={"hello": "world"})
    logger.info("Starting OAuth cleanup task")
    init_sentry()
    setup_logging()
    start_cleanup_task()
    await init_cache()

    yield

    # Событие при завершении работы приложения
    logger.info("Stopping OAuth cleanup task")


# Создаем экземпляр FastAPI
app = FastAPI(
    version="0.1.0",
    root_path="/api",
    title="TgWebApp API"
)

# Подключаем роутеры
include_routers_into_app(app)

# Добавляем версионирование
app = VersionedFastAPI(
    app,
    version_format="{major}",
    prefix_format="/api/v{major}",
    lifespan=lifespan,
)

# Добавляем middlewares
add_middlewares(app)

# Добавляем Prometheus
init_prometheus(app)


# Добавляем админку
admin = Admin(
    app,
    engine,
    title="Admin",
    authentication_backend=authentication_backend,
)
add_views_into_admin(admin)


# if __name__ == "__main__":
#     # logger.info("sys.path: %s", sys.path)
#     # logger.info("settings config[CORS]: %s",
#     #            json.dumps(settings.get_cors_attrs(), indent=4))
#     # logger.info("settings config[SMTP]: %s",
#     #            json.dumps(settings.get_smtp_attrs(), indent=4))

#     logger.info("Starting the application...")
#     import uvicorn

#     uvicorn.run(app, host="0.0.0.0", port=8000)
#     logger.info("Application ended")
