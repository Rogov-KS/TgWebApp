from fastapi import APIRouter
from fastapi_versioning import version

from backend.core.dependecies import CurrentUserDep
from backend.entities.assemblers.schemas import (
    SGameSession,
    SGameSessionCreate,
    SGameSessionUpdate,
)
from backend.entities.game_session.service import GameSessionServiceDep

router = APIRouter(prefix="/game_sessions", tags=["Game Sessions"])


@router.get("/", response_model=list[SGameSession])
@version(1)
async def get_game_sessions(
    game_session_service: GameSessionServiceDep,
) -> list[SGameSession]:
    """Получить все игровые сессии."""
    return await game_session_service.get_all_game_sessions()


@router.post("/", response_model=SGameSession)
@version(1)
async def create_game_session(
    game_session_data: SGameSessionCreate,
    user: CurrentUserDep,
    game_session_service: GameSessionServiceDep,
) -> SGameSession:
    """Создать новую игровую сессию."""
    return await game_session_service.create_game_session(
        game_session_data, user
    )


@router.get("/user_game_sessions", response_model=list[SGameSession])
@version(1)
async def get_user_game_sessions(
    user: CurrentUserDep,
    game_session_service: GameSessionServiceDep,
) -> list[SGameSession]:
    """Получить все игровые сессии пользователя."""
    return await game_session_service.get_user_game_sessions(user.id)


@router.get("/{game_session_id}", response_model=SGameSession)
@version(1)
async def get_game_session(
    game_session_id: int,
    user: CurrentUserDep,
    game_session_service: GameSessionServiceDep,
) -> SGameSession:
    """Получить игровую сессию по ID."""
    return await game_session_service.get_game_session_by_id(
        game_session_id, user
    )


@router.put("/{game_session_id}", response_model=SGameSession)
@version(1)
async def complete_game_session(
    game_session_id: int,
    game_session_update: SGameSessionUpdate,
    user: CurrentUserDep,
    game_session_service: GameSessionServiceDep,
) -> SGameSession:
    """Завершить игровую сессию."""
    return await game_session_service.update_game_session(
        game_session_id, game_session_update, user
    )


@router.delete("/{game_session_id}")
@version(1)
async def delete_game_session(
    game_session_id: int,
    user: CurrentUserDep,
    game_session_service: GameSessionServiceDep,
) -> dict[str, str]:
    """Удалить игровую сессию."""
    await game_session_service.delete_game_session(game_session_id, user)
    return {"message": "Game session deleted successfully"}
