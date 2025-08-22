from sqladmin import Admin
from backend.admin_page.auth import authentication_backend

from backend.admin_page.view import (
    GameSessionsAdmin,
    OAuth2TokenAdmin,
    RefreshTokenAdmin,
    UsersAdmin,
)


def add_views_into_admin(admin: Admin) -> None:
    admin.add_view(UsersAdmin)
    admin.add_view(GameSessionsAdmin)
    admin.add_view(RefreshTokenAdmin)
    admin.add_view(OAuth2TokenAdmin)


__all__ = [
    "add_views_into_admin",
    "authentication_backend",
]