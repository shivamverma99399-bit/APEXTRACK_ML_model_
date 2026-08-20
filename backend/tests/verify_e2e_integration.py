import sys
from pathlib import Path

backend_root = Path(__file__).resolve().parent.parent
if str(backend_root) not in sys.path:
    sys.path.insert(0, str(backend_root))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def run_e2e_verification():
    print("=" * 60)
    print("APEXTRACK AI — END-TO-END SYSTEM INTEGRATION VERIFICATION")
    print("=" * 60)

    # 1. Health Check
    print("\n1. Testing GET /api/v1/health...")
    health_resp = client.get("/api/v1/health")
    assert health_resp.status_code == 200, f"Health check failed: {health_resp.text}"
    health_data = health_resp.json()
    print(f"   Status:  {health_data['status']}")
    print(f"   Service: {health_data['service']}")
    print(f"   Model Configured: {health_data['model']['configured']}")
    print(f"   Model Target:     {health_data['model']['model_id']}")

    # 2. Test Real Image Predictions
    test_base = Path("../ml/data/processed/apextrack_balanced/test")
    if not test_base.exists():
        test_base = Path("ml/data/processed/apextrack_balanced/test")

    classes = ["dry", "damp", "wet"]
    print("\n2. Testing Real Image Inferences (POST /api/v1/analysis/image)...")

    sample_images = {
        "dry": "dry_0041.jpg",
        "damp": "damp_0006.jpg",
        "wet": "wet_0177.jpg",
    }

    for cls in classes:
        test_img_path = None
        if test_base.exists():
            cls_dir = test_base / cls
            images = list(cls_dir.glob("*.jpg"))
            if images:
                test_img_path = images[0]

        if test_img_path and test_img_path.exists():
            with open(test_img_path, "rb") as f:
                img_bytes = f.read()
            img_name = test_img_path.name
        else:
            # Fallback: Download sample from Hugging Face Dataset Hub
            from huggingface_hub import hf_hub_download
            filename = f"test/{cls}/{sample_images[cls]}"
            cached_path = hf_hub_download(
                repo_id="yuvrajengines/apextrack-track-condition-dataset",
                filename=filename,
                repo_type="dataset",
            )
            with open(cached_path, "rb") as f:
                img_bytes = f.read()
            img_name = sample_images[cls]

        files = {"file": (img_name, img_bytes, "image/jpeg")}

        resp = client.post("/api/v1/analysis/image", files=files)
        assert resp.status_code == 200, f"Analysis failed: {resp.text}"
        data = resp.json()

        pred = data["prediction"]
        print(f"\n   [Image: {img_name} | Ground Truth: {cls.upper()}]")
        print(f"   Predicted Condition: {pred['condition'].upper()}")
        print(f"   Confidence:          {pred['confidence'] * 100:.2f}%")
        print(f"   Probabilities:       Dry={pred['probabilities']['dry']*100:.1f}%, Damp={pred['probabilities']['damp']*100:.1f}%, Wet={pred['probabilities']['wet']*100:.1f}%")
        print(f"   Processing Time:     {data['processing_time_ms']} ms")
        print(f"   Model ID:            {data['model']['model_id']}")
        print(f"   Current Trend:       {data['trend']}")
        print(f"   Tire Advisory:       [{data['advisory']['severity'].upper()}] {data['advisory']['message']}")

    # 3. Test Trend Endpoint
    print("\n3. Testing GET /api/v1/track/trend...")
    trend_resp = client.get("/api/v1/track/trend")
    assert trend_resp.status_code == 200
    trend_data = trend_resp.json()
    print(f"   Telemetry History Count: {len(trend_data['history'])}")
    print(f"   Aggregate Trend State:   {trend_data['trend'].upper()}")
    print(f"   Active Tire Advisory:    {trend_data['advisory']['message']}")
    print(f"   Recommended Action:      {trend_data['advisory']['recommended_action']}")

    print("\n" + "=" * 60)
    print("END-TO-END VERIFICATION COMPLETED WITH 100% SUCCESS!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    run_e2e_verification()
