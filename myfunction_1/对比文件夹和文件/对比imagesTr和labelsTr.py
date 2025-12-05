import os
from glob import glob

# 设置路径
images_dir = "DATASET/nnUNet_raw/Task007_example/imagesTr"
labels_dir = "DATASET/nnUNet_raw/Task007_example/labelsTr"

# 获取文件名（包含完整文件名）
images_files = sorted([os.path.basename(f) for f in glob(os.path.join(images_dir, "*.nii.gz"))])
labels_files = sorted([os.path.basename(f) for f in glob(os.path.join(labels_dir, "*.nii.gz"))])

print(f"imagesTr: {len(images_files)} 个文件")
print(f"labelsTr: {len(labels_files)} 个文件")

print("\n对比所有字符:")
if images_files == labels_files:
    print("✓ 文件名完全匹配")
else:
    print("✗ 文件名不完全匹配")
    
    # 找出不匹配的文件
    images_set = set(images_files)
    labels_set = set(labels_files)
    
    only_in_images = images_set - labels_set
    only_in_labels = labels_set - images_set
    
    if only_in_images:
        print(f"\n只在imagesTr中的文件 ({len(only_in_images)}个):")
        for file in sorted(only_in_images):
            print(f"  {file}")
    
    if only_in_labels:
        print(f"\n只在labelsTr中的文件 ({len(only_in_labels)}个):")
        for file in sorted(only_in_labels):
            print(f"  {file}")
    
    # 如果有共同文件，也显示出来
    common_files = images_set & labels_set
    if common_files:
        print(f"\n共同文件 ({len(common_files)}个):")
        for i, file in enumerate(sorted(common_files)[:10]):  # 只显示前10个
            print(f"  {file}")
        if len(common_files) > 10:
            print(f"  ... 等 {len(common_files) - 10} 个文件")

# 详细对比每个文件
print("\n" + "="*60)
print("详细对比报告:")
print("="*60)

# 确保两个列表长度相同以进行逐项对比
max_len = max(len(images_files), len(labels_files))
print(f"\n文件数量: imagesTr={len(images_files)}, labelsTr={len(labels_files)}")

# 逐项对比
mismatch_count = 0
for i in range(max_len):
    if i < len(images_files) and i < len(labels_files):
        img_file = images_files[i]
        label_file = labels_files[i]
        if img_file == label_file:
            print(f"  [{i+1:03d}] ✓ {img_file}")
        else:
            print(f"  [{i+1:03d}] ✗ imagesTr: {img_file}")
            print(f"         ✗ labelsTr: {label_file}")
            mismatch_count += 1
    elif i < len(images_files):
        print(f"  [{i+1:03d}] ✗ imagesTr: {images_files[i]}")
        print(f"         ✗ labelsTr: <缺失>")
        mismatch_count += 1
    else:
        print(f"  [{i+1:03d}] ✗ imagesTr: <缺失>")
        print(f"         ✗ labelsTr: {labels_files[i]}")
        mismatch_count += 1

print("\n" + "="*60)
print("总结:")
print(f"总文件数对比: imagesTr={len(images_files)} vs labelsTr={len(labels_files)}")
print(f"完全匹配: {images_files == labels_files}")
print(f"不匹配项数量: {mismatch_count}")