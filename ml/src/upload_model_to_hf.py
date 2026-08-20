import os
import sys
from pathlib import Path
from huggingface_hub import HfApi, create_repo, upload_folder

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

# Detect local model directory
if Path("models/apextrack-vit-v2").exists():
    LOCAL_MODEL_DIR = Path("models/apextrack-vit-v2")
elif Path("ml/models/apextrack-vit-v2").exists():
    LOCAL_MODEL_DIR = Path("ml/models/apextrack-vit-v2")
else:
    raise FileNotFoundError("Could not find local model directory models/apextrack-vit-v2")

# Model card template
MODEL_CARD_CONTENT = """---
language:
- en
license: mit
tags:
- vision
- image-classification
- vit
- racing
- motorsport
- track-condition
- apex-track
datasets:
- mrcreoid/weather-whiplash-surfaces
metrics:
- accuracy
- f1
pipeline_tag: image-classification
---

# ApexTrack AI — Track Condition Classifier V2

ApexTrack AI is a computer vision model for live racing track condition classification (`dry`, `damp`, `wet`). It powers dynamic strategy decision-support systems for race engineers and simulation platforms.

## Model Overview
- **Architecture**: Vision Transformer (ViT-Base, `google/vit-base-patch16-224-in21k`)
- **Task**: 3-Class Image Classification (`dry`, `damp`, `wet`)
- **Input Resolution**: 224x224 RGB images
- **Labels**:
  - `0`: `damp`
  - `1`: `dry`
  - `2`: `wet`

## Dataset & Training
- **Source Dataset**: Weather Whiplash Surfaces (Real road & asphalt track surface conditions)
- **Dataset Size**: 190 original annotated images split into train (131), validation (27), and test (32).
- **V2 Balancing**: Controlled, conservative image augmentation was applied **ONLY to the training split** (bringing each training class to exactly 100 images = 300 total training images).
- **Validation & Test Sets**: Remained **100% untouched and unaugmented** to guarantee zero data leakage and honest evaluation.

## Performance Metrics (Evaluated on Untouched Test Set)
- **Accuracy**: 43.75%
- **Macro F1**: 40.78%
- **Weighted F1**: 42.51%

### Per-Class Performance
| Class | Precision | Recall | F1-Score |
| :--- | :--- | :--- | :--- |
| **Dry** | 50.00% | 72.73% | 59.26% |
| **Damp** | 22.22% | 28.57% | 25.00% |
| **Wet** | 57.14% | 28.57% | 38.10% |

## Note on "Drying" Condition
"Drying" is **not** an image classification class. Instead, track drying is inferred temporally by the ApexTrack AI backend engine across sequential live predictions (e.g. `wet` → `damp` → `dry`).

## Limitations & Disclaimer
- **Prototype Status**: This is an educational/hackathon prototype trained on a compact dataset.
- **Decision Support**: Predictions are designed for advisory decision support and should not be used in safety-critical autonomous control systems without human verification.
"""


def upload_model():
    print("=" * 60)
    print("APEXTRACK AI — HUGGING FACE MODEL REPOSITORY UPLOADER")
    print("=" * 60)

    token = os.getenv("HF_TOKEN")
    hf_username = os.getenv("HF_USERNAME")
    repo_id = os.getenv("HF_MODEL_ID")

    api = HfApi(token=token)

    # Determine authenticated user
    try:
        user_info = api.whoami(token=token)
        actual_username = user_info.get("name") or user_info.get("fullname")
        print(f"Authenticated as Hugging Face user: {actual_username}")
    except Exception as e:
        print(f"\nAuthentication check failed or token missing: {e}")
        actual_username = hf_username

    if not repo_id:
        if not actual_username:
            print("\nError: Please set HF_TOKEN or HF_USERNAME / HF_MODEL_ID in your environment.")
            sys.exit(1)
        repo_id = f"{actual_username}/apextrack-track-condition-v2"

    print(f"\nTarget Hugging Face Repository: {repo_id}")
    print(f"Source Model Directory:         {LOCAL_MODEL_DIR.resolve()}\n")

    # Verify required local model files exist
    required_files = ["config.json", "model.safetensors", "preprocessor_config.json"]
    for req_f in required_files:
        if not (LOCAL_MODEL_DIR / req_f).exists():
            raise FileNotFoundError(f"Missing required model artifact: {LOCAL_MODEL_DIR / req_f}")

    # Write Model Card README.md in model dir
    readme_path = LOCAL_MODEL_DIR / "README.md"
    readme_path.write_text(MODEL_CARD_CONTENT, encoding="utf-8")
    print("Model Card README.md generated.")

    # Create repository on HF Hub if not exists
    print(f"Creating/verifying repository '{repo_id}' on Hugging Face Hub...")
    try:
        create_repo(
            repo_id=repo_id,
            token=token,
            repo_type="model",
            exist_ok=True,
            private=False,
        )
        print("Repository verified on Hugging Face Hub.")
    except Exception as e:
        print(f"Note on repo creation: {e}")

    # Upload model files
    print("Uploading model artifacts to Hugging Face Hub...")
    upload_folder(
        folder_path=str(LOCAL_MODEL_DIR),
        repo_id=repo_id,
        repo_type="model",
        token=token,
        allow_patterns=["config.json", "model.safetensors", "preprocessor_config.json", "README.md", "*.json"],
        ignore_patterns=["checkpoint-*", "*.png", "*.bin", "__pycache__/*"],
    )

    print("\n" + "=" * 60)
    print("UPLOAD COMPLETED SUCCESSFULLY!")
    print(f"Hugging Face Model ID: {repo_id}")
    print(f"View online at:        https://huggingface.co/{repo_id}")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    upload_model()
