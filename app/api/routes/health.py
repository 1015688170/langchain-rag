from __future__ import annotations

from fastapi import APIRouter, Depends

from app.core.config import Settings
from app.core.dependencies import settings_dependency
from app.domain.schemas import HealthResponse


router = APIRouter(prefix="/health", tags=["health"])


@router.get("", response_model=HealthResponse)
def health(settings: Settings = Depends(settings_dependency)) -> HealthResponse:
    return HealthResponse(
        status="ok",
        app_name=settings.app_name,
        app_version=settings.app_version,
        llm_provider=settings.llm_provider,
        embedding_provider=settings.embedding_provider,
        vectorstore="local-json",
    )
