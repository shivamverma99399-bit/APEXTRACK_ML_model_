from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_endpoint_success():
    """
    Test GET /api/v1/health returns 200 and expected payload structure.
    """
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "service" in data
    assert "version" in data
    assert "model" in data
    assert "configured" in data["model"]
    assert "provider" in data["model"]
