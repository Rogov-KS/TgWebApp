from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Backend API for Telegram Snake Web App",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутеров
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
async def root() -> dict[str, Any]:
    return {"message": "Welcome to Telegram Snake Web App API"}


@app.get("/health")
async def health_check() -> dict[str, Any]:
    return {"status": "healthy"}
