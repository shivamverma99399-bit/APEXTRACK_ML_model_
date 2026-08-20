from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field
from app.schemas.prediction import PredictionResult
from app.schemas.trend import TireAdvisory, TrendEnum


class ModelMetadata(BaseModel):
    """
    Metadata about the ML model used for analysis.
    """

    provider: str = Field(
        default="huggingface", description="Model provider/source"
    )
    model_id: str = Field(
        default="unconfigured", description="Hugging Face model identifier or path"
    )

    model_config = {"protected_namespaces": ()}


class ImageAnalysisResponse(BaseModel):
    """
    API Response schema for image analysis endpoint POST /api/v1/analysis/image.
    """

    analysis_id: UUID = Field(
        ..., description="Unique analysis identifier (UUID)"
    )
    timestamp: datetime = Field(
        ..., description="Timestamp of analysis completion (ISO 8601 UTC)"
    )
    prediction: PredictionResult = Field(
        ..., description="Instantaneous track condition prediction result"
    )
    processing_time_ms: float = Field(
        ..., description="Total image processing & inference duration in milliseconds"
    )
    model: ModelMetadata = Field(
        ..., description="Information regarding the ML model"
    )
    trend: Optional[TrendEnum] = Field(
        default=None, description="Current computed temporal trend state"
    )
    advisory: Optional[TireAdvisory] = Field(
        default=None, description="Tactical decision-support tire advisory"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "analysis_id": "a3b8e7c1-2d4f-4e6a-8b10-9c8d7e6f5a4b",
                "timestamp": "2026-08-14T10:00:00Z",
                "prediction": {
                    "condition": "wet",
                    "confidence": 0.91,
                    "probabilities": {
                        "dry": 0.03,
                        "damp": 0.06,
                        "wet": 0.91,
                    },
                },
                "processing_time_ms": 184.2,
                "model": {
                    "provider": "huggingface",
                    "model_id": "apextrack/apextrack-track-condition-v2",
                },
                "trend": "drying",
                "advisory": {
                    "severity": "medium",
                    "message": "Track is drying. Tire-change window may be approaching.",
                    "recommended_action": "Prepare intermediate or slick tire change window.",
                },
            }
        }
    }


class ErrorDetail(BaseModel):
    code: str = Field(..., description="Machine-readable error code")
    message: str = Field(..., description="Human-readable error explanation")


class ErrorResponse(BaseModel):
    error: ErrorDetail

    model_config = {
        "json_schema_extra": {
            "example": {
                "error": {
                    "code": "INVALID_IMAGE",
                    "message": "The uploaded file is not a valid image.",
                }
            }
        }
    }
