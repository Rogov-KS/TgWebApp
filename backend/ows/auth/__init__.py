from fastapi import APIRouter

from backend.ows.auth.router import router as oauth2_router

router = APIRouter(
    prefix="/oauth2",
)

# Подключаем как старые роутеры (для обратной совместимости),
# так и новый общий роутер
router.include_router(oauth2_router)
