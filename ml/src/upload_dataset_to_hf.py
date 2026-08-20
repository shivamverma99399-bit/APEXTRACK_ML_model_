import os
from pathlib import Path
from dotenv import load_dotenv
from huggingface_hub import HfApi

# Load credentials
load_dotenv(Path("backend/.env"))
load_dotenv(Path("ml/.env"))

token = os.getenv("HF_TOKEN")
repo_id = "yuvrajengines/apextrack-track-condition-dataset"
dataset_folder = Path("ml/data/processed/apextrack_balanced")

if not dataset_folder.exists():
    raise FileNotFoundError(f"Dataset folder {dataset_folder} not found.")

print("=" * 60)
print("APEXTRACK AI — UPLOAD DATASET TO HUGGING FACE")
print("=" * 60)
print(f"Local dataset path: {dataset_folder}")
print(f"Target repository:  {repo_id}")

# Create dataset README / card
readme_content = """---
annotations_creators:
- expert-generated
language_creators:
- expert-generated
language:
- en
license:
- mit
multilinguality:
- monolingual
size_categories:
- n<1K
task_categories:
- image-classification
task_ids:
- multi-class-image-classification
tags:
- racing
- motorsport
- track-condition
- vision
- computer-vision
- vit
dataset_info:
  features:
  - name: image
    dtype: image
  - name: label
    dtype:
      class_label:
        names:
          '0': damp
          '1': dry
          '2': wet
  splits:
  - name: train
    num_bytes: 16000000
    num_examples: 300
  - name: validation
    num_bytes: 1500000
    num_examples: 27
  - name: test
    num_bytes: 1800000
    num_examples: 32
---

# ApexTrack Balanced Racing Track Condition Dataset

This dataset contains racing track condition images curated and balanced across three primary condition classes: **DRY**, **DAMP**, and **WET**.

It serves as the official training, validation, and evaluation benchmark for the **ApexTrack AI** Vision Transformer model ([`yuvrajengines/apextrack-track-condition-v2`](https://huggingface.co/yuvrajengines/apextrack-track-condition-v2)).

## Dataset Structure

```text
apextrack_balanced/
├── train/
│   ├── damp/ (100 images)
│   ├── dry/  (100 images)
│   └── wet/  (100 images)
├── validation/
│   ├── damp/ (5 images)
│   ├── dry/  (9 images)
│   └── wet/  (13 images)
└── test/
    ├── damp/ (7 images)
    ├── dry/  (11 images)
    └── wet/  (14 images)
```

## Classes

- `0: damp` - Track with noticeable moisture / drying racing lines.
- `1: dry` - Optimal dry asphalt surface.
- `2: wet` - Surface with visible standing water and spray.

## Usage with Hugging Face Datasets

```python
from datasets import load_dataset

dataset = load_dataset("yuvrajengines/apextrack-track-condition-dataset")
print(dataset)
```
"""

readme_path = dataset_folder / "README.md"
with open(readme_path, "w", encoding="utf-8") as f:
    f.write(readme_content)

print("\nUploading dataset folder to Hugging Face...")
api = HfApi(token=token)

api.upload_folder(
    folder_path=str(dataset_folder),
    repo_id=repo_id,
    repo_type="dataset",
    commit_message="Upload ApexTrack balanced track condition dataset (train, validation, test)",
)

print("\nDataset successfully uploaded to Hugging Face!")
print(f"URL: https://huggingface.co/datasets/{repo_id}")
