from huggingface_hub import HfApi, hf_hub_download
from pathlib import Path
import random

REPO_ID = "rezzzq/RSCD-1million"
OUTPUT_DIR = Path("data/processed/rscd")

DRY_LIMIT = 500
WET_LIMIT = 500

api = HfApi()

files = api.list_repo_files(
    repo_id=REPO_ID,
    repo_type="dataset"
)

dry_files = [
    f for f in files
    if f.lower().endswith((".jpg", ".jpeg", ".png"))
    and "dry-asphalt" in f.lower()
]

wet_files = [
    f for f in files
    if f.lower().endswith((".jpg", ".jpeg", ".png"))
    and "wet-asphalt" in f.lower()
]

random.seed(42)

random.shuffle(dry_files)
random.shuffle(wet_files)

dry_files = dry_files[:DRY_LIMIT]
wet_files = wet_files[:WET_LIMIT]

print("Dry selected:", len(dry_files))
print("Wet selected:", len(wet_files))

dry_dir = OUTPUT_DIR / "dry"
wet_dir = OUTPUT_DIR / "wet"

dry_dir.mkdir(parents=True, exist_ok=True)
wet_dir.mkdir(parents=True, exist_ok=True)

for i, file in enumerate(dry_files, 1):
    print(f"Downloading DRY {i}/{len(dry_files)}")
    
    downloaded = hf_hub_download(
        repo_id=REPO_ID,
        filename=file,
        repo_type="dataset"
    )
    
    target = dry_dir / f"dry_{i:04d}.jpg"
    Path(downloaded).replace(target)

for i, file in enumerate(wet_files, 1):
    print(f"Downloading WET {i}/{len(wet_files)}")
    
    downloaded = hf_hub_download(
        repo_id=REPO_ID,
        filename=file,
        repo_type="dataset"
    )
    
    target = wet_dir / f"wet_{i:04d}.jpg"
    Path(downloaded).replace(target)

print("DONE")