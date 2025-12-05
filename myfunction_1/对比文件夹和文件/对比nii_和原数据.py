import os
import glob
def simple_name_comparison():
    # 定义两个路径
    nii_dir = "/media/dell/T7 Shield/nnunet/AllData/GXYF/Finished/1-8_precontrast/mask/Group1/GT_couinaud"
    subfolder_dir = "/media/dell/T7 Shield/nnunet/AllData/GXYF/Finished/1-8dicom规范化/1_组1_规范化"
    
    print("简单命名对比")
    print(f"nii.gz目录: {nii_dir}")
    print(f"子文件夹目录: {subfolder_dir}")
    print("-" * 50)
    
    # 检查目录是否存在
    if not os.path.exists(nii_dir):
        print(f"错误：nii.gz目录不存在")
        return
    
    if not os.path.exists(subfolder_dir):
        print(f"错误：子文件夹目录不存在")
        return
    
    # 获取nii.gz文件的命名（不含扩展名）
    nii_files = glob.glob(os.path.join(nii_dir, "*.nii.gz"))
    nii_names = set(os.path.basename(f).replace('.nii.gz', '') for f in nii_files)
    
    # 获取子文件夹的命名
    subfolders = set()
    for item in os.listdir(subfolder_dir):
        item_path = os.path.join(subfolder_dir, item)
        if os.path.isdir(item_path):
            subfolders.add(item)
    
    print(f"nii.gz文件数: {len(nii_names)}")
    print(f"子文件夹数: {len(subfolders)}")
    print()
    
    # 找出不同命名的项目
    only_in_nii = nii_names - subfolders
    only_in_subfolders = subfolders - nii_names
    
    # 输出只在nii.gz目录中存在的项目
    if only_in_nii:
        print("只在nii.gz目录中存在的命名:")
        for name in sorted(only_in_nii):
            print(f"  - {name}")
        print()
    
    # 输出只在子文件夹目录中存在的项目
    if only_in_subfolders:
        print("只在子文件夹目录中存在的命名:")
        for name in sorted(only_in_subfolders):
            print(f"  - {name}")
        print()
    
    # 输出匹配信息
    matched = nii_names & subfolders
    print(f"匹配的命名数量: {len(matched)}")
    
    if not only_in_nii and not only_in_subfolders:
        print("所有命名完全匹配！")

if __name__ == "__main__":
    simple_name_comparison()