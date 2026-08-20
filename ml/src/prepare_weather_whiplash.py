from datasets import load_dataset
from pathlib import Path

DATASET_ID = "mrcreoid/weather-whiplash-surfaces"

OUTPUT_DIR = Path("data/processed/weather_whiplash")

dataset = load_dataset(DATASET_ID, split="train")

label_names = dataset.features["label"].names

print("Labels:", label_names)

for index, item in enumerate(dataset):
    label_id = item["label"]
    label = label_names[label_id]

    if label not in ["dry", "damp", "wet", "standing_water"]:
        continue

    output_folder = OUTPUT_DIR / label
    output_folder.mkdir(parents=True, exist_ok=True)

    image = item["image"].convert("RGB")

    image.save(output_folder / f"{label}_{index:04d}.jpg")

print("\nDone.")