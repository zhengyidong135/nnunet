import os
import nibabel as nib
import numpy as np

# 设置路径
dataset_path = "DATASET/nnUNet_raw/Dataset005_example"
images_dir = os.path.join(dataset_path, "imagesTr")
labels_dir = os.path.join(dataset_path, "labelsTr")

# 获取所有文件
image_files = sorted([f for f in os.listdir(images_dir) if f.endswith(".nii.gz")])
label_files = sorted([f for f in os.listdir(labels_dir) if f.endswith(".nii.gz")])

print(f"imagesTr 文件数: {len(image_files)}")
print(f"labelsTr 文件数: {len(label_files)}")

# 提取基础名称（移除模态后缀）
def get_base_name(filename):
    # nnUNet 命名格式: case_XXXXX_YYYY.nii.gz (YYYY 是模态编号)
    # 移除 _XXXXX 模态后缀
    if "_0000.nii.gz" in filename:
        return filename.replace("_0000.nii.gz", ".nii.gz")
    elif "_0001.nii.gz" in filename:
        return filename.replace("_0001.nii.gz", ".nii.gz")
    elif "_0002.nii.gz" in filename:
        return filename.replace("_0002.nii.gz", ".nii.gz")
    elif "_0003.nii.gz" in filename:
        return filename.replace("_0003.nii.gz", ".nii.gz")
    else:
        return filename

# 创建映射字典
image_base_to_full = {}
for img_file in image_files:
    base_name = get_base_name(img_file)
    image_base_to_full[base_name] = img_file

# 检查匹配情况
mismatched_shape = []
missing_labels = []
missing_images = []

for lbl_file in label_files:
    if lbl_file in image_base_to_full:
        img_file = image_base_to_full[lbl_file]
        
        # 加载图像和标签
        img_path = os.path.join(images_dir, img_file)
        lbl_path = os.path.join(labels_dir, lbl_file)
        
        try:
            img = nib.load(img_path)
            lbl = nib.load(lbl_path)
            
            # 检查维度（考虑多模态情况）
            img_shape = img.shape
            lbl_shape = lbl.shape
            
            # 对于 nnUNet，通常比较空间维度（前3维）
            if len(img_shape) >= 3 and len(lbl_shape) == 3:
                if img_shape[:3] != lbl_shape:
                    mismatched_shape.append((lbl_file, img_shape[:3], lbl_shape))
            elif img_shape != lbl_shape:
                mismatched_shape.append((lbl_file, img_shape, lbl_shape))
                
        except Exception as e:
            print(f"加载文件时出错 {lbl_file}: {e}")
    else:
        missing_images.append(lbl_file)

# 检查是否有 image 没有对应的 label
for img_base in image_base_to_full.keys():
    if img_base not in label_files:
        missing_labels.append(image_base_to_full[img_base])

# 输出结果
print("\n" + "="*60)
print("检查结果：")
print("="*60)

if mismatched_shape:
    print("\n❌ Shape 不匹配的文件：")
    for fname, img_shape, lbl_shape in mismatched_shape:
        print(f"  {fname}:")
        print(f"    图像 shape: {img_shape}")
        print(f"    标签 shape: {lbl_shape}")
else:
    print("\n✅ 所有匹配文件的 shape 均一致！")

if missing_images:
    print(f"\n⚠️  有标签但缺少图像的文件 ({len(missing_images)} 个):")
    for f in missing_images[:10]:  # 只显示前10个
        print(f"  {f}")
    if len(missing_images) > 10:
        print(f"  ... 还有 {len(missing_images)-10} 个文件")

if missing_labels:
    print(f"\n⚠️  有图像但缺少标签的文件 ({len(missing_labels)} 个):")
    for f in missing_labels[:10]:  # 只显示前10个
        print(f"  {f}")
    if len(missing_labels) > 10:
        print(f"  ... 还有 {len(missing_labels)-10} 个文件")

# 统计信息
print("\n" + "="*60)
print("统计信息：")
print(f"总图像文件数: {len(image_files)}")
print(f"总标签文件数: {len(label_files)}")
print(f"成功匹配的文件对: {len(label_files) - len(missing_images)}")
print(f"Shape 不匹配的文件对: {len(mismatched_shape)}")
print(f"缺少图像的文件: {len(missing_images)}")
print(f"缺少标签的文件: {len(missing_labels)}")