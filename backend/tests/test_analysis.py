import io
from PIL import Image
from fastapi.testclient import TestClient

from app.api.v1.analysis import get_predictor
from app.core.exceptions import ModelNotConfiguredException
from app.main import app
from app.ml.base import TrackConditionPredictor
from app.ml.predictor import MockPredictor
from app.schemas.analysis import ModelMetadata
from app.schemas.prediction import PredictionResult, TrackConditionEnum
from app.services.track_trend_service import track_trend_service_instance

client = TestClient(app)


def create_sample_image_bytes(format_name: str = "JPEG", size: tuple = (100, 100)) -> bytes:
    """Helper to generate valid image bytes in memory."""
    img = Image.new("RGB", size, color="red")
    buf = io.BytesIO()
    img.save(buf, format=format_name)
    return buf.getvalue()


class UnconfiguredPredictorStub(TrackConditionPredictor):
    def predict(self, image: Image.Image) -> PredictionResult:
        raise ModelNotConfiguredException("No Hugging Face model ID or path specified in configuration.")

    def get_model_info(self) -> ModelMetadata:
        return ModelMetadata(provider="huggingface", model_id="unconfigured")


def test_analyze_image_model_not_configured():
    """
    Test uploading a valid image when Hugging Face model is unconfigured.
    Should return 503 Service Unavailable with MODEL_NOT_CONFIGURED error code.
    """
    app.dependency_overrides[get_predictor] = lambda: UnconfiguredPredictorStub()
    try:
        image_bytes = create_sample_image_bytes("JPEG")
        files = {"file": ("test_track.jpg", image_bytes, "image/jpeg")}

        response = client.post("/api/v1/analysis/image", files=files)
        assert response.status_code == 503
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == "MODEL_NOT_CONFIGURED"
    finally:
        app.dependency_overrides.clear()


def test_analyze_image_with_injected_mock_predictor():
    """
    Test uploading a valid image with injected MockPredictor for test verification.
    Verifies full ImageAnalysisResponse schema contract including trend and advisory.
    """
    track_trend_service_instance.clear_history()

    mock_stub = MockPredictor(
        condition=TrackConditionEnum.DAMP,
        confidence=0.88,
        probabilities={"dry": 0.05, "damp": 0.88, "wet": 0.07},
    )

    app.dependency_overrides[get_predictor] = lambda: mock_stub

    try:
        image_bytes = create_sample_image_bytes("PNG")
        files = {"file": ("track_session_1.png", image_bytes, "image/png")}

        response = client.post("/api/v1/analysis/image", files=files)
        assert response.status_code == 200
        data = response.json()

        assert "analysis_id" in data
        assert "timestamp" in data
        assert "processing_time_ms" in data
        assert data["processing_time_ms"] >= 0

        # Prediction schema verification
        pred = data["prediction"]
        assert pred["condition"] == "damp"
        assert pred["confidence"] == 0.88
        assert pred["probabilities"]["damp"] == 0.88

        # Model metadata verification
        assert data["model"]["provider"] == "mock-test-stub"

        # Trend & advisory verification
        assert "trend" in data
        assert "advisory" in data
        assert "severity" in data["advisory"]
        assert "message" in data["advisory"]
        assert "recommended_action" in data["advisory"]
    finally:
        app.dependency_overrides.clear()


def test_get_track_trend_endpoint():
    """
    Test GET /api/v1/track/trend returns history and advisory telemetry.
    """
    response = client.get("/api/v1/track/trend")
    assert response.status_code == 200
    data = response.json()
    assert "history" in data
    assert "trend" in data
    assert "advisory" in data


def test_analyze_image_invalid_text_file():
    """
    Test uploading a text file masked as an image MIME type.
    Should return 400 INVALID_IMAGE.
    """
    files = {"file": ("document.jpg", b"This is plain text file content.", "image/jpeg")}
    response = client.post("/api/v1/analysis/image", files=files)
    assert response.status_code == 400
    data = response.json()
    assert data["error"]["code"] == "INVALID_IMAGE"


def test_analyze_image_empty_file():
    """
    Test uploading an empty file.
    Should return 400 EMPTY_FILE.
    """
    files = {"file": ("empty.jpg", b"", "image/jpeg")}
    response = client.post("/api/v1/analysis/image", files=files)
    assert response.status_code == 400
    data = response.json()
    assert data["error"]["code"] == "EMPTY_FILE"


def test_analyze_image_unsupported_mime():
    """
    Test uploading file with unsupported MIME type.
    Should return 415 UNSUPPORTED_IMAGE_TYPE.
    """
    files = {"file": ("document.pdf", b"%PDF-1.4 test data", "application/pdf")}
    response = client.post("/api/v1/analysis/image", files=files)
    assert response.status_code == 415
    data = response.json()
    assert data["error"]["code"] == "UNSUPPORTED_IMAGE_TYPE"


def test_analyze_image_corrupted_image_bytes():
    """
    Test uploading corrupted image file header/bytes.
    Should return 400 INVALID_IMAGE.
    """
    corrupted_bytes = b"\xFF\xD8\xFF\xE0\x00\x10JFIF corrupted garbage data string"
    files = {"file": ("corrupt.jpg", corrupted_bytes, "image/jpeg")}
    response = client.post("/api/v1/analysis/image", files=files)
    assert response.status_code == 400
    data = response.json()
    assert data["error"]["code"] == "INVALID_IMAGE"
