from backend.admin_page.view import (
    UsersAdmin,
    GameSessionsAdmin,
    RefreshTokenAdmin,
    OAuth2TokenAdmin,
)
from sqladmin import Admin


def add_views_into_admin(admin: Admin) -> None:
    admin.add_view(UsersAdmin)
    admin.add_view(GameSessionsAdmin)
    admin.add_view(RefreshTokenAdmin)
    admin.add_view(OAuth2TokenAdmin)
