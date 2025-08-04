from fastapi import APIRouter

from backend.oauth2.google.router import router as google_router
from backend.oauth2.yandex.router import router as yandex_router


router = APIRouter(
    prefix="/oauth2",
)

router.include_router(google_router)
router.include_router(yandex_router)
