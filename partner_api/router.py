from fastapi.routing import APIRouter

from partner_api.auth.routes import router as auth_router

router = APIRouter()
router.include_router(auth_router, prefix="/auth")
