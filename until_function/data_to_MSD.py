import os
import re

def rename_to_msd_case_format(root_dir):
    """
    将数据集重命名为MSD格式（case_*****.nii.gz）
    
    参数:
        root_dir: 包含imagesTr和labelsTr文件夹的根目录
    """
    # 定义路径
    images_dir = os.path.join(root_dir, "imagesTr")
    labels_dir = os.path.join(root_dir, "labelsTr")
    # images_dir = 'DATASET/nnUNet_raw/Task004_example/imagesTr'
    # labels_dir = 'DATASET/nnUNet_raw/Task004_example/labelsTs'
    
    # 确保目录存在
    if not os.path.exists(images_dir) or not os.path.exists(labels_dir):
        print("错误: imagesTr或labelsTr文件夹不存在")
        return
    
    # 获取所有图像和标签文件（按名称排序）
    image_files = sorted([f for f in os.listdir(images_dir) if f.endswith(".nii.gz")])
    label_files = sorted([f for f in os.listdir(labels_dir) if f.endswith(".nii.gz")])
    
    # 检查文件数量是否匹配
    if len(image_files) != len(label_files):
        print("警告: 图像和标签文件数量不匹配")
    
    # 创建病例编号，从00001开始
    case_number = 1
    
    # 重命名图像文件
    for img_file in image_files:
        # 构建新文件名
        new_name = f"case_{str(case_number).zfill(5)}.nii.gz"
        
        # 重命名
        old_path = os.path.join(images_dir, img_file)
        new_path = os.path.join(images_dir, new_name)
        os.rename(old_path, new_path)
        print(f"重命名图像: {img_file} -> {new_name}")
        
        case_number += 1
    
    # 重置病例编号
    case_number = 1
    
    # 重命名标签文件
    for lbl_file in label_files:
        # 构建新文件名
        new_name = f"case_{str(case_number).zfill(5)}.nii.gz"
        
        # 重命名
        old_path = os.path.join(labels_dir, lbl_file)
        new_path = os.path.join(labels_dir, new_name)
        os.rename(old_path, new_path)
        print(f"重命名标签: {lbl_file} -> {new_name}")
        
        case_number += 1

if __name__ == "__main__":
    # 设置您的数据集根目录
    dataset_root = "DATASET/nnUNet_raw/Task006_example"
    
    # 调用函数进行重命名
    rename_to_msd_case_format(dataset_root)