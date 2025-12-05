import os
import pandas as pd
import re

# 配置路径
source_dir = "/media/dell/T7 Shield1/nnunet/AllData/GXZL/finished/HBP/nii/Group5"
output_mapping_file = "/media/dell/T7 Shield1/nnunet/AllData/GXZL/finished/HBP/nii/name5.txt"

def natural_sort_key(s):
    """
    自然排序键函数，处理字母数字混合文件名
    """
    return [int(text) if text.isdigit() else text.lower() 
            for text in re.split('([0-9]+)', s)]

# 获取原始文件列表（按自然顺序排序）
original_files = sorted(
    [f for f in os.listdir(source_dir) if f.endswith('.nii.gz')],
    key=natural_sort_key
)

# 创建映射关系
mapping = []
for idx, orig_name in enumerate(original_files, start=1):
    # 生成标准化名称 (case_0001_0000.nii.gz 格式)
    new_name = f"case_{idx:04d}_0000.nii.gz"
    mapping.append({"original_name": orig_name, "standardized_name": new_name})

    # 重命名文件
    orig_path = os.path.join(source_dir, orig_name)
    new_path = os.path.join(source_dir, new_name)
    os.rename(orig_path, new_path)
    print(f"Renamed: {orig_name} -> {new_name}")

# 将映射关系保存为TSV文件
df = pd.DataFrame(mapping)
df.to_csv(output_mapping_file, sep="\t", index=False)
print(f"\nMapping saved to: {output_mapping_file}")

# 显示前几行示例
print("\nSample mapping:")
print(df.head())