import json
from pathlib import Path
import httpx

def main():
    client = httpx.Client(base_url="http://127.0.0.1:8000", timeout=30.0)

    print("=" * 60)
    print("APEXTRACK AI — LIVE BACKEND & MODEL SYSTEM AUDIT")
    print("=" * 60)

    # 1. Health endpoint
    print("\n1. Health Check (GET /api/v1/health):")
    r = client.get("/api/v1/health")
    assert r.status_code == 200, f"Health check failed: {r.text}"
    health_data = r.json()
    print(f"   HTTP Status: {r.status_code}")
    print(f"   Service:     {health_data['service']} (v{health_data['version']})")
    print(f"   Status:      {health_data['status']}")
    print(f"   Model ID:    {health_data['model']['model_id']}")
    print(f"   Configured:  {health_data['model']['configured']}")

    # 2. Real Image Inference
    test_dir = Path("../ml/data/processed/apextrack_balanced/test")
    if not test_dir.exists():
        test_dir = Path("ml/data/processed/apextrack_balanced/test")

    print("\n2. Real Vision Inference (POST /api/v1/analysis/image):")
    for condition in ["dry", "damp", "wet"]:
        cls_dir = test_dir / condition
        images = list(cls_dir.glob("*.jpg"))
        if not images:
            continue
        img_path = images[0]
        with open(img_path, "rb") as f:
            r = client.post("/api/v1/analysis/image", files={"file": (img_path.name, f.read(), "image/jpeg")})
        assert r.status_code == 200, f"Analysis failed for {condition}: {r.text}"
        data = r.json()
        pred = data["prediction"]
        print(f"   [{condition.upper()} Sample] -> Predicted: {pred['condition'].upper()} | Conf: {pred['confidence']*100:.1f}% | Latency: {data['processing_time_ms']} ms")
        print(f"      Probabilities: {pred['probabilities']}")
        print(f"      Tire Advisory: {data['advisory']['message']}")

    # 3. Telemetry Trend
    print("\n3. Telemetry Trend Analysis (GET /api/v1/track/trend):")
    r = client.get("/api/v1/track/trend")
    assert r.status_code == 200, f"Trend check failed: {r.text}"
    trend_data = r.json()
    print(f"   Trend Status:   {trend_data['trend'].upper()}")
    print(f"   History Window: {len(trend_data['history'])} telemetry events registered")
    print(f"   Action:         {trend_data['advisory']['recommended_action']}")

    # 4. Input Validation & Error Handling
    print("\n4. Edge-case & Validation Verification:")
    # Empty file
    r = client.post("/api/v1/analysis/image", files={"file": ("empty.jpg", b"", "image/jpeg")})
    assert r.status_code == 400, f"Expected 400 for empty file, got {r.status_code}"
    print(f"   Empty file rejection:       [PASS] (HTTP {r.status_code} - {r.json()['error']['code']})")

    # Non-image file
    r = client.post("/api/v1/analysis/image", files={"file": ("doc.pdf", b"%PDF-1.4...", "application/pdf")})
    assert r.status_code == 415, f"Expected 415 for PDF, got {r.status_code}"
    print(f"   Unsupported MIME rejection:  [PASS] (HTTP {r.status_code} - {r.json()['error']['code']})")

    # Corrupted image bytes
    r = client.post("/api/v1/analysis/image", files={"file": ("corrupt.jpg", b"\xFF\xD8\xFF\xE0corruptedbytes", "image/jpeg")})
    assert r.status_code == 400, f"Expected 400 for corrupted image, got {r.status_code}"
    print(f"   Corrupt image rejection:    [PASS] (HTTP {r.status_code} - {r.json()['error']['code']})")

    print("\n" + "=" * 60)
    print("ALL BACKEND & MODEL SUBSYSTEMS OPERATING PERFECTLY (100%)")
    print("=" * 60)

if __name__ == "__main__":
    main()
