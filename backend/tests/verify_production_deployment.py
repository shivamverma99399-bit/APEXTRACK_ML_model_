import io
import json
import httpx
from PIL import Image
from huggingface_hub import hf_hub_download

def test_production():
    backend_url = "https://apextrack-ml-model.onrender.com"
    frontend_url = "https://apextrack-ml-model.vercel.app"

    print("=" * 60)
    print("APEXTRACK AI — LIVE PRODUCTION DEPLOYMENT VERIFICATION")
    print("=" * 60)
    print(f"Backend URL:  {backend_url}")
    print(f"Frontend URL: {frontend_url}\n")

    client = httpx.Client(timeout=90.0)

    # 1. Health Check
    print("1. Testing GET /api/v1/health on Render...")
    try:
        r_health = client.get(f"{backend_url}/api/v1/health")
        print(f"   Status: {r_health.status_code}")
        print(f"   Body:   {r_health.text}")
        assert r_health.status_code == 200, f"Health check failed with {r_health.status_code}"
    except Exception as e:
        print(f"   [FAIL] Health check error: {e}")
        return

    # 2. CORS Options Preflight Check
    print("\n2. Testing CORS headers for Vercel origin...")
    try:
        r_cors = client.options(
            f"{backend_url}/api/v1/analysis/image",
            headers={
                "Origin": frontend_url,
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "content-type",
            },
        )
        print(f"   CORS Status: {r_cors.status_code}")
        print(f"   Access-Control-Allow-Origin:      {r_cors.headers.get('access-control-allow-origin')}")
        print(f"   Access-Control-Allow-Credentials: {r_cors.headers.get('access-control-allow-credentials')}")
    except Exception as e:
        print(f"   [WARNING] CORS error: {e}")

    # 3. Real Vision Inference on Production Render
    print("\n3. Testing POST /api/v1/analysis/image on Render...")
    try:
        sample_path = hf_hub_download(
            repo_id="yuvrajengines/apextrack-track-condition-dataset",
            filename="test/dry/dry_0041.jpg",
            repo_type="dataset",
        )
        with open(sample_path, "rb") as f:
            img_bytes = f.read()

        files = {"file": ("dry_0041.jpg", img_bytes, "image/jpeg")}
        r_analysis = client.post(
            f"{backend_url}/api/v1/analysis/image",
            files=files,
            headers={"Origin": frontend_url},
        )
        print(f"   Status Code: {r_analysis.status_code}")
        if r_analysis.status_code == 200:
            data = r_analysis.json()
            print(f"   Analysis ID:        {data.get('analysis_id')}")
            print(f"   Condition:          {data.get('prediction', {}).get('condition')}")
            print(f"   Confidence:         {data.get('prediction', {}).get('confidence')}")
            print(f"   Model ID:           {data.get('model', {}).get('model_id')}")
            print(f"   Processing Time:    {data.get('processing_time_ms')} ms")
            print(f"   Tire Advisory:      {data.get('advisory', {}).get('message')}")
        else:
            print(f"   Response Body: {r_analysis.text}")
    except Exception as e:
        print(f"   [FAIL] Analysis request error: {e}")

    # 4. Trend Endpoint
    print("\n4. Testing GET /api/v1/track/trend on Render...")
    try:
        r_trend = client.get(f"{backend_url}/api/v1/track/trend", headers={"Origin": frontend_url})
        print(f"   Status Code: {r_trend.status_code}")
        print(f"   Trend State: {r_trend.json().get('trend')}")
    except Exception as e:
        print(f"   [FAIL] Trend endpoint error: {e}")

    # 5. Vercel Frontend Smoke Test
    print("\n5. Testing Vercel Frontend Web App...")
    try:
        r_fe = client.get(frontend_url)
        print(f"   Frontend Status: {r_fe.status_code}")
        assert r_fe.status_code == 200, f"Frontend returned {r_fe.status_code}"
        print(f"   Title in HTML:   {'ApexTrack' in r_fe.text or 'APEXTRACK' in r_fe.text}")
    except Exception as e:
        print(f"   [FAIL] Frontend error: {e}")

    print("\n" + "=" * 60)
    print("PRODUCTION VERIFICATION RUN COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    test_production()
