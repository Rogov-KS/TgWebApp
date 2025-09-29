from datetime import UTC, datetime
from typing import Annotated, List, Any

from fastapi import Depends, HTTPException, status

from backend.core.logger import get_logger
from backend.entities.game_session.dao import GameSessionDAODep, GameSessionDAO
from backend.entities.assemblers.schemas import (
    SGameSession,
    SGameSessionCreate,
    SGameSessionUpdate,
)
from backend.entities.assemblers.schemas import SUser
from backend.entities.user.service import (
    UserService, UserServiceDep
)
logger = get_logger(__name__)


class GameSessionService:
    """
    Сервисный слой для работы с игровыми сессиями.
    """

    def __init__(
        self, game_session_dao: GameSessionDAO, user_service: UserService
    ):
        self.game_session_dao = game_session_dao
        self.user_service = user_service

    async def get_all_game_sessions(self) -> List[SGameSession]:
        """
        Получить все игровые сессии.

        Returns:
            List[SGameSession]: Список всех игровых сессий
        """
        game_sessions = await self.game_session_dao.get_all()
        logger.info(
            "Retrieved game sessions",
            extra={"count": len(game_sessions)}
        )
        return [
            SGameSession.model_validate(session) for session in game_sessions
        ]

    async def get_user_game_sessions(self, user_id: int) -> List[SGameSession]:
        """
        Получить все игровые сессии пользователя.

        Args:
            user_id (int): ID пользователя

        Returns:
            List[SGameSession]: Список игровых сессий пользователя
        """
        game_sessions = await self.game_session_dao.get_all(user_id=user_id)
        logger.info(
            "Retrieved game sessions",
            extra={"count": len(game_sessions), "user_id": user_id},
        )
        return [
            SGameSession.model_validate(session) for session in game_sessions
        ]

    async def get_all_game_sessions_by(
        self, user: SUser, **filter_by: Any
    ) -> List[SGameSession]:
        """
        Получить игровую сессию по фильтру.

        Args:
            **filter_by: Фильтр
            user (User): Текущий пользователь для проверки доступа

        Returns:
            List[SGameSession]: Список игровых сессий
        """
        logger.info(
            "Retrieving game sessions",
            extra={
                "filter_by": filter_by,
                "user_id": user.id
            },
        )
        game_session = await self.game_session_dao.get_all_sorted(**filter_by)
        return [SGameSession.model_validate(session) for session in game_session if session.user_id == user.id]

    async def get_all_game_sessions_sorted(
        self, limit: int = 10, offset: int = 0, sort_order: str = "desc", **filter_by: Any
    ) -> List[SGameSession]:
        """
        Получить все игровые сессии пользователя с сортировкой.
        """
        logger.info(
            "Retrieving game sessions With Pagination and Sorting",
            extra={
                "filter_by": filter_by,
                "user_id": user.id,
                "limit": limit,
                "offset": offset,
                "sort_order": sort_order
            },
        )
        game_session = await self.game_session_dao.get_all_sorted(limit=limit, offset=offset, sort_order=sort_order, **filter_by)
        return [SGameSession.model_validate(session) for session in game_session]

    async def get_game_session_by(
        self, user: SUser, **filter_by: Any
    ) -> SGameSession | None:
        """
        Получить игровую сессию по фильтру.
        """
        logger.info(
            "Retrieving game session",
            extra={
                "filter_by": filter_by,
                "user_id": user.id
            },
        )
        game_session = await self.game_session_dao.get_one_or_none(**filter_by)
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

        return SGameSession.model_validate(game_session)

    async def get_game_session_by_id(
        self, game_session_id: int, user: SUser
    ) -> SGameSession | None:
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
        return await self.get_game_session_by(id=game_session_id, user=user)

    async def create_game_session(
        self, game_session_data: SGameSessionCreate, user: SUser
    ) -> SGameSession:
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
            extra={"game_session": game_session},
        )

        return SGameSession.model_validate(game_session)

    async def update_game_session(
        self,
        filter_by: dict[str, Any],
        update_data: dict[str, Any],
        user: SUser,
    ) -> SGameSession:
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
        # Проверяем доступ к сессии
        _ = await self.get_game_session_by(**filter_by, user=user)

        logger.info(
            "Updating game session",
            extra={"game_session_update": update_data},
        )

        ended_at = datetime.now(UTC)
        try:
            updated_game_session = await self.game_session_dao.update(
                filters=filter_by,
                update_data={
                    "ended_at": ended_at,
                    **update_data
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
            extra={"updated_game_session": updated_game_session},
        )
        return SGameSession.model_validate(updated_game_session)

    async def delete_game_session(self, filter_by: dict[str, Any], user: SUser) -> bool:
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
            **filter_by
        )
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Game session not found",
            )
        logger.info(
            "Deleted game session",
            extra={"filter_by": filter_by}
        )
        return deleted

    async def get_user_max_score(self, user: SUser) -> int | None:
        """
        Получить максимальный счет пользователя.
        """
        return await self.game_session_dao.get_max_score(user.id)


def get_game_session_service(
    game_session_dao: GameSessionDAODep, user_service: UserServiceDep
) -> GameSessionService:
    """Dependency для получения GameSessionService."""
    return GameSessionService(game_session_dao, user_service)


# Тип для использования в роутерах
GameSessionServiceDep = Annotated[GameSessionService, Depends(get_game_session_service)]
