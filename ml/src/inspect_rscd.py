from huggingface_hub import HfApi

api = HfApi()

info = api.dataset_info(
    repo_id="rezzzq/RSCD-1million"
)

print("Dataset:", info.id)
print("Files:", len(info.siblings))

for file in info.siblings[:100]:
    print(file.rfilename)