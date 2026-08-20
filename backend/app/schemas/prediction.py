from enum import Enum
from typing import Dict
from pydantic import BaseModel, Field, field_validator, model_validator


class TrackConditionEnum(str, Enum):
    """
    Allowed instantaneous track conditions.
    Note: Temporal states like 'drying' are handled in later temporal analysis phases.
    """

    DRY = "dry"
    DAMP = "damp"
    WET = "wet"


class PredictionResult(BaseModel):
    """
    Schema for model prediction output.
    """

    condition: TrackConditionEnum = Field(
        ..., description="Predicted instantaneous track condition (dry, damp, wet)"
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score for the primary prediction (0.0 to 1.0)",
    )
    probabilities: Dict[str, float] = Field(
        ...,
        description="Probability distribution across all conditions (dry, damp, wet)",
    )

    @field_validator("probabilities")
    @classmethod
    def validate_probabilities(cls, v: Dict[str, float]) -> Dict[str, float]:
        required_keys = {c.value for c in TrackConditionEnum}
        if set(v.keys()) != required_keys:
            raise ValueError(
                f"Probabilities dictionary must contain exactly keys: {required_keys}"
            )
        for label, prob in v.items():
            if not (0.0 <= prob <= 1.0):
                raise ValueError(
                    f"Probability for '{label}' must be between 0.0 and 1.0, got {prob}"
                )
        return v

    @model_validator(mode="after")
    def validate_confidence_and_sum(self) -> "PredictionResult":
        # Validate sum approximately equals 1.0 (allow small floating point tolerance)
        prob_sum = sum(self.probabilities.values())
        if not (0.95 <= prob_sum <= 1.05):
            raise ValueError(
                f"Probabilities must sum to approximately 1.0 (got {prob_sum:.4f})"
            )
        return self

    model_config = {
        "json_schema_extra": {
            "example": {
                "condition": "wet",
                "confidence": 0.91,
                "probabilities": {
                    "dry": 0.03,
                    "damp": 0.06,
                    "wet": 0.91,
                },
            }
        }
    }
