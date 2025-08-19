from typing import Annotated

from fastapi import Depends

from backend.core.base_dao import BaseDAO
from backend.core.database import AsyncSessionDep
from backend.ows.auth.models import OAuth2Token


class OAuth2TokenDAO(BaseDAO[OAuth2Token]):
    """DAO для работы с OAuth2 токенами от сторонних провайдеров."""

    model = OAuth2Token


def get_oauth2_token_dao(session: AsyncSessionDep) -> OAuth2TokenDAO:
    """Dependency для получения OAuth2TokenDAO."""
    return OAuth2TokenDAO(session)


# Тип для использования в других модулях
OAuth2TokenDAODep = Annotated[OAuth2TokenDAO, Depends(get_oauth2_token_dao)]
