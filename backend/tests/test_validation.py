import io
import pytest
from PIL import Image
from pydantic import ValidationError

from app.core.exceptions import (
    EmptyFileException,
    ImageTooLargeException,
    InvalidImageException,
    UnsupportedImageTypeException,
)
from app.schemas.prediction import PredictionResult, TrackConditionEnum
from app.utils.file_validation import validate_image_file


def create_sample_image_bytes(format_name: str = "PNG", size: tuple = (100, 100)) -> bytes:
    """Helper to generate valid image bytes in memory."""
    img = Image.new("RGB", size, color="blue")
    buf = io.BytesIO()
    img.save(buf, format=format_name)
    return buf.getvalue()


def test_validate_image_file_valid():
    content = create_sample_image_bytes("PNG")
    pil_img, metadata = validate_image_file(content, content_type="image/png")
    assert pil_img is not None
    assert metadata["format"] == "PNG"
    assert metadata["width"] == 100
    assert metadata["height"] == 100


def test_validate_image_file_empty():
    with pytest.raises(EmptyFileException):
        validate_image_file(b"")


def test_validate_image_file_oversized(monkeypatch):
    from app.core.config import settings
    monkeypatch.setattr(settings, "MAX_IMAGE_SIZE_MB", 0)  # max size 0 bytes
    content = create_sample_image_bytes("PNG")
    with pytest.raises(ImageTooLargeException):
        validate_image_file(content)


def test_validate_image_file_invalid_bytes():
    with pytest.raises(InvalidImageException):
        validate_image_file(b"This is plain text, not an image file.")


def test_validate_image_file_unsupported_mime():
    content = create_sample_image_bytes("PNG")
    with pytest.raises(UnsupportedImageTypeException):
        validate_image_file(content, content_type="application/pdf")


def test_prediction_result_schema_valid():
    result = PredictionResult(
        condition=TrackConditionEnum.WET,
        confidence=0.91,
        probabilities={"dry": 0.03, "damp": 0.06, "wet": 0.91},
    )
    assert result.condition == TrackConditionEnum.WET
    assert result.confidence == 0.91


def test_prediction_result_schema_invalid_confidence():
    with pytest.raises(ValidationError):
        PredictionResult(
            condition=TrackConditionEnum.WET,
            confidence=1.5,  # > 1.0 invalid
            probabilities={"dry": 0.0, "damp": 0.0, "wet": 1.0},
        )

    with pytest.raises(ValidationError):
        PredictionResult(
            condition=TrackConditionEnum.WET,
            confidence=-0.1,  # < 0.0 invalid
            probabilities={"dry": 0.0, "damp": 0.0, "wet": 1.0},
        )


def test_prediction_result_schema_invalid_probabilities_sum():
    with pytest.raises(ValidationError):
        PredictionResult(
            condition=TrackConditionEnum.WET,
            confidence=0.5,
            probabilities={"dry": 0.1, "damp": 0.1, "wet": 0.1},  # Sums to 0.3 != ~1.0
        )
