from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_versioning import version

from backend.core.dependecies import get_current_user
from backend.entities.game_session.dao import GameSessionDAO
from backend.entities.user.dao import UserDAO
from backend.core.logger import get_logger
from backend.entities.game_session.schemas import (
    GameSession,
    GameSessionCreate,
    GameSessionUpdate,
)
from backend.entities.user.schemas import User

router = APIRouter(prefix="/game_sessions", tags=["Game Sessions"])

logger = get_logger(__name__)


@router.get("/", response_model=list[GameSession])
@version(1)
async def get_game_sessions() -> list[GameSession]:
    """Получить все игровые сессии."""
    game_sessions = await GameSessionDAO.get_all()
    logger.info("Retrieved game sessions", extra={"count": len(game_sessions)})
    return game_sessions


@router.post("/", response_model=GameSession)
@version(1)
async def create_game_session(
    game_session_data: GameSessionCreate,
    user: User = Depends(get_current_user),
) -> GameSession:

    if game_session_data.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to create this game session",
        )
    logger.info("Creating game session", extra={"game_session_data": game_session_data.model_dump()})
    try:
        game_session = await GameSessionDAO.create(**game_session_data.model_dump())
    except Exception as e:
        logger.error("Error creating game session", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create game session",
        ) from e

    if not game_session:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create game session",
        )
    logger.info("Created game session", extra={"game_session": {
        "id": game_session.id,
        "user_id": game_session.user_id,
        "score": game_session.score,
        "level": game_session.level,
        "started_at": game_session.started_at.isoformat() if game_session.started_at else None,
        "ended_at": game_session.ended_at.isoformat() if game_session.ended_at else None
    }})

    # Update user max score
    if game_session.score > user.max_score:
        await UserDAO.update(
            filters={"id": user.id},
            update_data={"max_score": game_session.score},
        )

    return game_session


@router.get("/user_game_sessions", response_model=list[GameSession])
@version(1)
async def get_user_game_sessions(
    user: User = Depends(get_current_user),
) -> list[GameSession]:
    """Получить все игровые сессии."""
    game_sessions = await GameSessionDAO.get_all(user_id=user.id)
    logger.info("Retrieved game sessions", extra={"count": len(game_sessions), "user_id": user.id})
    return game_sessions


@router.get("/{game_session_id}", response_model=GameSession)
@version(1)
async def get_game_session(
    game_session_id: int,
    user: User = Depends(get_current_user),
) -> GameSession:

    logger.info("Retrieving game session", extra={"game_session_id": game_session_id, "user_id": user.id})
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
@version(1)
async def complete_game_session(
    game_session_id: int,
    game_session_update: GameSessionUpdate,
    user: User = Depends(get_current_user),
) -> GameSession:

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
    logger.info("Updating game session", extra={"game_session_update": game_session_update.model_dump()})
    ended_at = datetime.now(timezone.utc)
    try:
        game_session = await GameSessionDAO.update(
            filters={"id": game_session_id},
            update_data={"ended_at": ended_at, **game_session_update.model_dump()},
        )
    except Exception as e:
        logger.error("Error updating game session", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update game session",
        ) from e
    if not game_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game session not found",
        )
    logger.info("Completed game session", extra={"game_session": {
        "id": game_session.id,
        "user_id": game_session.user_id,
        "score": game_session.score,
        "level": game_session.level,
        "started_at": game_session.started_at.isoformat() if game_session.started_at else None,
        "ended_at": game_session.ended_at.isoformat() if game_session.ended_at else None
    }})
    return game_session


@router.delete("/{game_session_id}")
@version(1)
async def delete_game_session(
    game_session_id: int,
    user: User = Depends(get_current_user),
) -> dict[str, str]:

    deleted = await GameSessionDAO.delete(id=game_session_id, user_id=user.id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game session not found",
        )
    logger.info("Deleted game session", extra={"game_session_id": game_session_id})
    return {"message": "Game session deleted successfully"}
