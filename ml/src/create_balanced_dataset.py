from pathlib import Path
import shutil
import random
from PIL import Image
import torch
import torchvision.transforms.v2 as transforms

# --------------------------------------------------
# CONFIG & REPRODUCIBILITY
# --------------------------------------------------
SEED = 42
random.seed(SEED)
torch.manual_seed(SEED)

TARGET_TRAIN_COUNT = 100
CLASSES = ["dry", "damp", "wet"]
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

# Detect root or ml/ execution context
if Path("data/processed/apextrack").exists():
    SOURCE_DIR = Path("data/processed/apextrack")
    TARGET_DIR = Path("data/processed/apextrack_balanced")
    WW_SOURCE_DIR = Path("data/processed/weather_whiplash")
elif Path("ml/data/processed/apextrack").exists():
    SOURCE_DIR = Path("ml/data/processed/apextrack")
    TARGET_DIR = Path("ml/data/processed/apextrack_balanced")
    WW_SOURCE_DIR = Path("ml/data/processed/weather_whiplash")
else:
    raise FileNotFoundError("Could not locate data/processed/apextrack.")

# --------------------------------------------------
# CONSERVATIVE AUGMENTATION PIPELINE
# Preserves realistic track surface characteristics
# --------------------------------------------------
augmentation_transform = transforms.Compose([
    transforms.RandomHorizontalFlip(p=0.5),
    transforms.RandomRotation(degrees=(-8, 8), interpolation=transforms.InterpolationMode.BILINEAR),
    transforms.RandomResizedCrop(
        size=(224, 224),
        scale=(0.88, 1.0),
        ratio=(0.95, 1.05),
        interpolation=transforms.InterpolationMode.BILINEAR,
        antialias=True
    ),
    transforms.RandomAffine(
        degrees=0,
        translate=(0.04, 0.04),
        interpolation=transforms.InterpolationMode.BILINEAR
    ),
    transforms.ColorJitter(
        brightness=0.08,
        contrast=0.08,
        saturation=0.08
    ),
    transforms.RandomApply([
        transforms.GaussianBlur(kernel_size=(3, 3), sigma=(0.1, 0.5))
    ], p=0.2),
])


def get_image_files(directory: Path):
    """Return all valid image files in directory, ignoring .gitkeep and hidden files."""
    if not directory.exists():
        return []
    return sorted([
        p for p in directory.iterdir()
        if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS and not p.name.startswith(".")
    ])


