import os

def rename_files_using_mapping_partial(directory_path, mapping_file_path):
    """
    根据映射文件重命名目录中的文件（匹配前9个字符）
    """
    # 检查目录是否存在
    if not os.path.exists(directory_path):
        print(f"错误: 目录不存在 - {directory_path}")
        return
    
    # 检查映射文件是否存在
    if not os.path.exists(mapping_file_path):
        print(f"错误: 映射文件不存在 - {mapping_file_path}")
        return
    
    # 读取映射文件
    mapping_dict = {}
    try:
        with open(mapping_file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # 跳过标题行
        for line in lines[1:]:
            line = line.strip()
            if line and '\t' in line:
                parts = line.split('\t')
                if len(parts) >= 2:
                    original_name = parts[0].strip()
                    standardized_name = parts[1].strip()
                    # 只取前9个字符作为键
                    standardized_prefix = standardized_name[:9]
                    mapping_dict[standardized_prefix] = original_name
        
        print(f"成功读取映射文件，共 {len(mapping_dict)} 条映射记录")
        print("映射关系示例:")
        for i, (prefix, original) in enumerate(list(mapping_dict.items())[:5]):
            print(f"  {prefix} -> {original}")
    except Exception as e:
        print(f"读取映射文件时出错: {e}")
        return
    
    # 获取目录中的所有nii.gz文件
    nii_files = [f for f in os.listdir(directory_path) if f.endswith('.nii.gz')]
    print(f"在目录中找到 {len(nii_files)} 个nii.gz文件")
    
    # 重命名文件
    renamed_count = 0
    for filename in nii_files:
        # 提取当前文件的前9个字符
        filename_prefix = filename[:9]
        
        if filename_prefix in mapping_dict:
            original_name = mapping_dict[filename_prefix]
            
            old_path = os.path.join(directory_path, filename)
            new_path = os.path.join(directory_path, original_name)
            
            # 检查目标文件是否已存在
            if os.path.exists(new_path):
                print(f"警告: 目标文件已存在，跳过 {filename}")
                continue
            
            try:
                os.rename(old_path, new_path)
                print(f"重命名: {filename} -> {original_name}")
                renamed_count += 1
            except Exception as e:
                print(f"重命名 {filename} 时出错: {e}")
        else:
            print(f"跳过: {filename} (前9个字符 '{filename_prefix}' 在映射文件中未找到对应关系)")
    
    print(f"\n重命名完成! 成功重命名 {renamed_count} 个文件")

# 使用示例
if __name__ == "__main__":
    directory_to_rename = "/media/dell/T7 Shield1/nnunet/AllData/GXZL/finished/HBP/pre/prelivrtumor/Group5" # /media/dell/T7 Shield1/nnunet/AllData/GXZL/finished/HBP/pre/prelivrtumor/Group3
    mapping_file = "/media/dell/T7 Shield1/nnunet/AllData/GXZL/finished/HBP/nii/name5.txt"
    
    rename_files_using_mapping_partial(directory_to_rename, mapping_file)