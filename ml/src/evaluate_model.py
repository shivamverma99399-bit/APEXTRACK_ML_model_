from datasets import load_dataset
from transformers import AutoImageProcessor, AutoModelForImageClassification
from torch.utils.data import DataLoader
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    ConfusionMatrixDisplay,
)
import torch
import numpy as np
import matplotlib.pyplot as plt


DATASET_PATH = "data/processed/apextrack"
MODEL_PATH = "models/apextrack-vit"

print("Loading test dataset...")

dataset = load_dataset(
    "imagefolder",
    data_dir=DATASET_PATH
)

test_dataset = dataset["test"]

print(f"Test images: {len(test_dataset)}")

print("\nLoading model...")

processor = AutoImageProcessor.from_pretrained(MODEL_PATH)

model = AutoModelForImageClassification.from_pretrained(
    MODEL_PATH
)

model.eval()

device = torch.device("cpu")
model.to(device)

print("Model loaded.")
print("Device:", device)

# --------------------------------------------------
# PREDICTION
# --------------------------------------------------

predictions = []
true_labels = []

print("\nRunning predictions...")

for example in test_dataset:

    image = example["image"].convert("RGB")

    inputs = processor(
        image,
        return_tensors="pt"
    )

    inputs = {
        key: value.to(device)
        for key, value in inputs.items()
    }

    with torch.no_grad():
        outputs = model(**inputs)

    predicted_class = torch.argmax(
        outputs.logits,
        dim=-1
    ).item()

    predictions.append(predicted_class)
    true_labels.append(example["label"])


# --------------------------------------------------
# LABELS
# --------------------------------------------------

labels = test_dataset.features["label"].names

print("\nLabels:")
for i, label in enumerate(labels):
    print(f"{i} -> {label}")


# --------------------------------------------------
# CLASSIFICATION REPORT
# --------------------------------------------------

print("\n")
print("=" * 60)
print("CLASSIFICATION REPORT")
print("=" * 60)

print(
    classification_report(
        true_labels,
        predictions,
        target_names=labels,
        digits=4,
        zero_division=0
    )
)


# --------------------------------------------------
# CONFUSION MATRIX
# --------------------------------------------------

cm = confusion_matrix(
    true_labels,
    predictions
)

print("=" * 60)
print("CONFUSION MATRIX")
print("=" * 60)

print(cm)

# --------------------------------------------------
# SAVE CONFUSION MATRIX
# --------------------------------------------------

display = ConfusionMatrixDisplay(
    confusion_matrix=cm,
    display_labels=labels
)

display.plot(
    xticks_rotation="horizontal"
)

plt.title("ApexTrack AI - Test Confusion Matrix")

plt.tight_layout()

plt.savefig(
    "models/apextrack-vit/confusion_matrix.png",
    dpi=200
)

plt.show()

print("\nConfusion matrix saved to:")
print("models/apextrack-vit/confusion_matrix.png")