"""Unit тесты для game_session service."""

from datetime import UTC, datetime
from unittest.mock import Mock

import pytest

from backend.entities.assemblers.schemas import SGameSession, SGameSessionCreate, SGameSessionUpdate, SUser
from backend.entities.game_session.dao import GameSessionDAO
from backend.entities.game_session.service import GameSessionService


class TestGameSessionService:
    """Тесты для GameSessionService."""

    @pytest.fixture
    def mock_game_session_dao(self):
        """Мок для GameSessionDAO."""
        return Mock(spec=GameSessionDAO)

    @pytest.fixture
    def mock_user_service(self):
        """Мок для UserService."""
        return Mock()

    @pytest.fixture
    def game_session_service(self, mock_game_session_dao, mock_user_service):
        """Создание GameSessionService с моком DAO."""
        return GameSessionService(mock_game_session_dao, mock_user_service)

    @pytest.fixture
    def sample_user(self):
        """Фикстура для тестового пользователя."""
        return SUser(
            id=1,
            telegram_id=None,
            email="test@example.com",
            username="testuser",
            hashed_password="$2b$12$test_hash",
            is_admin=False,
            is_bot=False,
            is_active=True,
            created_at=datetime.now(),
        )

    @pytest.fixture
    def sample_game_session(self):
        """Образец игровой сессии для тестов."""
        return SGameSession(
            id=1,
            user_id=1,
            score=100,
            duration=60,
            is_completed=True,
            started_at=datetime.now(UTC),
            completed_at=datetime.now(UTC),
        )

    @pytest.fixture
    def sample_game_session_create(self):
        """Образец данных для создания игровой сессии."""
        return SGameSessionCreate(
            user_id=1,
            score=0,
            duration=0,
            is_completed=False,
        )

    @pytest.mark.asyncio
    async def test_create_game_session_success(
        self, game_session_service, mock_game_session_dao, sample_game_session, sample_user
    ):
        """Тест успешного создания игровой сессии."""
        # Настройка мока
        mock_game_session_dao.create.return_value = sample_game_session

        # Данные для создания
        session_data = SGameSessionCreate(
            user_id=1,
            score=0,
            duration=0,
            is_completed=False,
        )

        # Вызов метода
        result = await game_session_service.create_game_session(session_data, sample_user)

        # Проверки
        assert result == sample_game_session
        mock_game_session_dao.create_game_session.assert_called_once_with(session_data)

    @pytest.mark.asyncio
    async def test_get_game_session_by_id_success(
        self, game_session_service, mock_game_session_dao, sample_game_session
    ):
        """Тест успешного получения игровой сессии по ID."""
        # Настройка мока
        mock_game_session_dao.get_one_or_none.return_value = sample_game_session

        # Вызов метода
        result = await game_session_service.get_game_session_by_id(1)

        # Проверки
        assert result == sample_game_session
        mock_game_session_dao.get_game_session_by_id.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_get_game_session_by_id_not_found(self, game_session_service, mock_game_session_dao):
        """Тест получения несуществующей игровой сессии по ID."""
        # Настройка мока
        mock_game_session_dao.get_one_or_none.return_value = None

        # Вызов метода
        result = await game_session_service.get_game_session_by_id(999)

        # Проверки
        assert result is None
        mock_game_session_dao.get_game_session_by_id.assert_called_once_with(999)

    @pytest.mark.asyncio
    async def test_get_user_game_sessions_success(
        self, game_session_service, mock_game_session_dao, sample_game_session
    ):
        """Тест успешного получения игровых сессий пользователя."""
        # Настройка мока
        mock_game_session_dao.get_all.return_value = [sample_game_session]

        # Вызов метода
        result = await game_session_service.get_user_game_sessions(1)

        # Проверки
        assert len(result) == 1
        assert result[0] == sample_game_session
        mock_game_session_dao.get_user_game_sessions.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_get_user_game_sessions_empty(self, game_session_service, mock_game_session_dao):
        """Тест получения пустого списка игровых сессий пользователя."""
        # Настройка мока
        mock_game_session_dao.get_all.return_value = []

        # Вызов метода
        result = await game_session_service.get_user_game_sessions(1)

        # Проверки
        assert result == []
        mock_game_session_dao.get_user_game_sessions.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_update_game_session_success(self, game_session_service, mock_game_session_dao, sample_game_session):
        """Тест успешного обновления игровой сессии."""
        # Настройка мока
        updated_session = SGameSession(
            id=1,
            user_id=1,
            score=200,
            duration=120,
            is_completed=True,
            started_at=datetime.now(UTC),
            completed_at=datetime.now(UTC),
        )
        mock_game_session_dao.update.return_value = updated_session

        # Данные для обновления
        update_data = SGameSessionUpdate(
            score=200,
            duration=120,
            is_completed=True,
        )

        # Вызов метода
        result = await game_session_service.update_game_session(1, update_data)

        # Проверки
        assert result == updated_session
        mock_game_session_dao.update_game_session.assert_called_once_with(1, update_data)

    @pytest.mark.asyncio
    async def test_complete_game_session_success(
        self, game_session_service, mock_game_session_dao, sample_game_session
    ):
        """Тест успешного завершения игровой сессии."""
        # Настройка мока
        completed_session = SGameSession(
            id=1,
            user_id=1,
            score=150,
            duration=90,
            is_completed=True,
            started_at=datetime.now(UTC),
            completed_at=datetime.now(UTC),
        )
        mock_game_session_dao.complete_game_session.return_value = completed_session

        # Вызов метода
        result = await game_session_service.complete_game_session(1, 150, 90)

        # Проверки
        assert result == completed_session
        mock_game_session_dao.complete_game_session.assert_called_once_with(1, 150, 90)

    @pytest.mark.asyncio
    async def test_get_user_best_score_success(self, game_session_service, mock_game_session_dao):
        """Тест успешного получения лучшего счета пользователя."""
        # Настройка мока
        mock_game_session_dao.get_user_best_score.return_value = 500

        # Вызов метода
        result = await game_session_service.get_user_best_score(1)

        # Проверки
        assert result == 500
        mock_game_session_dao.get_user_best_score.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_get_user_best_score_no_sessions(self, game_session_service, mock_game_session_dao):
        """Тест получения лучшего счета для пользователя без сессий."""
        # Настройка мока
        mock_game_session_dao.get_user_best_score.return_value = 0

        # Вызов метода
        result = await game_session_service.get_user_best_score(1)

        # Проверки
        assert result == 0
        mock_game_session_dao.get_user_best_score.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_get_user_total_playtime_success(self, game_session_service, mock_game_session_dao):
        """Тест успешного получения общего времени игры пользователя."""
        # Настройка мока
        mock_game_session_dao.get_user_total_playtime.return_value = 3600  # 1 час в секундах

        # Вызов метода
        result = await game_session_service.get_user_total_playtime(1)

        # Проверки
        assert result == 3600
        mock_game_session_dao.get_user_total_playtime.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_get_user_total_playtime_no_sessions(self, game_session_service, mock_game_session_dao):
        """Тест получения общего времени игры для пользователя без сессий."""
        # Настройка мока
        mock_game_session_dao.get_user_total_playtime.return_value = 0

        # Вызов метода
        result = await game_session_service.get_user_total_playtime(1)

        # Проверки
        assert result == 0
        mock_game_session_dao.get_user_total_playtime.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_delete_game_session_success(self, game_session_service, mock_game_session_dao):
        """Тест успешного удаления игровой сессии."""
        # Настройка мока
        mock_game_session_dao.delete_game_session.return_value = None

        # Вызов метода
        await game_session_service.delete_game_session(1)

        # Проверки
        mock_game_session_dao.delete_game_session.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_get_user_game_sessions_with_limit(
        self, game_session_service, mock_game_session_dao, sample_game_session
    ):
        """Тест получения игровых сессий пользователя с ограничением."""
        # Настройка мока
        mock_game_session_dao.get_all.return_value = [sample_game_session]

        # Вызов метода с лимитом
        result = await game_session_service.get_user_game_sessions(1, limit=10, offset=0)

        # Проверки
        assert len(result) == 1
        assert result[0] == sample_game_session
        mock_game_session_dao.get_user_game_sessions.assert_called_once_with(1, limit=10, offset=0)
