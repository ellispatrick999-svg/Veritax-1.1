from fastapi import APIRouter

from user_api import router as user_router
from tax_api import router as tax_router
from ai_api import router as ai_router
from health import router as health_router

api_router = APIRouter()

api_router.include_router(health_router, tags=["health"])
api_router.include_router(user_router, prefix="/users", tags=["users"])
api_router.include_router(tax_router, prefix="/tax", tags=["tax"])
api_router.include_router(ai_router, prefix="/ai", tags=["ai"])
