from fastapi import APIRouter

def versioned_router(version: str) -> APIRouter:
    return APIRouter(prefix=f"/api/{version}")
router = versioned_router("v1")
