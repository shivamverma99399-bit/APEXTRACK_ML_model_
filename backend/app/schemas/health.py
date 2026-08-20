from typing import Optional
from pydantic import BaseModel, Field


class ModelHealthStatus(BaseModel):
    configured: bool = Field(..., description="Whether a model identifier or path is configured")
    provider: str = Field(default="huggingface", description="Model provider")
    model_id: str = Field(default="unconfigured", description="Target model identifier or path")
    model_config = {"protected_namespaces": ()}


class HealthResponse(BaseModel):
    """
    Schema for health check endpoint response.
    """

    status: str = Field(default="healthy", description="Current health status")
    service: str = Field(default="ApexTrack AI API", description="Service identifier")
    version: str = Field(default="1.0.0", description="API version")
    model: Optional[ModelHealthStatus] = Field(default=None, description="ML Model health and configuration status")

    model_config = {
        "json_schema_extra": {
            "example": {
                "status": "healthy",
                "service": "ApexTrack AI API",
                "version": "1.0.0",
                "model": {
                    "configured": True,
                    "provider": "huggingface",
                    "model_id": "apextrack-track-condition-v2",
                },
            }
        }
    }
