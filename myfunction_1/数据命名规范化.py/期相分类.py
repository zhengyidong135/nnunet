import os
import shutil
import pydicom
from pypinyin import lazy_pinyin
import re
from tqdm import tqdm
import json
from pathlib import Path


def convert_name_to_pinyin(name):
    """
    Convert Chinese name to pinyin and remove any spaces and special characters.

    :param name: Chinese name.
    :return: Name in pinyin without spaces and special characters.
    """
    cleaned_name = re.sub(r'\([^)]*\)', '', name)  # Remove anything in parentheses
    cleaned_name = re.sub(r'[^\x00-\x7F]+', '', cleaned_name)
    return ''.join(lazy_pinyin(cleaned_name)).replace(' ', '')


def clean_filename(filename):
    """
    Remove or replace characters that are not allowed in file paths.

    :param filename: The original filename.
    :return: A cleaned filename.
    """
    return re.sub(r'[<>:"/\\|?*]', '', filename)


def save_progress(processed_files, progress_file):
    """
    Save the list of processed files to a JSON file using a temporary file.

    :param processed_files: List of processed files.
    :param progress_file: Path to the progress file.
    """
    temp_file = progress_file + '.tmp'
    with open(temp_file, 'w') as f:
        json.dump(processed_files, f)
    os.replace(temp_file, progress_file)


def load_progress(progress_file):
    """
    Load the list of processed files from a JSON file.

    :param progress_file: Path to the progress file.
    :return: List of processed files.
    """
    if os.path.exists(progress_file):
        with open(progress_file, 'r') as f:
            return json.load(f)
    return []


def get_original_folder_structure(file_path, input_dir):
    """
    获取文件相对于输入目录的原始文件夹结构
    
    :param file_path: 文件的完整路径
    :param input_dir: 输入目录的根路径
    :return: 原始文件夹结构路径
    """
    # 获取相对于输入目录的路径
    relative_path = os.path.relpath(file_path, input_dir)
    # 获取文件所在的文件夹路径（去掉文件名）
    folder_path = os.path.dirname(relative_path)
    return folder_path


def get_common_folders(input_dir, output_dir):
    """
    获取输入目录和输出目录中共同存在的文件夹路径
    
    :param input_dir: 输入目录
    :param output_dir: 输出目录
    :return: 共同存在的文件夹路径列表
    """
    common_folders = []
    
    if not os.path.exists(output_dir):
        return common_folders
    
    # 遍历输入目录的所有子文件夹
    for root, dirs, files in os.walk(input_dir):
        # 获取相对于输入目录的路径
        relative_path = os.path.relpath(root, input_dir)
        
        # 如果这是根目录本身，跳过
        if relative_path == '.':
            continue
            
        # 检查输出目录中是否存在相同的相对路径
        corresponding_output_path = os.path.join(output_dir, relative_path)
        if os.path.exists(corresponding_output_path):
            common_folders.append(relative_path)
    
    return common_folders


def should_process_file(file_path, input_dir, common_folders):
    """
    检查文件是否应该被处理（不在共同存在的文件夹中）
    
    :param file_path: 文件路径
    :param input_dir: 输入目录
    :param common_folders: 共同存在的文件夹列表
    :return: 是否应该处理该文件
    """
    # 获取文件相对于输入目录的文件夹路径
    relative_folder = os.path.dirname(os.path.relpath(file_path, input_dir))
    
    # 如果文件在根目录，直接处理
    if relative_folder == '.':
        return True
    
    # 检查文件是否在任何共同存在的文件夹中
    for common_folder in common_folders:
        if relative_folder.startswith(common_folder):
            return False
    
    return True


