from fastapi import APIRouter

from backend.ows.auth.common_router import router as common_router

router = APIRouter(
    prefix="/oauth2",
)

# Подключаем как старые роутеры (для обратной совместимости),
# так и новый общий роутер
router.include_router(common_router)
