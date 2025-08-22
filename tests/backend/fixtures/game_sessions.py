"""
Фикстуры для игровых сессий в тестах
"""
import pytest
import pytest_asyncio
from backend.entities.user.dao import UserDAO
from backend.entities.game_session.dao import GameSessionDAO
from backend.entities.game_session.models import GameSessionDB
from sqlalchemy.ext.asyncio import AsyncSession
from backend.entities.user.models import UserDB


@pytest.fixture
def get_game_session_data() -> dict:
    """Тестовые данные игровой сессии."""
    return {
        "user_id": 1,
        "score": 100,
        "duration": 300,  # 5 минут
        "level": 2,
        "is_completed": True,
        "game_data": {"snake_length": 10, "food_eaten": 5},
    }


@pytest.fixture
def get_multiple_game_sessions_data() -> list[dict]:
    """Тестовые данные для нескольких игровых сессий."""
    return [
        {
            "user_id": 1,
            "score": 100,
            "duration": 300,
            "level": 2,
            "is_completed": True,
            "game_data": {"snake_length": 10, "food_eaten": 5},
        },
        {
            "user_id": 1,
            "score": 250,
            "duration": 600,
            "level": 3,
            "is_completed": True,
            "game_data": {"snake_length": 15, "food_eaten": 12},
        },
        {
            "user_id": 1,
            "score": 50,
            "duration": 120,
            "level": 1,
            "is_completed": False,
            "game_data": {"snake_length": 5, "food_eaten": 2},
        },
        {
            "user_id": 2,
            "score": 300,
            "duration": 900,
            "level": 4,
            "is_completed": True,
            "game_data": {"snake_length": 20, "food_eaten": 18},
        },
    ]


@pytest_asyncio.fixture
async def insert_test_game_session(
    get_async_test_db_session: AsyncSession,
    insert_test_user: UserDB,
    get_game_session_data: dict,
) -> GameSessionDB:
    """Создает тестовую игровую сессию в БД."""
    msg = "GameSession's user-id must be equal to User's id"
    assert insert_test_user.id == get_game_session_data["user_id"], msg

    dao = GameSessionDAO(get_async_test_db_session)
    game_session = await dao.create(
        **get_game_session_data
    )
    return game_session


@pytest_asyncio.fixture
async def insert_test_game_sessions(
    get_async_test_db_session: AsyncSession,
    insert_test_users: list[UserDB],
    get_multiple_game_sessions_data: list[dict],
) -> list[GameSessionDB]:
    """Создает несколько тестовых игровых сессий в БД."""

    dao = GameSessionDAO(get_async_test_db_session)
    game_sessions = []
    for session_data in get_multiple_game_sessions_data:
        game_session = await dao.create(
            **session_data
        )
        game_sessions.append(game_session)
    return game_sessions
