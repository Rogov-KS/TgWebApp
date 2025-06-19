from fastapi import APIRouter

from app.api.endpoints import auth, game, telegram

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(game.router, prefix="/game", tags=["game"])
api_router.include_router(telegram.router, prefix="/telegram", tags=["telegram"])
