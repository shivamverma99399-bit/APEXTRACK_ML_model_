from datasets import load_dataset
from transformers import (
    AutoImageProcessor,
    AutoModelForImageClassification,
    TrainingArguments,
    Trainer,
)
import numpy as np
import evaluate

# --------------------------------------------------
# CONFIG
# --------------------------------------------------

DATASET_PATH = "data/processed/apextrack"
MODEL_NAME = "google/vit-base-patch16-224-in21k"
OUTPUT_DIR = "models/apextrack-vit"

# --------------------------------------------------
# LOAD DATASET
# --------------------------------------------------

print("Loading dataset...")

dataset = load_dataset(
    "imagefolder",
    data_dir=DATASET_PATH
)

print(dataset)

# --------------------------------------------------
# LABELS
# --------------------------------------------------

labels = dataset["train"].features["label"].names

label2id = {
    label: i
    for i, label in enumerate(labels)
}

id2label = {
    i: label
    for i, label in enumerate(labels)
}

print("\nLabels:")
print(label2id)

# --------------------------------------------------
# IMAGE PROCESSOR
# --------------------------------------------------

print("\nLoading image processor...")

processor = AutoImageProcessor.from_pretrained(
    MODEL_NAME
)

# --------------------------------------------------
# PREPROCESSING
# --------------------------------------------------

def preprocess(example):
    image = example["image"].convert("RGB")

    processed = processor(
        image,
        return_tensors="pt"
    )

    example["pixel_values"] = processed["pixel_values"][0]

    return example


print("\nPreprocessing images...")

dataset = dataset.map(
    preprocess,
    remove_columns=["image"]
)

dataset.set_format("torch")

# --------------------------------------------------
# METRICS
# --------------------------------------------------

accuracy_metric = evaluate.load("accuracy")
f1_metric = evaluate.load("f1")


def compute_metrics(eval_pred):

    predictions, labels = eval_pred

    predictions = np.argmax(
        predictions,
        axis=1
    )

    accuracy = accuracy_metric.compute(
        predictions=predictions,
        references=labels
    )

    f1 = f1_metric.compute(
        predictions=predictions,
        references=labels,
        average="weighted"
    )

    return {
        "accuracy": accuracy["accuracy"],
        "f1": f1["f1"],
    }


# --------------------------------------------------
# MODEL
# --------------------------------------------------

print("\nLoading pretrained ViT...")

model = AutoModelForImageClassification.from_pretrained(
    MODEL_NAME,
    num_labels=len(labels),
    id2label=id2label,
    label2id=label2id,
    ignore_mismatched_sizes=True,
)

# --------------------------------------------------
# TRAINING
# --------------------------------------------------

training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,

    num_train_epochs=5,

    per_device_train_batch_size=4,
    per_device_eval_batch_size=4,

    learning_rate=2e-5,

    eval_strategy="epoch",
    save_strategy="epoch",

    load_best_model_at_end=True,

    metric_for_best_model="f1",
    greater_is_better=True,

    logging_steps=5,

    report_to="none",

    fp16=False,
)

# --------------------------------------------------
# TRAINER
# --------------------------------------------------

trainer = Trainer(
    model=model,
    args=training_args,

    train_dataset=dataset["train"],
    eval_dataset=dataset["validation"],

    compute_metrics=compute_metrics,
)

# --------------------------------------------------
# TRAIN
# --------------------------------------------------

print("\nStarting training...\n")

trainer.train()

# --------------------------------------------------
# TEST
# --------------------------------------------------

print("\nEvaluating on TEST dataset...\n")

results = trainer.evaluate(
    dataset["test"]
)

print("\nTEST RESULTS")
print("=" * 50)

for key, value in results.items():
    print(f"{key}: {value}")

# --------------------------------------------------
# SAVE
# --------------------------------------------------

print("\nSaving model...")

trainer.save_model(OUTPUT_DIR)
processor.save_pretrained(OUTPUT_DIR)

print("\nModel saved to:")
print(OUTPUT_DIR)