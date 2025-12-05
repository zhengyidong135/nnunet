import os
import shutil
import pydicom
import re
from pathlib import Path
from collections import defaultdict

def find_non_common_folders(dir1, dir2):
    """
    找到dir1中存在但dir2中不存在的文件夹
    """
    if not os.path.exists(dir1):
        raise ValueError(f"源目录不存在: {dir1}")
    
    # 获取dir1中的所有子文件夹
    dir1_folders = set()
    for item in os.listdir(dir1):
        item_path = os.path.join(dir1, item)
        if os.path.isdir(item_path):
            dir1_folders.add(item)
    
    # 如果dir2不存在，则所有dir1的文件夹都是非共有的
    if not os.path.exists(dir2):
        return list(dir1_folders)
    
    # 获取dir2中的所有子文件夹
    dir2_folders = set()
    for item in os.listdir(dir2):
        item_path = os.path.join(dir2, item)
        if os.path.isdir(item_path):
            dir2_folders.add(item)
    
    # 返回dir1中有但dir2中没有的文件夹
    non_common = dir1_folders - dir2_folders
    return list(non_common)

def clean_folder_name(name):
    """
    清理文件夹名称，移除特殊字符
    """
    if not name or name == '':
        return "Unknown_Series"
    
    # 移除特殊字符
    cleaned = re.sub(r'[^\w\s\u4e00-\u9fff-]', '', name, flags=re.UNICODE)
    # 替换空格和下划线
    cleaned = re.sub(r'[\s]+', '_', cleaned)
    # 移除首尾的下划线
    cleaned = cleaned.strip('_')
    
    # 如果清理后为空，返回默认值
    if not cleaned:
        cleaned = "Unknown_Series"
    
    return cleaned

def get_series_info(dicom_file):
    """
    从DICOM文件中获取SeriesDescription和其他信息
    """
    try:
        # 尝试读取DICOM文件
        ds = pydicom.dcmread(dicom_file, force=True, stop_before_pixels=True)
        
        # 获取SeriesDescription
        series_desc = getattr(ds, 'SeriesDescription', None)
        
        # 如果SeriesDescription为空，尝试其他字段
        if not series_desc:
            # 尝试ProtocolName
            series_desc = getattr(ds, 'ProtocolName', None)
        
        # 如果还是没有，尝试SequenceName或SeriesNumber
        if not series_desc:
            series_desc = getattr(ds, 'SequenceName', None)
        
        if not series_desc:
            series_num = getattr(ds, 'SeriesNumber', None)
            if series_num:
                series_desc = f"Series_{series_num}"
            else:
                series_desc = "Unknown_Series"
        
        # 获取Modality
        modality = getattr(ds, 'Modality', 'OT')
        
        # 获取SeriesNumber用于排序
        series_number = getattr(ds, 'SeriesNumber', 9999)
        
        return {
            'description': str(series_desc),
            'modality': str(modality),
            'series_number': int(series_number) if str(series_number).isdigit() else 9999
        }
        
    except Exception as e:
        print(f"读取DICOM文件失败 {dicom_file}: {e}")
        return {
            'description': "Error_Reading_DICOM",
            'modality': "OT",
            'series_number': 9999
        }

def find_dicom_files(folder_path):
    """
    递归查找文件夹中的所有DICOM文件
    """
    dicom_files = []
    
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            
            # 检查是否是DICOM文件
            if file.lower().endswith(('.dcm', '.dicom', '.ima')):
                dicom_files.append(file_path)
            elif '.' not in file or file.lower().endswith(('.img', '.mag', '.rec')):
                dicom_files.append(file_path)
            else:
                # 尝试读取文件头判断是否是DICOM
                try:
                    with open(file_path, 'rb') as f:
                        f.seek(128)
                        if f.read(4) == b'DICM':
                            dicom_files.append(file_path)
                except:
                    pass
    
    return dicom_files

