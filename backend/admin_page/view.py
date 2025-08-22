from sqladmin import ModelView

from backend.entities.assemblers.models import *


class UsersAdmin(ModelView, model=UserDB):
    column_list = [
        c.name for c in UserDB.__table__.columns if c.name != "hashed_password"
    ]
    column_details_exclude_list = [UserDB.hashed_password]
    can_delete = False
    name = "Пользователь"
    name_plural = "Пользователи"
    icon = "fa-solid fa-user"


class GameSessionsAdmin(ModelView, model=GameSession):
    column_list = [c.name for c in GameSession.__table__.columns]
    can_delete = False
    name = "Игровая сессия"
    name_plural = "Игровые сессии"
    icon = "fa-solid fa-gamepad"


class RefreshTokenAdmin(ModelView, model=RefreshToken):
    column_list = [c.name for c in RefreshToken.__table__.columns if c.name != "token"]
    column_details_exclude_list = [RefreshToken.token]
    can_create = False
    can_edit = False
    name = "Refresh токен"
    name_plural = "Refresh токены"
    icon = "fa-solid fa-refresh"


class OAuth2TokenAdmin(ModelView, model=OAuth2Token):
    column_list = [
        c.name
        for c in OAuth2Token.__table__.columns
        if c.name not in ["access_token", "refresh_token"]
    ]
    column_details_exclude_list = [OAuth2Token.access_token, OAuth2Token.refresh_token]
    can_delete = False
    can_create = False
    can_edit = False
    name = "Oauth2 токен"
    name_plural = "Oauth2 токены"
    icon = "fa-solid fa-key"
