from datetime import UTC, datetime
from typing import Annotated, List

from fastapi import Depends, HTTPException, status

from backend.core.logger import get_logger
from backend.entities.game_session.dao import GameSessionDAO, GameSessionDAODep
from backend.entities.game_session.schemas import (
    GameSession,
    GameSessionCreate,
    GameSessionUpdate,
)
from backend.entities.user.dao import UserDAODep
from backend.entities.user.interfaces import IUserDAO
from backend.entities.user.schemas import User

logger = get_logger(__name__)


class GameSessionService:
    """Сервисный слой для работы с игровыми сессиями."""

    def __init__(self, game_session_dao: GameSessionDAO, user_dao: IUserDAO):
        self.game_session_dao = game_session_dao
        self.user_dao = user_dao

    async def get_all_game_sessions(self) -> List[GameSession]:
        """
        Получить все игровые сессии.

        Returns:
            List[GameSession]: Список всех игровых сессий
        """
        game_sessions = await self.game_session_dao.get_all()
        logger.info(
            "Retrieved game sessions",
            extra={"count": len(game_sessions)}
        )
        return [
            GameSession.model_validate(session) for session in game_sessions
        ]

    async def get_user_game_sessions(self, user_id: int) -> List[GameSession]:
        """
        Получить все игровые сессии пользователя.

        Args:
            user_id (int): ID пользователя

        Returns:
            List[GameSession]: Список игровых сессий пользователя
        """
        game_sessions = await self.game_session_dao.get_all(user_id=user_id)
        logger.info(
            "Retrieved game sessions",
            extra={"count": len(game_sessions), "user_id": user_id},
        )
        return [
            GameSession.model_validate(session) for session in game_sessions
        ]

    async def get_game_session_by_id(
        self, game_session_id: int, user: User
    ) -> GameSession:
        """
        Получить игровую сессию по ID с проверкой доступа.

        Args:
            game_session_id (int): ID игровой сессии
            user (User): Текущий пользователь

        Returns:
            GameSession: Игровая сессия

        Raises:
            HTTPException: Если сессия не найдена или нет доступа
        """
        logger.info(
            "Retrieving game session",
            extra={
                "game_session_id": game_session_id,
                "user_id": user.id
            },
        )
        game_session = await self.game_session_dao.get_one_or_none(id=game_session_id)
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
        return GameSession.model_validate(game_session)

    async def create_game_session(
        self, game_session_data: GameSessionCreate, user: User
    ) -> GameSession:
        """
        Создать новую игровую сессию.

        Args:
            game_session_data (GameSessionCreate): Данные для создания сессии
            user (User): Текущий пользователь

        Returns:
            GameSession: Созданная игровая сессия

        Raises:
            HTTPException: Если нет прав на создание или ошибка создания
        """
        if game_session_data.user_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not allowed to create this game session",
            )

        logger.info(
            "Creating game session",
            extra={"game_session_data": game_session_data.model_dump()},
        )

        try:
            game_session = await self.game_session_dao.create(
                **game_session_data.model_dump()
            )
        except Exception as e:
            logger.exception("Error creating game session", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create game session",
            ) from e

        if not game_session:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create game session",
            )

        logger.info(
            "Created game session",
            extra={
                "game_session": {
                    "id": game_session.id,
                    "user_id": game_session.user_id,
                    "score": game_session.score,
                    "level": game_session.level,
                    "started_at": (
                        game_session.started_at.isoformat()
                        if game_session.started_at
                        else None
                    ),
                    "ended_at": (
                        game_session.ended_at.isoformat()
                        if game_session.ended_at
                        else None
                    ),
                }
            },
        )

        # Обновить максимальный счет пользователя
        if game_session.score > user.max_score:
            await self.user_dao.update(
                filters={"id": user.id},
                update_data={"max_score": game_session.score},
            )

        return GameSession.model_validate(game_session)

    async def update_game_session(
        self,
        game_session_id: int,
        game_session_update: GameSessionUpdate,
        user: User,
    ) -> GameSession:
        """
        Обновить игровую сессию.

        Args:
            game_session_id (int): ID игровой сессии
            game_session_update (GameSessionUpdate): Данные для обновления
            user (User): Текущий пользователь

        Returns:
            GameSession: Обновленная игровая сессия

        Raises:
            HTTPException: Если сессия не найдена, нет доступа или ошибка обновления
        """
        game_session = await self.game_session_dao.get_one_or_none(id=game_session_id)
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

        logger.info(
            "Updating game session",
            extra={"game_session_update": game_session_update.model_dump()},
        )

        ended_at = datetime.now(UTC)
        try:
            updated_game_session = await self.game_session_dao.update(
                filters={"id": game_session_id},
                update_data={
                    "ended_at": ended_at,
                    **game_session_update.model_dump()
                },
            )
        except Exception as e:
            logger.exception("Error updating game session", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update game session",
            ) from e

        if not updated_game_session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Game session not found",
            )

        logger.info(
            "Completed game session",
            extra={
                "game_session": {
                    "id": updated_game_session.id,
                    "user_id": updated_game_session.user_id,
                    "score": updated_game_session.score,
                    "level": updated_game_session.level,
                    "started_at": (
                        updated_game_session.started_at.isoformat()
                        if updated_game_session.started_at
                        else None
                    ),
                    "ended_at": (
                        updated_game_session.ended_at.isoformat()
                        if updated_game_session.ended_at
                        else None
                    ),
                }
            },
        )
        return GameSession.model_validate(updated_game_session)

    async def delete_game_session(self, game_session_id: int, user: User) -> bool:
        """
        Удалить игровую сессию.

        Args:
            game_session_id (int): ID игровой сессии
            user (User): Текущий пользователь

        Returns:
            bool: True если сессия удалена, False если не найдена

        Raises:
            HTTPException: Если сессия не найдена
        """
        deleted = await self.game_session_dao.delete(
            id=game_session_id, user_id=user.id
        )
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Game session not found",
            )
        logger.info(
            "Deleted game session",
            extra={"game_session_id": game_session_id}
        )
        return deleted


def get_game_session_service(
    game_session_dao: GameSessionDAODep, user_dao: UserDAODep
) -> GameSessionService:
    """Dependency для получения GameSessionService."""
    return GameSessionService(game_session_dao, user_dao)


# Тип для использования в роутерах
GameSessionServiceDep = Annotated[
    GameSessionService, Depends(get_game_session_service)
]