def classify_and_copy_with_numbering(source_folder, dest_base_folder, patient_folder_name):
    """
    分类并复制DICOM文件，文件夹命名前加上编号
    """
    # 查找所有DICOM文件
    dicom_files = find_dicom_files(source_folder)
    
    if not dicom_files:
        print(f"  在 {source_folder} 中没有找到DICOM文件")
        return 0, {}
    
    print(f"  找到 {len(dicom_files)} 个DICOM文件")
    
    # 第一阶段：收集所有不同的SeriesDescription并排序
    series_info_dict = {}
    
    for dicom_file in dicom_files:
        try:
            info = get_series_info(dicom_file)
            series_desc = info['description']
            
            if series_desc not in series_info_dict:
                series_info_dict[series_desc] = {
                    'info': info,
                    'count': 0,
                    'files': []
                }
            
            series_info_dict[series_desc]['files'].append(dicom_file)
            
        except Exception as e:
            print(f"  获取信息失败 {dicom_file}: {e}")
    
    # 按SeriesNumber排序，如果SeriesNumber相同按描述排序
    sorted_series = sorted(series_info_dict.items(), 
                          key=lambda x: (x[1]['info']['series_number'], x[1]['info']['description']))
    
    # 创建编号映射：01_, 02_, 03_...
    series_numbering = {}
    for idx, (series_desc, data) in enumerate(sorted_series, 1):
        # 格式化编号为两位数
        number_str = f"{idx:02d}"
        series_numbering[series_desc] = number_str
    
    # 第二阶段：复制文件
    processed_count = 0
    series_stats = {}
    
    for series_desc, number_str in series_numbering.items():
        files = series_info_dict[series_desc]['files']
        info = series_info_dict[series_desc]['info']
        
        # 清理系列描述
        cleaned_series_desc = clean_folder_name(series_desc)
        
        # 创建带编号的文件夹名
        numbered_folder_name = f"{number_str}_{cleaned_series_desc}"
        
        # 创建目标文件夹路径
        patient_dest_folder = os.path.join(dest_base_folder, patient_folder_name)
        series_dest_folder = os.path.join(patient_dest_folder, numbered_folder_name)
        
        # 创建文件夹
        os.makedirs(series_dest_folder, exist_ok=True)
        
        # 复制该系列的所有文件
        for dicom_file in files:
            try:
                # 生成目标文件名
                original_filename = os.path.basename(dicom_file)
                
                # 如果文件名没有扩展名，添加.dcm
                if '.' not in original_filename:
                    target_filename = original_filename + '.dcm'
                else:
                    target_filename = original_filename
                
                target_path = os.path.join(series_dest_folder, target_filename)
                
                # 处理文件名冲突
                counter = 1
                while os.path.exists(target_path):
                    name_part, ext = os.path.splitext(target_filename)
                    target_path = os.path.join(series_dest_folder, f"{name_part}_{counter}{ext}")
                    counter += 1
                
                # 复制文件
                shutil.copy2(dicom_file, target_path)
                processed_count += 1
                
            except Exception as e:
                print(f"  复制文件失败 {dicom_file}: {e}")
        
        # 更新统计
        series_stats[numbered_folder_name] = len(files)
        
        # 显示进度
        print(f"    {number_str}_{cleaned_series_desc}: {len(files)} 个文件")
    
    return processed_count, series_stats

