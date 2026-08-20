from fastapi import APIRouter, status
from app.core.config import settings
from app.ml.model_loader import HFModelLoader
from app.schemas.health import HealthResponse, ModelHealthStatus

router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Application Health Check",
    description="Returns service status, API version, and safe model configuration status.",
    tags=["System"],
)
async def health_check() -> HealthResponse:
    """
    Lightweight health check endpoint returning service and model configuration status.
    """
    is_configured = HFModelLoader.is_configured()
    target_id = HFModelLoader.get_configured_model_target() or "unconfigured"

    model_health = ModelHealthStatus(
        configured=is_configured,
        provider="huggingface",
        model_id=target_id,
    )

    return HealthResponse(
        status="healthy",
        service=settings.APP_NAME,
        version=settings.APP_VERSION,
        model=model_health,
    )
