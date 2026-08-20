from fastapi import APIRouter, Depends, File, UploadFile, status
from app.core.config import settings
from app.ml.base import TrackConditionPredictor
from app.ml.predictor import HFTrackConditionPredictor, MockPredictor
from app.schemas.analysis import ErrorResponse, ImageAnalysisResponse
from app.schemas.trend import TrackTrendResponse
from app.services.analysis_service import AnalysisService
from app.services.image_service import ImageService
from app.services.track_trend_service import TrackTrendService, track_trend_service_instance

router = APIRouter()


def get_image_service() -> ImageService:
    """Dependency provider for ImageService."""
    return ImageService()


def get_predictor() -> TrackConditionPredictor:
    """
    Dependency provider for TrackConditionPredictor.
    Injects HFTrackConditionPredictor by default.
    Injects MockPredictor only if ENABLE_MOCK_PREDICTOR configuration is explicitly True.
    """
    if settings.ENABLE_MOCK_PREDICTOR:
        return MockPredictor()
    return HFTrackConditionPredictor()


def get_trend_service() -> TrackTrendService:
    """Dependency provider for TrackTrendService singleton."""
    return track_trend_service_instance


def get_analysis_service(
    image_service: ImageService = Depends(get_image_service),
    predictor: TrackConditionPredictor = Depends(get_predictor),
    trend_service: TrackTrendService = Depends(get_trend_service),
) -> AnalysisService:
    """Dependency provider for AnalysisService."""
    return AnalysisService(
        image_service=image_service,
        predictor=predictor,
        trend_service=trend_service,
    )


@router.post(
    "/analysis/image",
    response_model=ImageAnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze Track Condition Image",
    description=(
        "Upload a track image (JPEG, PNG, WEBP) to perform computer vision analysis. "
        "Returns instantaneous track condition (dry, damp, wet) alongside confidence, probability breakdown, "
        "and updated temporal trend & tire advisory."
    ),
    responses={
        400: {
            "model": ErrorResponse,
            "description": "Invalid image payload or unreadable image file.",
        },
        413: {
            "model": ErrorResponse,
            "description": "Image payload size exceeds allowed limit (MAX_IMAGE_SIZE_MB).",
        },
        415: {
            "model": ErrorResponse,
            "description": "Unsupported image format or MIME type.",
        },
        422: {
            "model": ErrorResponse,
            "description": "Unprocessable upload request or form validation error.",
        },
        503: {
            "model": ErrorResponse,
            "description": "Hugging Face ML model is not configured (MODEL_NOT_CONFIGURED).",
        },
    },
    tags=["Analysis"],
)
async def analyze_image_endpoint(
    file: UploadFile = File(
        ...,
        description="Track condition image file (JPEG, PNG, WEBP format, max 10MB)",
    ),
    analysis_service: AnalysisService = Depends(get_analysis_service),
) -> ImageAnalysisResponse:
    """
    HTTP POST handler for track image analysis.
    """
    return await analysis_service.analyze_image(file)


@router.get(
    "/track/trend",
    response_model=TrackTrendResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Track Condition Trend & History",
    description="Returns chronological sequence of recent reliable predictions, calculated trend state, and tactical tire advisory.",
    tags=["Analysis"],
)
@router.get(
    "/analysis/history",
    response_model=TrackTrendResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Analysis History & Trend",
    description="Alias endpoint for retrieving historical track condition telemetry and trend analysis.",
    tags=["Analysis"],
)
async def get_track_trend_endpoint(
    trend_service: TrackTrendService = Depends(get_trend_service),
) -> TrackTrendResponse:
    """
    HTTP GET handler for track condition trend and prediction history telemetry.
    """
    return trend_service.get_trend_response()
