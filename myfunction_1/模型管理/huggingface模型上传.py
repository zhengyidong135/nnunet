import os
from huggingface_hub import HfApi
from tqdm import tqdm

# -------------------------------
# 1) 使用网页申请的 Token（无需 login()）
# -------------------------------

api = HfApi(token=TOKEN)

# -------------------------------
# 2) 仓库信息
# -------------------------------
REPO_ID = "Xunqi/nnunet_segment_model"

# 可以写多个本地文件夹，自动循环上传
FOLDERS = [
    "DATASET/nnUNet_results/portal_vein_segment",
    "DATASET/nnUNet_results/hepatic_vein_segment",
    
]

# -------------------------------
# 3) 创建仓库（如果存在可忽略错误）
# -------------------------------
try:
    api.create_repo(repo_id=REPO_ID, repo_type="model")
except:
    print("仓库已存在，继续上传。")

# -------------------------------
# 4) 上传单个文件夹（带进度条）
# -------------------------------
def upload_with_progress(api, repo_id, folder_path):
    file_list = []

    # 遍历文件夹
    for root, _, files in os.walk(folder_path):
        for file in files:
            full = os.path.join(root, file)
            rel = os.path.relpath(full, folder_path)
            file_list.append((full, rel))

    print(f"\n开始上传文件夹: {folder_path}")
    print(f"总文件数: {len(file_list)}")

    # 上传文件，带进度条
    for full_path, rel_path in tqdm(file_list, desc="上传中", unit="file"):
        api.upload_file(
            path_or_fileobj=full_path,
            path_in_repo=rel_path,
            repo_id=repo_id,
            repo_type="model",
        )

# -------------------------------
# 5) 循环上传多个文件夹
# -------------------------------
for folder in FOLDERS:
    upload_with_progress(api, REPO_ID, folder)

print("\n全部文件夹上传完成！")