def process_group5_with_numbering():
    """
    主处理函数 - 带编号版本
    """
    # 定义路径
    source_dir = "/media/dell/T7 Shield1/nnunet/AllData/GXZL/finished/dicom/Group5"
    compare_dir = "/media/dell/T7 Shield1/nnunet/AllData/GXZL/finished/dicom_规范化/Group5"
    dest_dir = "/media/dell/T7 Shield1/nnunet/AllData/GXZL/finished/dicom/Group5_sheng"
    
    print("=" * 80)
    print("开始处理 Group5 非共有文件夹 (带编号版本)")
    print("=" * 80)
    print(f"源目录: {source_dir}")
    print(f"比较目录: {compare_dir}")
    print(f"目标目录: {dest_dir}")
    print("-" * 80)
    
    # 检查源目录是否存在
    if not os.path.exists(source_dir):
        print(f"错误: 源目录不存在 - {source_dir}")
        return
    
    # 确保目标目录存在
    os.makedirs(dest_dir, exist_ok=True)
    
    # 找到非共有文件夹
    print("正在查找非共有文件夹...")
    non_common_folders = find_non_common_folders(source_dir, compare_dir)
    
    if not non_common_folders:
        print("没有找到非共有文件夹!")
        return
    
    print(f"找到 {len(non_common_folders)} 个非共有文件夹:")
    for folder in sorted(non_common_folders):
        print(f"  • {folder}")
    
    print("-" * 80)
    
    # 处理每个非共有文件夹
    total_files = 0
    all_series_stats = {}
    
    for folder in sorted(non_common_folders):
        print(f"\n处理患者文件夹: {folder}")
        
        # 源文件夹路径
        source_folder = os.path.join(source_dir, folder)
        
        # 处理并分类DICOM文件（带编号）
        processed_count, series_stats = classify_and_copy_with_numbering(
            source_folder, dest_dir, folder
        )
        
        # 更新总统计
        total_files += processed_count
        
        # 记录统计
        if series_stats:
            all_series_stats[folder] = series_stats
            print(f"  完成! 共处理 {processed_count} 个文件")
        else:
            print(f"  该文件夹没有DICOM文件")
    
    # 打印总体统计
    print("\n" + "=" * 80)
    print("处理完成!")
    print("=" * 80)
    print(f"总处理患者文件夹数: {len(non_common_folders)}")
    print(f"总处理文件数: {total_files}")
    
    # 显示文件夹命名示例
    print("\n文件夹命名示例:")
    print("-" * 80)
    for folder in sorted(all_series_stats.keys()):
        print(f"\n{folder}:")
        for series_name in sorted(all_series_stats[folder].keys()):
            print(f"  {series_name}")
    
    print(f"\n所有文件已保存到: {dest_dir}")
    print("=" * 80)
    
    # 保存统计信息到文件
    save_stats_to_file(all_series_stats, dest_dir)

def save_stats_to_file(stats, dest_dir):
    """
    保存统计信息到文件
    """
    stats_file = os.path.join(dest_dir, "处理统计.txt")
    
    with open(stats_file, 'w', encoding='utf-8') as f:
        f.write("DICOM文件处理统计报告\n")
        f.write("=" * 50 + "\n\n")
        
        total_patients = len(stats)
        total_files = sum(sum(series.values()) for series in stats.values())
        total_series = sum(len(series) for series in stats.values())
        
        f.write(f"总患者数: {total_patients}\n")
        f.write(f"总文件数: {total_files}\n")
        f.write(f"总系列数: {total_series}\n\n")
        
        f.write("详细统计:\n")
        f.write("=" * 50 + "\n\n")
        
        for patient in sorted(stats.keys()):
            f.write(f"患者: {patient}\n")
            f.write("-" * 40 + "\n")
            
            patient_total = sum(stats[patient].values())
            patient_series = len(stats[patient])
            
            f.write(f"文件数: {patient_total}\n")
            f.write(f"系列数: {patient_series}\n")
            f.write("系列列表:\n")
            
            for series_name in sorted(stats[patient].keys()):
                count = stats[patient][series_name]
                f.write(f"  {series_name}: {count} 个文件\n")
            
            f.write("\n")
    
    print(f"统计信息已保存到: {stats_file}")

def main():
    """
    主函数
    """
    try:
        process_group5_with_numbering()
    except KeyboardInterrupt:
        print("\n\n用户中断操作")
    except Exception as e:
        print(f"\n处理过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()