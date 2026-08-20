# ApexTrack AI — Live Track Condition Intelligence Backend

## Current Phase: Phase 11 & Phase 12 (Backend Foundation + Image Analysis API)

Production-ready backend architecture for **ApexTrack AI**, built with **FastAPI**, **Pydantic v2**, and a clean **Hugging Face ML Inference Boundary**.

---

## 🏗️ System Architecture

```
FRONTEND (Phase 14+)
    │
    │ multipart/form-data
    ▼
FastAPI Application
    │
    ├── /api/v1/health  (Lightweight health check)
    │
    └── /api/v1/analysis/image
          │
          ▼
    AnalysisService
          │
          ├── ImageValidation (MIME, file size, Pillow & OpenCV decoding)
          │
          ├── ImagePreprocessing (RGB conversion, resolution normalization)
          │
          ▼
    TrackConditionPredictor (Abstract Inference Boundary)
          │
          ├── HFTrackConditionPredictor  ──────► [Hugging Face Vision Model — Phase 13]
          │
          ▼
    PredictionResult (dry, damp, wet probabilities)
          │
          ▼
    ImageAnalysisResponse (UUID, timestamp, duration ms, model metadata)
```

---

## 🚀 Running Locally

### 1. Prerequisites
- Python 3.11+
- virtualenv / venv

### 2. Setup Virtual Environment

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configuration

Copy the `.env.example` file to `.env`:

```bash
cp .env.example .env
```

Key environment variables:

| Variable | Default | Description |
|---|---|---|
| `APP_ENV` | `development` | Environment mode (`development`, `production`) |
| `API_V1_PREFIX` | `/api/v1` | Base API prefix |
| `MODEL_ID` | `""` | Hugging Face model identifier (e.g. `organization/model-name`) |
| `MAX_IMAGE_SIZE_MB` | `10` | Maximum allowed image payload size in MB |
| `ALLOWED_ORIGINS` | `http://localhost:3000` | Allowed CORS origins (comma separated) |
| `ENABLE_MOCK_PREDICTOR` | `false` | Enable MockPredictor stub (for dev/tests only) |

### 5. Start the Development Server

```bash
python run.py
```

Or directly using Uvicorn:

```bash
uvicorn app.main:app --reload --port 8000
```

---

## 📖 API Documentation & Endpoints

Interactive Swagger UI documentation is automatically served at:
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **OpenAPI Schema**: [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json)

### 1. Health Check
`GET /api/v1/health`

Response (200 OK):
```json
{
  "status": "healthy",
  "service": "apextrack-ai",
  "version": "1.0.0"
}
```

### 2. Image Track Analysis
`POST /api/v1/analysis/image`

Accepts `multipart/form-data` with field name `file`. Formats supported: `.jpg`, `.jpeg`, `.png`, `.webp`.

Response (200 OK):
```json
{
  "analysis_id": "a3b8e7c1-2d4f-4e6a-8b10-9c8d7e6f5a4b",
  "timestamp": "2026-08-13T11:40:00Z",
  "prediction": {
    "condition": "wet",
    "confidence": 0.91,
    "probabilities": {
      "dry": 0.03,
      "damp": 0.06,
      "wet": 0.91
    }
  },
  "processing_time_ms": 184.2,
  "model": {
    "provider": "huggingface",
    "model_id": "apextrack/track-condition-vit"
  }
}
```

Error Response (503 Service Unavailable when model is unconfigured):
```json
{
  "error": {
    "code": "MODEL_NOT_CONFIGURED",
    "message": "Hugging Face model is not configured. Real inference will be enabled in the ML phase."
  }
}
```

---

## 🧪 Running Automated Tests

Run the full pytest suite:

```bash
pytest
```

Includes test suites for:
- `tests/test_health.py` (Health check)
- `tests/test_validation.py` (Image size, format, MIME type, Pillow & OpenCV decoding, Pydantic schemas)
- `tests/test_analysis.py` (Image endpoint contracts, error responses, dependency overrides with `MockPredictor`)

---

## 🤖 ML Status

> **Notice:** The real Hugging Face vision model will be fine-tuned and integrated in the next ML phase (Phase 13).
> No fake AI predictions are returned. Until `MODEL_ID` is set, the API returns a structured `MODEL_NOT_CONFIGURED` response.
