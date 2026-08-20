import json
from pathlib import Path
import numpy as np
import torch
import matplotlib.pyplot as plt
from datasets import load_dataset
from transformers import (
    AutoImageProcessor,
    AutoModelForImageClassification,
    TrainingArguments,
    Trainer,
    set_seed,
)
from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    classification_report,
    confusion_matrix,
    ConfusionMatrixDisplay,
)

# --------------------------------------------------
# CONFIG & SEED
# --------------------------------------------------
import os
cpu_cores = os.cpu_count() or 4
torch.set_num_threads(cpu_cores)

SEED = 42
set_seed(SEED)

# Detect runtime path context
if Path("data/processed/apextrack_balanced").exists():
    DATASET_PATH = "data/processed/apextrack_balanced"
    OUTPUT_DIR = "models/apextrack-vit-v2"
elif Path("ml/data/processed/apextrack_balanced").exists():
    DATASET_PATH = "ml/data/processed/apextrack_balanced"
    OUTPUT_DIR = "ml/models/apextrack-vit-v2"
else:
    raise FileNotFoundError("Could not find apextrack_balanced dataset directory.")

MODEL_NAME = "google/vit-base-patch16-224-in21k"
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

# --------------------------------------------------
# LOAD BALANCED DATASET
# --------------------------------------------------
print("=" * 60)
print("APEXTRACK AI — V2 MODEL TRAINING (BALANCED DATASET)")
print("=" * 60)
print(f"Dataset path: {DATASET_PATH}")
print(f"Base model:   {MODEL_NAME}")
print(f"Output dir:   {OUTPUT_DIR}\n")

print("Loading dataset...")
dataset = load_dataset("imagefolder", data_dir=DATASET_PATH)
print(dataset)

# --------------------------------------------------
# LABELS & MAPPINGS
# --------------------------------------------------
labels = dataset["train"].features["label"].names
label2id = {label: i for i, label in enumerate(labels)}
id2label = {i: label for i, label in enumerate(labels)}

print("\nLabels mapped:")
for label, idx in label2id.items():
    print(f"  {idx} -> {label}")

# --------------------------------------------------
# IMAGE PROCESSOR & PREPROCESSING
# --------------------------------------------------
print("\nLoading image processor...")
processor = AutoImageProcessor.from_pretrained(MODEL_NAME)


def preprocess(example):
    image = example["image"].convert("RGB")
    processed = processor(image, return_tensors="pt")
    example["pixel_values"] = processed["pixel_values"][0]
    return example


print("Preprocessing dataset images...")
dataset = dataset.map(preprocess, remove_columns=["image"])
dataset.set_format("torch")

# --------------------------------------------------
# METRICS FUNCTION
# --------------------------------------------------
def compute_metrics(eval_pred):
    logits, ground_truth = eval_pred
    preds = np.argmax(logits, axis=1)

    acc = accuracy_score(ground_truth, preds)
    precision_macro, recall_macro, f1_macro, _ = precision_recall_fscore_support(
        ground_truth, preds, average="macro", zero_division=0
    )
    _, _, f1_weighted, _ = precision_recall_fscore_support(
        ground_truth, preds, average="weighted", zero_division=0
    )

    return {
        "accuracy": float(acc),
        "macro_precision": float(precision_macro),
        "macro_recall": float(recall_macro),
        "macro_f1": float(f1_macro),
        "weighted_f1": float(f1_weighted),
    }


# --------------------------------------------------
# MODEL INITIALIZATION
# --------------------------------------------------
print("\nLoading pretrained ViT model...")
model = AutoModelForImageClassification.from_pretrained(
    MODEL_NAME,
    num_labels=len(labels),
    id2label=id2label,
    label2id=label2id,
    ignore_mismatched_sizes=True,
)

# --------------------------------------------------
# TRAINING CONFIGURATION
# --------------------------------------------------
training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,
    num_train_epochs=5,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    learning_rate=2.5e-5,
    eval_strategy="epoch",
    save_strategy="epoch",
    load_best_model_at_end=True,
    metric_for_best_model="macro_f1",
    greater_is_better=True,
    logging_steps=10,
    report_to="none",
    fp16=False,
    seed=SEED,
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset["train"],
    eval_dataset=dataset["validation"],
    compute_metrics=compute_metrics,
)

# --------------------------------------------------
# TRAIN MODEL
# --------------------------------------------------
print("\nStarting V2 model training on balanced dataset...\n")
trainer.train()

# --------------------------------------------------
# EVALUATION ON UNTOUCHED TEST SET
# --------------------------------------------------
print("\n" + "=" * 60)
print("EVALUATING V2 ON UNTOUCHED TEST DATASET")
print("=" * 60)

test_predictions_output = trainer.predict(dataset["test"])
test_preds = np.argmax(test_predictions_output.predictions, axis=1)
test_labels = test_predictions_output.label_ids

