import os
import sys
from pathlib import Path
from PIL import Image
import torch
import torch.nn.functional as F
from transformers import AutoImageProcessor, AutoModelForImageClassification
# Manual / fallback .env loader
def load_env_file():
    for env_path in [Path(".env"), Path("../.env"), Path("../backend/.env")]:
        if env_path.exists():
            for line in env_path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    k, v = k.strip(), v.strip().strip("'\"")
                    if k and k not in os.environ:
                        os.environ[k] = v

load_env_file()

# Determine model target
HF_MODEL_ID = os.getenv("HF_MODEL_ID")
LOCAL_MODEL_PATH = "models/apextrack-vit-v2" if Path("models/apextrack-vit-v2").exists() else "ml/models/apextrack-vit-v2"
TARGET_MODEL = HF_MODEL_ID or LOCAL_MODEL_PATH


def test_model_load():
    print("=" * 60)
    print("APEXTRACK AI — MODEL LOADING & INFERENCE VERIFICATION")
    print("=" * 60)
    print(f"Target Model: {TARGET_MODEL}\n")

    token = os.getenv("HF_TOKEN")

    print("Loading image processor...")
    try:
        processor = AutoImageProcessor.from_pretrained(TARGET_MODEL, token=token)
        print("[OK] Image processor loaded successfully.")
    except Exception as e:
        print(f"[FAIL] Error loading image processor: {e}")
        sys.exit(1)

    print("\nLoading classification model...")
    try:
        model = AutoModelForImageClassification.from_pretrained(TARGET_MODEL, token=token)
        model.eval()
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model.to(device)
        print(f"[OK] Model loaded successfully on device: {device}")
    except Exception as e:
        print(f"[FAIL] Error loading model: {e}")
        sys.exit(1)

    # Inspect label mapping
    id2label = getattr(model.config, "id2label", {})
    print("\nLabels configured:")
    for idx, name in sorted(id2label.items(), key=lambda x: int(x[0])):
        print(f"  {idx} -> {name}")

    # Find sample test image
    test_dirs = [
        Path("data/processed/apextrack_balanced/test"),
        Path("ml/data/processed/apextrack_balanced/test"),
    ]
    test_root = next((d for d in test_dirs if d.exists()), None)
    if not test_root:
        print("\nWarning: Test directory not found, using a test RGB image.")
        sample_img = Image.new("RGB", (224, 224), color=(100, 100, 100))
        img_source_desc = "Synthetic RGB test canvas"
    else:
        # Pick a real test image from each class
        sample_files = list(test_root.rglob("*.jpg"))
        if sample_files:
            sample_img_path = sample_files[0]
            sample_img = Image.open(sample_img_path).convert("RGB")
            img_source_desc = str(sample_img_path)
        else:
            sample_img = Image.new("RGB", (224, 224), color=(100, 100, 100))
            img_source_desc = "Synthetic RGB test canvas"

    print(f"\nRunning test inference on: {img_source_desc}")
    inputs = processor(sample_img, return_tensors="pt")
    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        probs = F.softmax(logits, dim=-1).squeeze().tolist()

    if isinstance(probs, float):
        probs = [probs]

    probabilities_dict = {"dry": 0.0, "damp": 0.0, "wet": 0.0}
    for idx, prob_val in enumerate(probs):
        label_name = str(id2label.get(idx, idx)).lower().strip()
        if label_name in probabilities_dict:
            probabilities_dict[label_name] = round(float(prob_val), 4)

    best_condition = max(probabilities_dict, key=probabilities_dict.get)
    confidence = probabilities_dict[best_condition]

    print("\nINFERENCE RESULTS:")
    print("-" * 40)
    print(f"Predicted Condition: {best_condition.upper()}")
    print(f"Confidence:          {confidence * 100:.2f}%")
    print(f"Probabilities:")
    for cls, p in probabilities_dict.items():
        bar = "#" * int(p * 20)
        print(f"  {cls:<6}: {p * 100:>6.2f}% | {bar}")

    print("-" * 40)
    print("MODEL LOAD & INFERENCE TEST PASSED SUCCESSFULLY!\n" + "=" * 60)


if __name__ == "__main__":
    test_model_load()
