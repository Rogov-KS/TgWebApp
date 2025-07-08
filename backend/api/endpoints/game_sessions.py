from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, status

from backend.core.dependecies import get_current_user
from backend.dao.game_session import GameSessionDAO
from backend.logger import get_logger
from backend.schemas.game_session import (
    GameSession,
    GameSessionCreate,
    GameSessionUpdate,
)
from backend.schemas.user import User

router = APIRouter(prefix="/game_sessions", tags=["Game Sessions"])

logger = get_logger(__name__)


@router.get("/", response_model=list[GameSession])
async def get_game_sessions() -> list[GameSession]:
    """Получить все игровые сессии."""
    game_sessions = await GameSessionDAO.get_all()
    logger.info("Retrieved %d game sessions", len(game_sessions))
    return game_sessions


@router.post("/", response_model=GameSession)
async def create_game_session(
    game_session_data: GameSessionCreate,
    user: User = Depends(get_current_user),
) -> GameSession:
    """Создать новую игровую сессию."""
    if game_session_data.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to create this game session",
        )
    logger.info("Creating game session: %s", game_session_data.model_dump())
    try:
        game_session = await GameSessionDAO.create(**game_session_data.model_dump())
    except Exception as e:
        logger.exception("Error creating game session")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create game session",
        ) from e

    if not game_session:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create game session",
        )
    logger.info("Created game session %s", game_session)
    return game_session


@router.get("/user_game_sessions", response_model=list[GameSession])
async def get_user_game_sessions(
    user: User = Depends(get_current_user),
) -> list[GameSession]:
    """Получить все игровые сессии."""
    game_sessions = await GameSessionDAO.get_all(user_id=user.id)
    logger.info("Retrieved %d game sessions", len(game_sessions))
    return game_sessions


@router.get("/{game_session_id}", response_model=GameSession)
async def get_game_session(
    game_session_id: int,
    user: User = Depends(get_current_user),
) -> GameSession:
    """Получить конкретную игровую сессию."""
    logger.info("Retrieving game session %d for user %s", game_session_id, user)
    game_session = await GameSessionDAO.get_one_or_none(id=game_session_id)
    if not game_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game session not found",
        )
    if game_session.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to access this game session",
        )
    return game_session


@router.put("/{game_session_id}", response_model=GameSession)
async def complete_game_session(
    game_session_id: int,
    game_session_update: GameSessionUpdate,
    user: User = Depends(get_current_user),
) -> GameSession:
    """Завершить игровую сессию."""
    game_session = await GameSessionDAO.get_one_or_none(id=game_session_id)
    if not game_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game session not found",
        )
    if game_session.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to update this game session",
        )
    logger.info("Updating game session: %s", game_session_update.model_dump())
    ended_at = datetime.now(UTC)
    try:
        game_session = await GameSessionDAO.update(
            filters={"id": game_session_id},
            update_data={"ended_at": ended_at, **game_session_update.model_dump()},
        )
    except Exception as e:
        logger.exception("Error updating game session")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update game session",
        ) from e
    if not game_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game session not found",
        )
    logger.info("Completed game session: %s", game_session)
    return game_session


@router.delete("/{game_session_id}")
async def delete_game_session(
    game_session_id: int,
    user: User = Depends(get_current_user),
) -> dict[str, str]:
    """Удалить игровую сессию."""
    deleted = await GameSessionDAO.delete(id=game_session_id, user_id=user.id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game session not found",
        )
    logger.info("Deleted game session %d", game_session_id)
    return {"message": "Game session deleted successfully"}
