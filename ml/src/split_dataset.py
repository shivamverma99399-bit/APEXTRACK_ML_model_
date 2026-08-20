from pathlib import Path
import random
import shutil

SOURCE = Path("data/processed/weather_whiplash")
DEST = Path("data/processed/apextrack")

CLASSES = ["dry", "damp", "wet"]

TRAIN_RATIO = 0.70
VAL_RATIO = 0.15
TEST_RATIO = 0.15

random.seed(42)

for class_name in CLASSES:
    source_dir = SOURCE / class_name

    images = [
        p for p in source_dir.iterdir()
        if p.is_file() and p.suffix.lower() in [".jpg", ".jpeg", ".png", ".webp"]
    ]

    random.shuffle(images)

    total = len(images)

    train_end = int(total * TRAIN_RATIO)
    val_end = train_end + int(total * VAL_RATIO)

    train_images = images[:train_end]
    val_images = images[train_end:val_end]
    test_images = images[val_end:]

    print(f"\n{class_name}:")
    print(f"  Total:      {total}")
    print(f"  Train:      {len(train_images)}")
    print(f"  Validation: {len(val_images)}")
    print(f"  Test:       {len(test_images)}")

    for split, split_images in [
        ("train", train_images),
        ("validation", val_images),
        ("test", test_images),
    ]:
        output_dir = DEST / split / class_name
        output_dir.mkdir(parents=True, exist_ok=True)

        # Remove old files except .gitkeep
        for old_file in output_dir.iterdir():
            if old_file.is_file() and old_file.name != ".gitkeep":
                old_file.unlink()

        for image in split_images:
            shutil.copy2(image, output_dir / image.name)

print("\nDataset split completed.")
