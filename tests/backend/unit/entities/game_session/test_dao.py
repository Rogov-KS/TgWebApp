"""
Unit тесты для GameSessionDAO
"""
import pytest
import pytest_asyncio
from backend.entities.game_session.dao import GameSessionDAO
from sqlalchemy.orm.exc import MultipleResultsFound
from backend.entities.game_session.models import GameSessionDB
from backend.entities.user.models import UserDB
from backend.entities.user.dao import UserDAO
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError


class TestGameSessionDAO:
    """Тесты для GameSessionDAO."""

    @pytest_asyncio.fixture
    async def dao(self, get_async_test_db_session) -> GameSessionDAO:
        """Создает экземпляр GameSessionDAO для тестов."""
        return GameSessionDAO(get_async_test_db_session)

    class TestCreate:
        """Тесты для метода create."""

        async def test_create_game_session_success(
            self, dao, insert_test_user: UserDB, get_game_session_data: dict
        ):
            """Тест успешного создания игровой сессии."""
            game_session_data = get_game_session_data
            game_session = await dao.create(**game_session_data)

            assert game_session is not None
            assert game_session.user_id == game_session_data["user_id"]
            assert game_session.score == game_session_data["score"]
            assert game_session.duration == game_session_data["duration"]
            assert game_session.level == game_session_data["level"]
            assert game_session.is_completed == game_session_data[
                "is_completed"
            ]
            assert game_session.game_data == game_session_data["game_data"]
            assert game_session.id is not None

        async def test_create_game_session_minimal_data(
            self, dao, insert_test_user: UserDB
        ):
            """Тест создания игровой сессии с минимальными данными."""
            minimal_data = {"user_id": insert_test_user.id}
            game_session = await dao.create(**minimal_data)

            assert game_session is not None
            assert game_session.user_id == insert_test_user.id
            assert game_session.score == 0  # значение по умолчанию
            assert game_session.duration == 0  # значение по умолчанию
            assert game_session.level == 1  # значение по умолчанию
            assert game_session.is_completed is False  # значение по умолчанию

        async def test_create_game_session_with_invalid_user_id(
            self, dao, insert_test_user: UserDB
        ):
            """Тест создания игровой сессии с минимальными данными."""
            minimal_data = {"user_id": insert_test_user.id + 1}

            with pytest.raises(IntegrityError):
                await dao.create(**minimal_data)

    class TestGetOneOrNone:
        """Тесты для метода get_one_or_none."""

        async def test_get_game_session_by_id_success(
            self,
            dao: GameSessionDAO,
            insert_test_game_session: GameSessionDB
        ):
            """Тест успешного получения игровой сессии по ID."""
            game_session = insert_test_game_session
            result = await dao.get_one_or_none(id=game_session.id)

            assert result is not None
            assert result.id == game_session.id
            assert result.user_id == game_session.user_id

        async def test_get_game_session_by_user_id(
            self,
            dao: GameSessionDAO,
            insert_test_game_sessions: list[GameSessionDB]
        ):
            """Тест получения игровой сессии по user_id."""
            game_sessions = insert_test_game_sessions
            user_id = game_sessions[-1].user_id
            result = await dao.get_one_or_none(user_id=user_id)
            assert result is not None
            assert result.user_id == user_id

        async def test_get_game_session_by_user_id_with_exception(
            self,
            dao: GameSessionDAO,
            insert_test_game_sessions: list[GameSessionDB]
        ):
            """Тест получения игровой сессии по user_id."""
            game_sessions = insert_test_game_sessions
            user_id = game_sessions[0].user_id
            with pytest.raises(MultipleResultsFound):
                await dao.get_one_or_none(user_id=user_id)

    class TestGetAll:
        """Тесты для метода get_all."""

        async def test_get_all_game_sessions(
            self, dao, insert_test_game_sessions: list[GameSessionDB]
        ):
            """Тест получения всех игровых сессий."""
            result = await dao.get_all()

            assert len(result) == len(insert_test_game_sessions)
            assert all(isinstance(session, GameSessionDB) for session in result)

        async def test_get_game_sessions_by_user_id(
            self, dao, insert_test_game_sessions: list[GameSessionDB]
        ):
            """Тест получения игровых сессий по user_id."""
            user_id = 1
            result = await dao.get_all(user_id=user_id)

            # В тестовых данных у пользователя с id=1 есть 3 сессии
            assert len(result) == 3
            assert all(session.user_id == user_id for session in result)

        async def test_get_completed_game_sessions(
            self, dao, insert_test_game_sessions: list[GameSessionDB]
        ):
            """Тест получения завершенных игровых сессий."""
            result = await dao.get_all(is_completed=True)

            # В тестовых данных есть 3 завершенные сессии
            assert len(result) == 3
            assert all(session.is_completed is True for session in result)

    class TestUpdate:
        """Тесты для метода update."""

        async def test_update_game_session_success(
            self, dao, insert_test_game_session: GameSessionDB
        ):
            """Тест успешного обновления игровой сессии."""
            update_data = {
                "score": 500,
                "duration": 1200,
                "level": 5,
                "is_completed": True,
            }

            result = await dao.update(
                filters={"id": insert_test_game_session.id},
                update_data=update_data
            )

            assert result is not None
            assert result.score == update_data["score"]
            assert result.duration == update_data["duration"]
            assert result.level == update_data["level"]
            assert result.is_completed == update_data["is_completed"]

        async def test_update_game_session_not_found(self, dao, insert_test_game_session: GameSessionDB):
            """Тест обновления несуществующей игровой сессии."""
            update_data = {"score": 500}

            result = await dao.update(
                filters={"id": insert_test_game_session.id + 1},
                update_data=update_data
            )

            assert result is None

        async def test_update_game_session_empty_filters(self, dao, insert_test_game_session: GameSessionDB):
            """Тест обновления с пустыми фильтрами."""
            update_data = {"score": 500}

            with pytest.raises(
                ValueError, match="Filters and update data cannot be empty"
            ):
                await dao.update(filters={}, update_data=update_data)

        async def test_update_game_session_empty_data(self, dao, insert_test_game_session: GameSessionDB):
            """Тест обновления с пустыми данными."""
            with pytest.raises(ValueError, match="Filters and update data cannot be empty"):
                await dao.update(
                    filters={"id": insert_test_game_session.id},
                    update_data={}
                )

    class TestDelete:
        """Тесты для метода delete."""

        async def test_delete_game_session_success(
            self, dao, insert_test_game_session: GameSessionDB
        ):
            """Тест успешного удаления игровой сессии."""
            result = await dao.delete(id=insert_test_game_session.id)

            assert result is True

            # Проверяем, что сессия действительно удалена
            deleted_session = await dao.get_one_or_none(id=insert_test_game_session.id)
            assert deleted_session is None

        async def test_delete_game_session_not_found(self, dao, insert_test_game_session: GameSessionDB):
            """Тест удаления несуществующей игровой сессии."""
            result = await dao.delete(id=insert_test_game_session.id + 1)

            assert result is False

    class TestGetMaxScore:
        """Тесты для специфичного метода get_max_score."""

        async def test_get_max_score_success(self, dao, insert_test_game_sessions: list[GameSessionDB]):
            """Тест успешного получения максимального счета."""
            user_id = 1
            result = await dao.get_max_score(user_id)

            # В тестовых данных у пользователя с id=1 максимальный счет 250
            assert result == 250

        async def test_get_max_score_user_with_no_sessions(self, dao, insert_test_game_sessions: list[GameSessionDB]):
            """Тест получения максимального счета для пользователя без сессий."""
            user_id = 999
            result = await dao.get_max_score(user_id)

            assert result is None

        async def test_get_max_score_invalid_user_id_zero(self, dao, insert_test_game_sessions: list[GameSessionDB]):
            """Тест получения максимального счета с user_id = 0."""
            with pytest.raises(
                ValueError,
                match="user_id должен быть положительным целым числом"
            ):
                await dao.get_max_score(0)

        async def test_get_max_score_invalid_user_id_negative(self, dao, insert_test_game_sessions: list[GameSessionDB]):
            """Тест получения максимального счета с отрицательным user_id."""
            with pytest.raises(ValueError, match="user_id должен быть положительным целым числом"):
                await dao.get_max_score(-1)

        async def test_get_max_score_invalid_user_id_type(self, dao, insert_test_game_sessions: list[GameSessionDB]):
            """Тест получения максимального счета с неправильным типом user_id."""
            with pytest.raises(ValueError, match="user_id должен быть положительным целым числом"):
                await dao.get_max_score("invalid")

        async def test_get_max_score_multiple_users(self, dao, insert_test_game_sessions: list[GameSessionDB]):
            """Тест получения максимального счета для разных пользователей."""
            # У пользователя с id=1 максимальный счет 250
            max_score_user1 = await dao.get_max_score(1)
            assert max_score_user1 == 250

            # У пользователя с id=2 максимальный счет 300
            max_score_user2 = await dao.get_max_score(2)
            assert max_score_user2 == 300
