from typing import Annotated, Type

from fastapi import Depends

from backend.core.base_dao import BaseDAO
from backend.core.database import AsyncSessionDep
from backend.ows.auth.interfaces import IOAuth2TokenDAO
from backend.ows.auth.models import OAuth2TokenDB


class OAuth2TokenDAO(BaseDAO[OAuth2TokenDB]):
    """
    DAO (Data Access Object) для работы с OAuth2 токенами от сторонних провайдеров.

    Implements `IOAuth2TokenDAO` interface.
    """

    model = OAuth2TokenDB


OAuth2TokenDAO: Type[IOAuth2TokenDAO]


def get_oauth2_token_dao(session: AsyncSessionDep) -> IOAuth2TokenDAO:
    """Dependency для получения OAuth2TokenDAO."""
    return OAuth2TokenDAO(session)


# Тип для использования в других модулях
OAuth2TokenDAODep = Annotated[IOAuth2TokenDAO, Depends(get_oauth2_token_dao)]