def main():
    print("=" * 60)
    print("APEXTRACK BALANCED DATASET GENERATION")
    print("=" * 60)
    print(f"Source: {SOURCE_DIR}")
    print(f"Target: {TARGET_DIR}")
    print(f"Random Seed: {SEED}\n")

    # Record original file counts for immutability verification
    original_source_counts = {
        split: {
            cls: len(get_image_files(SOURCE_DIR / split / cls))
            for cls in CLASSES
        }
        for split in ["train", "validation", "test"]
    }

    # Clean/prepare target directory
    if TARGET_DIR.exists():
        for item in TARGET_DIR.iterdir():
            if item.is_dir():
                shutil.rmtree(item)
            else:
                item.unlink()
    TARGET_DIR.mkdir(parents=True, exist_ok=True)

    # Summary tracking
    stats = {"train": {}, "validation": {}, "test": {}}

    # --------------------------------------------------
    # 1. PROCESS TRAINING SET (COPY ORIGINALS + AUGMENT)
    # --------------------------------------------------
    print("Processing TRAINING split...")
    for cls in CLASSES:
        src_cls_dir = SOURCE_DIR / "train" / cls
        dst_cls_dir = TARGET_DIR / "train" / cls
        dst_cls_dir.mkdir(parents=True, exist_ok=True)

        orig_images = get_image_files(src_cls_dir)
        orig_count = len(orig_images)
        if orig_count == 0:
            raise ValueError(f"No original training images found in {src_cls_dir}")

        # Copy original training images unchanged
        for img_path in orig_images:
            shutil.copy2(img_path, dst_cls_dir / img_path.name)

        needed = TARGET_TRAIN_COUNT - orig_count
        if needed < 0:
            raise ValueError(f"Class {cls} already has {orig_count} images (exceeds target {TARGET_TRAIN_COUNT})")

        # Generate required augmentations distributed across source images
        augmented_count = 0
        if needed > 0:
            # Deterministic shuffled sampling pool
            source_pool = []
            while len(source_pool) < needed:
                shuffled_indices = list(range(orig_count))
                random.shuffle(shuffled_indices)
                source_pool.extend(shuffled_indices)
            source_pool = source_pool[:needed]

            for i, src_idx in enumerate(source_pool, start=1):
                src_path = orig_images[src_idx]
                with Image.open(src_path) as img:
                    img_rgb = img.convert("RGB")
                    # If image is smaller or non-standard, resize gently
                    orig_w, orig_h = img_rgb.size
                    # Apply transform
                    aug_tensor = augmentation_transform(img_rgb)
                    # Resize back to approximate original scale or standard 224x224
                    aug_img = transforms.ToPILImage()(aug_tensor) if isinstance(aug_tensor, torch.Tensor) else aug_tensor
                    if aug_img.size != (orig_w, orig_h):
                        aug_img = aug_img.resize((orig_w, orig_h), Image.Resampling.BICUBIC)

                    aug_filename = f"aug_{cls}_{i:04d}.jpg"
                    aug_path = dst_cls_dir / aug_filename
                    aug_img.save(aug_path, format="JPEG", quality=95)
                    augmented_count += 1

        final_count = len(get_image_files(dst_cls_dir))
        stats["train"][cls] = {
            "original": orig_count,
            "augmented": augmented_count,
            "final": final_count,
        }

    # --------------------------------------------------
    # 2. PROCESS VALIDATION SET (UNCHANGED COPY)
    # --------------------------------------------------
    print("Processing VALIDATION split (unchanged copy)...")
    for cls in CLASSES:
        src_cls_dir = SOURCE_DIR / "validation" / cls
        dst_cls_dir = TARGET_DIR / "validation" / cls
        dst_cls_dir.mkdir(parents=True, exist_ok=True)

        orig_images = get_image_files(src_cls_dir)
        for img_path in orig_images:
            shutil.copy2(img_path, dst_cls_dir / img_path.name)

        stats["validation"][cls] = len(get_image_files(dst_cls_dir))

    # --------------------------------------------------
    # 3. PROCESS TEST SET (UNCHANGED COPY)
    # --------------------------------------------------
    print("Processing TEST split (unchanged copy)...")
    for cls in CLASSES:
        src_cls_dir = SOURCE_DIR / "test" / cls
        dst_cls_dir = TARGET_DIR / "test" / cls
        dst_cls_dir.mkdir(parents=True, exist_ok=True)

        orig_images = get_image_files(src_cls_dir)
        for img_path in orig_images:
            shutil.copy2(img_path, dst_cls_dir / img_path.name)

        stats["test"][cls] = len(get_image_files(dst_cls_dir))

    # --------------------------------------------------
    # 4. COMPREHENSIVE DATA INTEGRITY CHECKS
    # --------------------------------------------------
    print("\nRunning comprehensive integrity checks...")

    # Check 1: Train counts == 100 per class
    for cls in CLASSES:
        count = len(get_image_files(TARGET_DIR / "train" / cls))
        if count != TARGET_TRAIN_COUNT:
            raise AssertionError(f"Integrity check failed: train/{cls} has {count} images, expected {TARGET_TRAIN_COUNT}")

    # Check 2: Validation counts match source
    for cls in CLASSES:
        count = len(get_image_files(TARGET_DIR / "validation" / cls))
        expected = original_source_counts["validation"][cls]
        if count != expected:
            raise AssertionError(f"Integrity check failed: validation/{cls} has {count}, expected {expected}")

    # Check 3: Test counts match source
    for cls in CLASSES:
        count = len(get_image_files(TARGET_DIR / "test" / cls))
        expected = original_source_counts["test"][cls]
        if count != expected:
            raise AssertionError(f"Integrity check failed: test/{cls} has {count}, expected {expected}")

    # Check 4: No standing_water
    for path in TARGET_DIR.rglob("*"):
        if "standing_water" in path.name.lower():
            raise AssertionError(f"Integrity check failed: Found standing_water at {path}")

    # Check 5: All images valid, RGB, not corrupted, no duplicate filenames
    seen_paths = set()
    for split in ["train", "validation", "test"]:
        for cls in CLASSES:
            cls_dir = TARGET_DIR / split / cls
            files = get_image_files(cls_dir)
            filenames = [f.name for f in files]
            if len(filenames) != len(set(filenames)):
                raise AssertionError(f"Integrity check failed: Duplicate filenames detected in {cls_dir}")

            for img_file in files:
                if str(img_file) in seen_paths:
                    raise AssertionError(f"Integrity check failed: Duplicate file path {img_file}")
                seen_paths.add(str(img_file))

                try:
                    with Image.open(img_file) as img:
                        img.verify()
                    # Reopen to test loading and mode
                    with Image.open(img_file) as img:
                        img.load()
                        if img.mode != "RGB":
                            raise AssertionError(f"Integrity check failed: {img_file} is not RGB (mode={img.mode})")
                except Exception as e:
                    raise AssertionError(f"Integrity check failed: Corrupted image at {img_file} - {e}")

    # Check 6: Source dataset untouched
    for split in ["train", "validation", "test"]:
        for cls in CLASSES:
            current_source_count = len(get_image_files(SOURCE_DIR / split / cls))
            if current_source_count != original_source_counts[split][cls]:
                raise AssertionError(f"Integrity check failed: Source {SOURCE_DIR}/{split}/{cls} was altered!")

    # --------------------------------------------------
    # 5. FINAL TERMINAL OUTPUT
    # --------------------------------------------------
    print("\n" + "=" * 50)
    print("APEXTRACK BALANCED DATASET")
    print("=" * 50)
    print(f"\nSource:\n{SOURCE_DIR}")
    print(f"\nTarget:\n{TARGET_DIR}\n")

    print("TRAINING:")
    for cls in CLASSES:
        print(f"\n{cls}:")
        print(f"  original:  {stats['train'][cls]['original']}")
        print(f"  augmented: {stats['train'][cls]['augmented']}")
        print(f"  final:     {stats['train'][cls]['final']}")

    print("\nVALIDATION:")
    for cls in CLASSES:
        print(f"{cls}: {stats['validation'][cls]}")

    print("\nTEST:")
    for cls in CLASSES:
        print(f"{cls}: {stats['test'][cls]}")

    print("\nIntegrity checks:")
    print("[OK] Training counts (100 per class, 300 total)")
    print("[OK] Validation unchanged")
    print("[OK] Test unchanged")
    print("[OK] No corrupted images")
    print("[OK] RGB format")
    print("[OK] No standing_water")
    print("[OK] Source dataset untouched")
    print("\nDATASET BALANCING COMPLETE\n" + "=" * 50)


if __name__ == "__main__":
    main()
