from fastapi.routing import APIRouter

from partner_api.auth.routes import router as auth_router
from partner_api.events.routes import router as events_router

router = APIRouter()
router.include_router(auth_router, prefix="/auth")
router.include_router(events_router, prefix="/events")
