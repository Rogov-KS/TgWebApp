from fastapi import FastAPI

from backend.core import test_router
from backend.entities.auth.router import router as auth_router
from backend.entities.game_session.router import router as game_session_router
from backend.entities.leaderboard.router import router as leaderboard_router
from backend.entities.telegram import telegram_router
from backend.entities.user.router import router as user_router
from backend.integrations.oauth.router import router as oauth2_router
from backend.prometheus import router as prometheus_router


def include_routers_into_app(app: FastAPI) -> None:
    app.include_router(test_router.router)
    app.include_router(oauth2_router)
    app.include_router(auth_router)
    app.include_router(telegram_router)
    app.include_router(user_router)
    app.include_router(game_session_router)
    app.include_router(leaderboard_router)
    app.include_router(prometheus_router)
