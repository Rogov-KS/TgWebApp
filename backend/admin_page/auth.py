from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from starlette.responses import RedirectResponse

from backend.utils.auth import authenticate_admin_user, create_access_token
from backend.core.dependecies import get_current_admin_user_by_token
from backend.core.config import settings
from backend.core.logger import get_logger


logger = get_logger(__name__)


class AdminAuth(AuthenticationBackend):
    def _redirect_to_login(self, request: Request) -> RedirectResponse:
        return RedirectResponse(request.url_for("admin:login"), status_code=302)

    async def login(self, request: Request) -> bool:
        form = await request.form()
        username_or_email, password = form["username"], form["password"]

        user = await authenticate_admin_user(username_or_email, password)

        if user:
            access_token = create_access_token({"sub": str(user.id)})
            request.session.update({"token": access_token})

        return True

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool | RedirectResponse:
        token = request.session.get("token")

        if not token:
            return self._redirect_to_login(request)

        try:
            logger.info("try to get admin user by token", extra={"token": token})
            admin_user = await get_current_admin_user_by_token(token)
        except Exception as e:
            logger.error("Error getting current admin user", exc_info=True)
            return self._redirect_to_login(request)
        logger.info("admin_user login in admin page success")
        if not admin_user:
            return self._redirect_to_login(request)

        return True


authentication_backend = AdminAuth(secret_key=settings.SECRET_KEY)
