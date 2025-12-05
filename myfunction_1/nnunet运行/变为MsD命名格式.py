import os
import re

def rename_to_msd_case_format(root_dir):
    """
    将数据集重命名为MSD格式（case_*****.nii.gz）
    基于前7个字符进行匹配
    """
    # 定义路径
    images_dir = os.path.join(root_dir, "imagesTr")
    labels_dir = os.path.join(root_dir, "labelsTr")
    
    # 确保目录存在
    if not os.path.exists(images_dir) or not os.path.exists(labels_dir):
        print("错误: imagesTr或labelsTr文件夹不存在")
        return
    
    # 获取所有图像和标签文件
    image_files = sorted([f for f in os.listdir(images_dir) if f.endswith(".nii.gz")])
    label_files = sorted([f for f in os.listdir(labels_dir) if f.endswith(".nii.gz")])
    
    print(f"找到 {len(image_files)} 个图像文件")
    print(f"找到 {len(label_files)} 个标签文件")
    
    # 提取前7个字符并创建映射
    image_prefix_map = {}
    for img_file in image_files:
        prefix = img_file[:7]
        image_prefix_map[prefix] = img_file
    
    label_prefix_map = {}
    for lbl_file in label_files:
        prefix = lbl_file[:7]
        label_prefix_map[prefix] = lbl_file
    
    # 找到共同的前缀
    common_prefixes = sorted(set(image_prefix_map.keys()) & set(label_prefix_map.keys()))
    print(f"找到 {len(common_prefixes)} 个匹配的前缀")
    
    if not common_prefixes:
        print("错误: 没有找到匹配的前缀")
        return
    
    # 为每个匹配的前缀创建新的MSD格式文件名
    case_number = 1
    
    for prefix in common_prefixes:
        # 构建新文件名
        new_name = f"case_{str(case_number).zfill(5)}.nii.gz"
        
        # 重命名图像文件
        old_img_path = os.path.join(images_dir, image_prefix_map[prefix])
        new_img_path = os.path.join(images_dir, new_name)
        os.rename(old_img_path, new_img_path)
        print(f"重命名图像: {image_prefix_map[prefix]} -> {new_name}")
        
        # 重命名标签文件
        old_lbl_path = os.path.join(labels_dir, label_prefix_map[prefix])
        new_lbl_path = os.path.join(labels_dir, new_name)
        os.rename(old_lbl_path, new_lbl_path)
        print(f"重命名标签: {label_prefix_map[prefix]} -> {new_name}")
        
        case_number += 1
    
    # 处理不匹配的文件
    only_in_images = set(image_prefix_map.keys()) - set(common_prefixes)
    only_in_labels = set(label_prefix_map.keys()) - set(common_prefixes)
    
    if only_in_images:
        print(f"\n警告: {len(only_in_images)} 个图像文件没有匹配的标签:")
        for prefix in only_in_images:
            print(f"  {image_prefix_map[prefix]}")
    
    if only_in_labels:
        print(f"\n警告: {len(only_in_labels)} 个标签文件没有匹配的图像:")
        for prefix in only_in_labels:
            print(f"  {label_prefix_map[prefix]}")

if __name__ == "__main__":
    # 设置您的数据集根目录
    dataset_root = "DATASET/nnUNet_raw/Task007_example"
    
    # 调用函数进行重命名
    rename_to_msd_case_format(dataset_root)