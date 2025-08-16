from fastapi import FastAPI

from backend.routers.endpoints import auth, leaderboard, test

from backend.entities.user.router import router as user_router
from backend.entities.game_session.router import router as game_session_router

from backend.oauth2 import router as oauth2_router
from backend.prometheus import router as prometheus_router


def include_routers_into_app(app: FastAPI) -> None:
    app.include_router(test.router)
    app.include_router(oauth2_router)
    app.include_router(auth.router)
    app.include_router(user_router) # noqa
    app.include_router(game_session_router)
    app.include_router(leaderboard.router)
    app.include_router(prometheus_router)
