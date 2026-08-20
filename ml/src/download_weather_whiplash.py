from datasets import load_dataset

DATASET_ID = "mrcreoid/weather-whiplash-surfaces"

print("Loading dataset...")

dataset = load_dataset(DATASET_ID, split="train")

print(dataset)
print(dataset.features)

print("\nLabels:")

label_feature = dataset.features["label"]

for i, name in enumerate(label_feature.names):
    print(i, "->", name)