from datetime import datetime, timedelta, timezone

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.dao.base import BaseDAO
from backend.models.oauth2_token import OAuth2Token
from backend.core.database import async_session_maker


class OAuth2TokenDAO(BaseDAO[OAuth2Token]):
    """DAO для работы с refresh токенами через таблицу refresh_tokens,
    которая хранит только refresh токены нашего приложения."""

    model = OAuth2Token
