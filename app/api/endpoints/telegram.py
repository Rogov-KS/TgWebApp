from typing import Any

from fastapi import APIRouter

router = APIRouter()


@router.post("/webhook")
async def telegram_webhook() -> dict[str, Any]:
    """Webhook для получения обновлений от Telegram"""
    return {"message": "Webhook received"}


@router.get("/init")
async def init_telegram() -> dict[str, Any]:
    """Инициализация Telegram Web App"""
    return {"message": "Telegram Web App initialized"}
