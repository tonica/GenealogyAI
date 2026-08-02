from typing import Any

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.core.config import get_settings

router = APIRouter()


@router.get("/health", tags=["system"])
async def health_check() -> JSONResponse:
    """Endpoint de comprobacion de salud."""
    settings = get_settings()
    payload: dict[str, Any] = {
        "status": "ok",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }
    return JSONResponse(content=payload)
