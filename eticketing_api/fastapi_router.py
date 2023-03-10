from fastapi import APIRouter

from partner_api.router import router as partner_api

router = APIRouter()
router.include_router(partner_api)
