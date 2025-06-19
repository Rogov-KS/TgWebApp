from typing import Any

from fastapi import APIRouter
from fastapi.security import HTTPBearer

router = APIRouter()
security = HTTPBearer()


@router.post("/login")
async def login() -> dict[str, Any]:
    """Вход пользователя через Telegram"""
    return {"message": "Login endpoint"}


@router.post("/logout")
async def logout() -> dict[str, Any]:
    """Выход пользователя"""
    return {"message": "Logout endpoint"}


@router.get("/me")
async def get_current_user() -> dict[str, Any]:
    """Получение информации текущем пользователе"""
    return {"message": "Current user info"}
