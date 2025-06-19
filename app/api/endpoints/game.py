from typing import Any

from fastapi import APIRouter

router = APIRouter()


@router.post("/start")
async def start_game() -> dict[str, Any]:
    """Начать новую игру"""
    return {"message": "Game started", "game_id": "123"}


@router.get("/{game_id}")
async def get_game_state(game_id: str) -> dict[str, Any]:
    """Получить состояние игры"""
    return {"game_id": game_id, "state": "playing"}


@router.post("/{game_id}/move")
async def make_move(game_id: str, direction: str) -> dict[str, Any]:
    """Сделать ход в игре"""
    return {"game_id": game_id, "move": direction}


@router.get("/leaderboard")
async def get_leaderboard() -> dict[str, Any]:
    """Получить таблицу лидеров"""
    return {"leaderboard": []}
