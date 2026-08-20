from huggingface_hub import HfApi, hf_hub_download
from PIL import Image

def main():
    api = HfApi()
    repo_id = "yuvrajengines/apextrack-track-condition-dataset"

    print("=" * 60)
    print("APEXTRACK AI — REMOTE DATASET VERIFICATION")
    print("=" * 60)

    files = api.list_repo_files(repo_id=repo_id, repo_type="dataset")
    print(f"Total files in remote dataset: {len(files)}")

    train_files = [f for f in files if f.startswith("train/")]
    val_files = [f for f in files if f.startswith("validation/")]
    test_files = [f for f in files if f.startswith("test/")]

    damp_train = len([f for f in train_files if "/damp/" in f])
    dry_train = len([f for f in train_files if "/dry/" in f])
    wet_train = len([f for f in train_files if "/wet/" in f])

    damp_val = len([f for f in val_files if "/damp/" in f])
    dry_val = len([f for f in val_files if "/dry/" in f])
    wet_val = len([f for f in val_files if "/wet/" in f])

    damp_test = len([f for f in test_files if "/damp/" in f])
    dry_test = len([f for f in test_files if "/dry/" in f])
    wet_test = len([f for f in test_files if "/wet/" in f])

    print(f"Train files:      {len(train_files)} (damp: {damp_train}, dry: {dry_train}, wet: {wet_train})")
    print(f"Validation files: {len(val_files)} (damp: {damp_val}, dry: {dry_val}, wet: {wet_val})")
    print(f"Test files:       {len(test_files)} (damp: {damp_test}, dry: {dry_test}, wet: {wet_test})")

    assert len(train_files) == 300, f"Expected 300 train images, got {len(train_files)}"
    assert len(val_files) == 27, f"Expected 27 val images, got {len(val_files)}"
    assert len(test_files) == 32, f"Expected 32 test images, got {len(test_files)}"

    print("\nVerifying sample remote image access:")
    sample_file = test_files[0]
    print(f"Downloading sample: {sample_file}")
    local_sample = hf_hub_download(repo_id=repo_id, filename=sample_file, repo_type="dataset")
    img = Image.open(local_sample)
    print(f"Sample image successfully loaded: format={img.format}, size={img.size}, mode={img.mode}")

    print("\n" + "=" * 60)
    print("REMOTE HUGGING FACE DATASET VERIFICATION: 100% SUCCESS")
    print("=" * 60)

if __name__ == "__main__":
    main()
