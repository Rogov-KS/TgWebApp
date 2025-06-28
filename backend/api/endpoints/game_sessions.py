from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, status

from backend.dao.game_session import GameSessionDAO
from backend.logger import get_logger
from backend.schemas.game_session import (
    GameSession,
    GameSessionCreate,
    GameSessionUpdate,
)


router = APIRouter(prefix="/game_sessions", tags=["Game Sessions"])

logger = get_logger(__name__)


@router.get("/", response_model=list[GameSession])
async def get_game_sessions() -> list[GameSession]:
    """Получить все игровые сессии."""
    game_sessions = await GameSessionDAO.get_all()
    logger.info("Retrieved %d game sessions", len(game_sessions))
    return game_sessions


@router.get("/{game_session_id}", response_model=GameSession)
async def get_game_session(game_session_id: int) -> GameSession:
    """Получить конкретную игровую сессию."""
    game_session = await GameSessionDAO.get_one_or_none(id=game_session_id)
    if not game_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game session not found",
        )
    return game_session


@router.get("/user/{user_id}", response_model=list[GameSession])
async def get_user_game_sessions(user_id: int) -> list[GameSession]:
    """Получить все игровые сессии пользователя."""
    game_sessions = await GameSessionDAO.get_all(user_id=user_id)
    logger.info(
        "Retrieved %d game sessions for user %d",
        len(game_sessions),
        user_id
    )
    return game_sessions


@router.post("/", response_model=GameSession)
async def create_game_session(
    game_session_data: GameSessionCreate
) -> GameSession:
    """Создать новую игровую сессию."""
    logger.info(f"Creating game session: {game_session_data.model_dump()}")
    try:
        game_session = await GameSessionDAO.create(**game_session_data.model_dump())
    except Exception as e:
        logger.error(f"Error creating game session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create game session",
        )

    if not game_session:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create game session",
        )
    logger.info(
        "Created game session %s",
        game_session
    )
    return game_session


@router.put("/{game_session_id}/complete", response_model=GameSession)
async def complete_game_session(
    game_session_id: int,
    game_session_data: GameSessionUpdate
) -> GameSession:
    """Завершить игровую сессию."""
    logger.info(f"Updating game session: {game_session_data.model_dump()}")
    ended_at = datetime.now(timezone.utc)
    try:
        game_session = await GameSessionDAO.update(
            filters={"id": game_session_id},
            update_data={
                "ended_at": ended_at,
                **game_session_data.model_dump()
            }
        )
    except Exception as e:
        logger.error(f"Error updating game session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update game session",
        )
    if not game_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game session not found",
        )
    logger.info(
        "Completed game session: %s",
        game_session
    )
    return game_session


@router.delete("/{game_session_id}")
async def delete_game_session(game_session_id: int) -> dict[str, str]:
    """Удалить игровую сессию."""
    deleted = await GameSessionDAO.delete(id=game_session_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game session not found",
        )
    logger.info("Deleted game session %d", game_session_id)
    return {"message": "Game session deleted successfully"}
