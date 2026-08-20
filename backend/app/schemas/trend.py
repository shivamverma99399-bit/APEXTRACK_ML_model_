from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field
from app.schemas.prediction import TrackConditionEnum


class TrendEnum(str, Enum):
    """
    Temporal track condition trend states derived across sequential predictions.
    """
    STABLE = "stable"
    DRYING = "drying"
    WETTING = "wetting"
    INSUFFICIENT_DATA = "insufficient_data"


class TireAdvisory(BaseModel):
    """
    Decision support tire advisory payload.
    """
    severity: str = Field(..., description="Advisory severity: low, medium, high")
    message: str = Field(..., description="Tactical decision support advisory message")
    recommended_action: str = Field(..., description="Recommended engineering / strategy action")

    model_config = {
        "json_schema_extra": {
            "example": {
                "severity": "medium",
                "message": "Track is drying. Tire-change window may be approaching.",
                "recommended_action": "Monitor intermediate to slick crossover lap times."
            }
        }
    }


class HistoryItem(BaseModel):
    """
    Single recorded track condition snapshot in telemetry history.
    """
    timestamp: datetime = Field(..., description="UTC timestamp of the observation")
    condition: TrackConditionEnum = Field(..., description="Observed track condition")
    confidence: float = Field(..., description="Prediction confidence score (0.0 to 1.0)")


class TrackTrendResponse(BaseModel):
    """
    Schema for GET /api/v1/track/trend and GET /api/v1/analysis/history.
    """
    history: List[HistoryItem] = Field(default_factory=list, description="Recent reliable prediction history")
    trend: TrendEnum = Field(..., description="Computed temporal trend state")
    advisory: TireAdvisory = Field(..., description="Decision support tire advisory")

    model_config = {
        "json_schema_extra": {
            "example": {
                "history": [
                    {"timestamp": "2026-08-14T10:00:00Z", "condition": "wet", "confidence": 0.84},
                    {"timestamp": "2026-08-14T10:01:00Z", "condition": "damp", "confidence": 0.72},
                    {"timestamp": "2026-08-14T10:02:00Z", "condition": "dry", "confidence": 0.65},
                ],
                "trend": "drying",
                "advisory": {
                    "severity": "medium",
                    "message": "Track is approaching dry conditions. Monitor tire-change timing.",
                    "recommended_action": "Consider transition to dry compound as dry line emerges."
                }
            }
        }
    }