def organize_dicom_files(input_dir, output_dir, progress_file):
    """
    Organize DICOM files into subfolders based on Series information,
    while preserving the original folder structure.

    :param input_dir: Path to the directory containing DICOM files.
    :param output_dir: Path to the directory where organized DICOM files will be saved.
    :param progress_file: Path to the file where progress will be saved.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    processed_files = load_progress(progress_file)
    
    # 获取共同存在的文件夹
    common_folders = get_common_folders(input_dir, output_dir)
    if common_folders:
        print(f"发现 {len(common_folders)} 个共同存在的文件夹，将跳过处理这些文件夹中的文件:")
        for folder in common_folders:
            print(f"  - {folder}")

    # Iterate through all files in the input directory
    all_files = [os.path.join(root, file) for root, _, files in os.walk(input_dir) for file in files]
    
    # 过滤掉已经在共同存在文件夹中的文件
    all_files = [file for file in all_files if should_process_file(file, input_dir, common_folders)]
    
    unprocessed_files = [file for file in all_files if file not in processed_files]

    print(f"总文件数: {len(all_files)}，待处理文件数: {len(unprocessed_files)}")

    for file_path in tqdm(unprocessed_files, desc="Processing DICOM files", ncols=100):
        try:
            # Read the DICOM file
            dicom = pydicom.dcmread(file_path, force=True)

            # Extract relevant metadata
            series_description = dicom.SeriesDescription
            series_number = dicom.SeriesNumber

            # Clean series description to ensure it's a valid directory name
            series_description_clean = clean_filename(series_description)
            series_folder_name = f"{series_number:03}_{series_description_clean}"

            # Get original folder structure
            original_structure = get_original_folder_structure(file_path, input_dir)
            
            # 在输出目录下创建原始文件夹结构
            original_structure_dir = os.path.join(output_dir, original_structure)
            
            # 在原始文件夹结构下创建序列文件夹
            series_dir = os.path.join(original_structure_dir, series_folder_name)

            if not os.path.exists(series_dir):
                os.makedirs(series_dir)

            # Copy the DICOM file to the new directory (保持原始文件名)
            shutil.copy2(file_path, series_dir)

            # Update the list of processed files and save progress
            processed_files.append(file_path)
            save_progress(processed_files, progress_file)

        except Exception as e:
            print(f"Error processing file {file_path}: {e}")


def copy_with_original_structure(input_dir, output_dir):
    """
    直接将输入目录的所有内容复制到输出目录，保持原始文件夹结构
    
    :param input_dir: 输入目录
    :param output_dir: 输出目录
    """
    print("开始复制文件并保持原始文件夹结构...")
    
    # 获取共同存在的文件夹
    common_folders = get_common_folders(input_dir, output_dir)
    if common_folders:
        print(f"发现 {len(common_folders)} 个共同存在的文件夹，将跳过复制这些文件夹:")
        for folder in common_folders:
            print(f"  - {folder}")
    
    # 使用shutil.copytree但跳过共同存在的文件夹
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    
    # 创建自定义复制函数来跳过共同存在的文件夹
    def ignore_func(src, names):
        ignored = set()
        relative_src = os.path.relpath(src, input_dir)
        
        # 如果当前目录是共同存在的文件夹，忽略所有内容
        if relative_src in common_folders:
            return names
        
        # 检查当前目录是否是共同存在文件夹的子目录
        for common_folder in common_folders:
            if relative_src.startswith(common_folder + os.sep):
                return names
        
        return ignored
    
    shutil.copytree(input_dir, output_dir, ignore=ignore_func)
    print(f"复制完成: {input_dir} -> {output_dir}")


def organize_dicom_files_simple(input_dir, output_dir, progress_file):
    """
    简化的DICOM文件组织，只按序列信息组织，不创建患者子文件夹
    
    :param input_dir: 输入目录
    :param output_dir: 输出目录
    :param progress_file: 进度文件
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    processed_files = load_progress(progress_file)
    
    # 获取共同存在的文件夹
    common_folders = get_common_folders(input_dir, output_dir)
    if common_folders:
        print(f"发现 {len(common_folders)} 个共同存在的文件夹，将跳过处理这些文件夹中的文件:")
        for folder in common_folders:
            print(f"  - {folder}")

    # Iterate through all files in the input directory
    all_files = [os.path.join(root, file) for root, _, files in os.walk(input_dir) for file in files]
    
    # 过滤掉已经在共同存在文件夹中的文件
    all_files = [file for file in all_files if should_process_file(file, input_dir, common_folders)]
    
    unprocessed_files = [file for file in all_files if file not in processed_files]

    print(f"总文件数: {len(all_files)}，待处理文件数: {len(unprocessed_files)}")

    for file_path in tqdm(unprocessed_files, desc="Processing DICOM files", ncols=100):
        try:
            # Read the DICOM file
            dicom = pydicom.dcmread(file_path, force=True)

            # Extract relevant metadata
            series_description = dicom.SeriesDescription
            series_number = dicom.SeriesNumber

            # Clean series description to ensure it's a valid directory name
            series_description_clean = clean_filename(series_description)
            series_folder_name = f"{series_number:03}_{series_description_clean}"

            # 直接在输出目录下创建序列文件夹
            series_dir = os.path.join(output_dir, series_folder_name)

            if not os.path.exists(series_dir):
                os.makedirs(series_dir)

            # Copy the DICOM file to the new directory (保持原始文件名)
            shutil.copy2(file_path, series_dir)

            # Update the list of processed files and save progress
            processed_files.append(file_path)
            save_progress(processed_files, progress_file)

        except Exception as e:
            print(f"Error processing file {file_path}: {e}")


if __name__ == '__main__':
    input_dir = "/media/dell/T7 Shield1/nnunet/AllData/GXZL/finished/dicom/Group4"
    output_dir = "/media/dell/T7 Shield1/nnunet/AllData/GXZL/finished/dicom_规范化/Group4"
    progress_file = '/media/dell/T7 Shield1/nnunet/AllData/GXZL/finished.json'
    
    # 选择其中一种方式：
    # 方式1: 保持原始文件夹结构并按序列信息组织（推荐）
    print("方式1: 保持原始文件夹结构并按序列信息组织")
    organize_dicom_files(input_dir, output_dir, progress_file)
    # # 方式2: 直接复制保持原始结构
    # print("方式2: 直接复制保持原始文件夹结构")
    # copy_with_original_structure(input_dir, output_dir)
    
    # # 方式3: 简化的组织方式，只按序列信息组织
    # print("方式3: 简化的组织方式，只按序列信息组织")
    # organize_dicom_files_simple(input_dir, output_dir, progress_file)