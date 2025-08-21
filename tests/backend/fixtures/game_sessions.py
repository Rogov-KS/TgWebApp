"""
Фикстуры для игровых сессий в тестах
"""
import pytest
import pytest_asyncio
from backend.entities.game_session.dao import GameSessionDAO


@pytest.fixture
def game_session_data():
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
def multiple_game_sessions_data():
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
async def test_game_session(test_db_session, test_user, game_session_data):
    """Создает тестовую игровую сессию в БД."""

    dao = GameSessionDAO(test_db_session)
    game_session = await dao.create(**game_session_data)
    return game_session


@pytest_asyncio.fixture
async def test_game_sessions(
    test_db_session, test_users, multiple_game_sessions_data
):
    """Создает несколько тестовых игровых сессий в БД."""

    dao = GameSessionDAO(test_db_session)
    game_sessions = []
    for session_data in multiple_game_sessions_data:
        game_session = await dao.create(**session_data)
        game_sessions.append(game_session)
    return game_sessions
