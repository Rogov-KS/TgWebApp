from fastapi import FastAPI

from backend.api.endpoints import auth, game_sessions, leaderboard, test
from backend.oauth2 import router as oauth2_router


def include_routers_into_app(app: FastAPI) -> None:
    app.include_router(test.router)
    app.include_router(oauth2_router)
    app.include_router(auth.router)
    # app.include_router(users.router) # noqa
    app.include_router(game_sessions.router)
    app.include_router(leaderboard.router)
