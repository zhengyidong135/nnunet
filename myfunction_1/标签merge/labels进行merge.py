import os
import numpy as np
import nibabel as nib
from pathlib import Path

def extract_single_label(source_dir, label_value, target_dir, suffix=""):
    """
    从多标签文件中提取单个标签值
    
    参数:
        source_dir: 源文件夹路径
        label_value: 要提取的标签值 (int)
        target_dir: 目标文件夹路径
        suffix: 文件名后缀 (可选)
    """
    # 确保目标文件夹存在
    target_dir = Path(target_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    
    # 获取所有nii.gz文件
    source_path = Path(source_dir)
    nii_files = list(source_path.glob("*.nii.gz"))
    
    print(f"提取标签值 {label_value}...")
    
    for file_path in nii_files:
        try:
            # 加载NIfTI文件
            img = nib.load(file_path)
            data = img.get_fdata()
            affine = img.affine
            header = img.header
            
            # 提取特定标签
            mask = (data == label_value).astype(np.uint8)
            
            # 创建新的NIfTI图像
            new_img = nib.Nifti1Image(mask, affine, header)
            
            # 构建目标文件名
            if suffix:
                target_filename = f"{file_path.stem.replace('.nii', '')}{suffix}.nii.gz"
            else:
                target_filename = f"{file_path.stem.replace('.nii', '')}_label{label_value}.nii.gz"
            
            target_path = target_dir / target_filename
            
            # 保存提取的标签
            nib.save(new_img, target_path)
            
            # 统计提取的体素数量
            voxel_count = np.sum(mask)
            print(f"  已处理: {file_path.name} -> {target_filename} (体素数: {voxel_count})")
            
        except Exception as e:
            print(f"  处理 {file_path.name} 时出错: {e}")

def extract_and_merge_labels(source_dir, label_values, target_dir, suffix=""):
    """
    从多标签文件中提取多个标签值并合并为一个标签
    
    参数:
        source_dir: 源文件夹路径
        label_values: 要提取的标签值列表 [int]
        target_dir: 目标文件夹路径
        suffix: 文件名后缀 (可选)
    """
    # 确保目标文件夹存在
    target_dir = Path(target_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    
    # 获取所有nii.gz文件
    source_path = Path(source_dir)
    nii_files = list(source_path.glob("*.nii.gz"))
    
    print(f"提取并合并标签值 {label_values}...")
    
    for file_path in nii_files:
        try:
            # 加载NIfTI文件
            img = nib.load(file_path)
            data = img.get_fdata()
            affine = img.affine
            header = img.header
            
            # 初始化合并掩码
            merged_mask = np.zeros_like(data, dtype=np.uint8)
            
            # 提取并合并所有指定标签
            for label_value in label_values:
                mask = (data == label_value).astype(np.uint8)
                merged_mask = np.maximum(merged_mask, mask)  # 合并掩码
            
            # 创建新的NIfTI图像 (值为1表示包含任何指定的标签)
            new_img = nib.Nifti1Image(merged_mask, affine, header)
            
            # 构建目标文件名
            if suffix:
                target_filename = f"{file_path.stem.replace('.nii', '')}{suffix}.nii.gz"
            else:
                label_str = "_".join([f"label{l}" for l in label_values])
                target_filename = f"{file_path.stem.replace('.nii', '')}_{label_str}.nii.gz"
            
            target_path = target_dir / target_filename
            
            # 保存合并的标签
            nib.save(new_img, target_path)
            
            # 统计提取的体素数量
            voxel_count = np.sum(merged_mask)
            individual_counts = {}
            for label_value in label_values:
                individual_counts[label_value] = np.sum(data == label_value)
            
            print(f"  已处理: {file_path.name} -> {target_filename}")
            print(f"    合并后体素数: {voxel_count}")
            print(f"    各标签体素数: {individual_counts}")
            
        except Exception as e:
            print(f"  处理 {file_path.name} 时出错: {e}")

# 主程序
if __name__ == "__main__":
    # 路径设置
    source_labels_dir = "DATASET/nnUNet_raw/Task005_example/PKU/labelsTr"
    target_portal_dir = "DATASET/nnUNet_raw/Task005_example/PKU/label_portal"
    target_liver_vein_dir = "DATASET/nnUNet_raw/Task005_example/PKU/label_liver_vein"
    
    print("=" * 60)
    print("开始分离多标签文件中的特定标签")
    print("=" * 60)
    
    # 1. 提取标签2到portal目录
    print("\n1. 提取标签2 (门静脉)")
    extract_single_label(source_labels_dir, 2, target_portal_dir, "_portal")
    
    print("\n" + "-" * 40)
    
    # 2. 提取标签7,8,9并合并到liver_vein目录
    print("\n2. 提取并合并标签7,8,9 (肝静脉)")
    liver_vein_labels = [7, 8, 9]  # 要提取的标签值
    extract_and_merge_labels(source_labels_dir, liver_vein_labels, target_liver_vein_dir, "_hepaticvein")
    
    print("\n" + "=" * 60)
    print("标签分离完成！")
    print(f"门静脉标签保存到: {target_portal_dir}")
    print(f"肝静脉标签保存到: {target_liver_vein_dir}")
    print("注: 肝静脉标签已合并label7,8,9为单一标签")