# Overall Metrics
test_acc = accuracy_score(test_labels, test_preds)
macro_prec, macro_rec, macro_f1, _ = precision_recall_fscore_support(
    test_labels, test_preds, average="macro", zero_division=0
)
_, _, weighted_f1, _ = precision_recall_fscore_support(
    test_labels, test_preds, average="weighted", zero_division=0
)

# Per-class metrics
precisions, recalls, f1s, supports = precision_recall_fscore_support(
    test_labels, test_preds, average=None, labels=list(range(len(labels))), zero_division=0
)

per_class_results = {}
for i, label_name in enumerate(labels):
    per_class_results[label_name] = {
        "precision": float(precisions[i]),
        "recall": float(recalls[i]),
        "f1": float(f1s[i]),
        "support": int(supports[i]),
    }

# --------------------------------------------------
# CLASSIFICATION REPORT
# --------------------------------------------------
print("\nCLASSIFICATION REPORT (V2 TEST SET):")
print("-" * 60)
report_str = classification_report(
    test_labels,
    test_preds,
    target_names=labels,
    digits=4,
    zero_division=0,
)
print(report_str)

# --------------------------------------------------
# CONFUSION MATRIX
# --------------------------------------------------
cm = confusion_matrix(test_labels, test_preds)
print("CONFUSION MATRIX (V2):")
print("-" * 60)
print(cm)

cm_display = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=labels)
fig, ax = plt.subplots(figsize=(6, 5))
cm_display.plot(ax=ax, cmap="Blues", colorbar=False)
plt.title("ApexTrack AI - V2 Test Confusion Matrix")
plt.tight_layout()

cm_path = Path(OUTPUT_DIR) / "confusion_matrix.png"
plt.savefig(cm_path, dpi=200)
plt.close()
print(f"\nConfusion matrix plot saved to: {cm_path}")

# --------------------------------------------------
# SAVE RESULTS JSON
# --------------------------------------------------
results_payload = {
    "model": MODEL_NAME,
    "dataset": "apextrack_balanced",
    "accuracy": float(test_acc),
    "macro_precision": float(macro_prec),
    "macro_recall": float(macro_rec),
    "macro_f1": float(macro_f1),
    "weighted_f1": float(weighted_f1),
    "per_class": {
        cls: {
            "precision": float(per_class_results[cls]["precision"]),
            "recall": float(per_class_results[cls]["recall"]),
            "f1": float(per_class_results[cls]["f1"]),
        }
        for cls in ["damp", "dry", "wet"]
    },
}

results_json_path = Path(OUTPUT_DIR) / "results.json"
with open(results_json_path, "w") as f:
    json.dump(results_payload, f, indent=4)
print(f"Results JSON saved to: {results_json_path}")

# --------------------------------------------------
# SAVE FINAL BEST MODEL & PROCESSOR
# --------------------------------------------------
print("\nSaving final V2 model and processor...")
trainer.save_model(OUTPUT_DIR)
processor.save_pretrained(OUTPUT_DIR)
print(f"Model saved to: {OUTPUT_DIR}")

# --------------------------------------------------
# V1 vs V2 COMPARISON TABLE
# --------------------------------------------------
v1_acc = 53.13
v1_weighted_f1 = 46.57
v1_macro_f1 = 39.65
v1_damp_f1 = 0.00
v1_dry_f1 = 58.33
v1_wet_f1 = 60.61

v2_acc_pct = test_acc * 100
v2_weighted_f1_pct = weighted_f1 * 100
v2_macro_f1_pct = macro_f1 * 100
v2_damp_f1_pct = per_class_results.get("damp", {}).get("f1", 0.0) * 100
v2_dry_f1_pct = per_class_results.get("dry", {}).get("f1", 0.0) * 100
v2_wet_f1_pct = per_class_results.get("wet", {}).get("f1", 0.0) * 100

print("\n" + "=" * 50)
print("APEXTRACK MODEL COMPARISON")
print("=" * 50)
print(f"{'':<20} {'V1':<12} {'V2':<12}")
print(f"{'Accuracy':<20} {v1_acc:>6.2f}%     {v2_acc_pct:>6.2f}%")
print(f"{'Weighted F1':<20} {v1_weighted_f1:>6.2f}%     {v2_weighted_f1_pct:>6.2f}%")
print(f"{'Macro F1':<20} {v1_macro_f1:>6.2f}%     {v2_macro_f1_pct:>6.2f}%")
print(f"{'Damp F1':<20} {v1_damp_f1:>6.2f}%     {v2_damp_f1_pct:>6.2f}%")
print(f"{'Dry F1':<20} {v1_dry_f1:>6.2f}%     {v2_dry_f1_pct:>6.2f}%")
print(f"{'Wet F1':<20} {v1_wet_f1:>6.2f}%     {v2_wet_f1_pct:>6.2f}%")
print("=" * 50 + "\n")
