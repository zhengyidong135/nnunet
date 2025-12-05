import os
import shutil

# 目标文件夹路径
target_dir = "/media/dell/T7 Shield1/nnunet/AllData/GXZL/finished/HBP/dicom/Group5"

# 要删除的子文件夹列表
folders_to_delete = [
    "MR250494",
    "MR251060",
    "MR252312",
    "MR252473", 
    "MR252678",
    "MR252796",
    "MR253538",
    "MR254804",
    "MR255167"
]
print("将要删除的文件夹:")
for i, folder in enumerate(folders_to_delete, 1):
    print(f"{i}. {folder}")

print(f"\n总计: {len(folders_to_delete)} 个文件夹")
print("\n目标目录内容:")
for item in os.listdir(target_dir):
    if os.path.isdir(os.path.join(target_dir, item)):
        print(f"  文件夹: {item}")
    else:
        print(f"  文件: {item}")

# 确认操作
confirm = input(f"\n确认要删除以上 {len(folders_to_delete)} 个文件夹吗？(y/N): ")

if confirm.lower() == 'y':
    deleted_count = 0
    error_folders = []
    
    for folder in folders_to_delete:
        folder_path = os.path.join(target_dir, folder)
        
        if os.path.exists(folder_path) and os.path.isdir(folder_path):
            try:
                shutil.rmtree(folder_path)  # 递归删除文件夹及其内容
                print(f"✓ 已删除: {folder}")
                deleted_count += 1
            except Exception as e:
                print(f"✗ 删除 {folder} 时出错: {e}")
                error_folders.append(folder)
        else:
            print(f"⚠ {folder} 不存在或不是文件夹")
    
    # 显示删除结果
    print(f"\n删除完成:")
    print(f"  成功删除: {deleted_count} 个文件夹")
    print(f"  失败: {len(error_folders)} 个文件夹")
    
    if error_folders:
        print("删除失败的文件夹:")
        for folder in error_folders:
            print(f"  - {folder}")
else:
    print("操作已取消")

# 验证当前目录内容
print(f"\n当前目录内容:")
for item in os.listdir(target_dir):
    item_path = os.path.join(target_dir, item)
    if os.path.isdir(item_path):
        print(f"  文件夹: {item}")
    else:
        print(f"  文件: {item}")