from fastapi import APIRouter, Request, Response
from fastapi_versioning import version

from backend.celery_app.tasks.email import send_welcome_email_task
from backend.core.dependecies import CurrentUserDep
from backend.core.logger import get_logger
from backend.entities.auth import utils as auth_utils
from backend.entities.auth.service import AuthServiceDep
from backend.entities.refresh_token.service import RefreshTokenServiceDep
from backend.entities.user.schemas import User, UserAuth, UserLogin

logger = get_logger(__name__)

router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)


@router.post("/register")
@version(1)
async def register(
    user_data: UserAuth,
    auth_service: AuthServiceDep
) -> User:
    """Регистрация нового пользователя."""
    model_user = await auth_service.register_user(user_data)

    # Отправляем приветственное письмо
    if user_data.email:
        logger.info(
            "Try to send welcome email", extra={"email": user_data.email}
        )
        await send_welcome_email_task(
            user_email=user_data.email, username=user_data.username
        )

    return model_user


@router.post("/login")
@version(1)
async def login(
    response: Response,
    user_data: UserLogin,
    auth_service: AuthServiceDep,
    refresh_token_service: RefreshTokenServiceDep,
) -> dict[str, str]:
    """Вход пользователя в систему."""
    return await auth_service.login_user(
        user_data, response, auth_utils, refresh_token_service
    )


@router.post("/refresh")
@version(1)
async def refresh(
    response: Response,
    request: Request,
    auth_service: AuthServiceDep,
    refresh_token_service: RefreshTokenServiceDep,
) -> dict[str, str]:
    """Обновить access token используя refresh token с ротацией
    refresh токена."""
    return await auth_service.refresh_tokens(
        request, response, auth_utils, refresh_token_service
    )


@router.post("/logout")
@version(1)
async def logout(
    response: Response,
    user: CurrentUserDep,
    auth_service: AuthServiceDep,
    refresh_token_service: RefreshTokenServiceDep,
) -> dict[str, str]:
    """Выйти из системы."""
    return await auth_service.logout_user(
        user, response, refresh_token_service
    )


@router.get("/me")
@version(1)
async def get_current_user_info(
    user: CurrentUserDep
) -> User:
    """Получить информацию о текущем пользователе."""
    return user


@router.get("/hello_world")
@version(1)
async def hello_world() -> dict[str, str]:
    """Тестовый эндпоинт."""
    return {"message": "Hello World from Auth!"}
