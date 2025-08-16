from backend.core.base_dao import BaseDAO
from backend.entities.oauth2_token.models import OAuth2Token


class OAuth2TokenDAO(BaseDAO[OAuth2Token]):
    """DAO для работы с OAuth2 токенами от сторонних провайдеров."""

    model = OAuth2Token
