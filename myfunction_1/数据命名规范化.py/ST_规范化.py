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


def get_specified_patient_folders(input_dir, source_dir):
    """
    根据源目录中的文件夹名来获取输入目录中对应的患者文件夹

    :param input_dir: 输入目录 (SDYFY_100)
    :param source_dir: 源目录 (SDYFY_100_exist_dicom)
    :return: 患者文件夹路径列表
    """
    patient_folders = []
    
    # 获取源目录中的所有文件夹名
    if not os.path.exists(source_dir):
        print(f"❌ 源目录不存在: {source_dir}")
        return patient_folders
    
    source_folders = []
    for item in os.listdir(source_dir):
        item_path = os.path.join(source_dir, item)
        if os.path.isdir(item_path):
            source_folders.append(item)
    
    print(f"✅ 从源目录中找到 {len(source_folders)} 个文件夹")
    
    # 在输入目录中查找对应的文件夹
    if not os.path.exists(input_dir):
        print(f"❌ 输入目录不存在: {input_dir}")
        return patient_folders
    
    for folder_name in source_folders:
        folder_path = os.path.join(input_dir, folder_name)
        if os.path.exists(folder_path) and os.path.isdir(folder_path):
            patient_folders.append(folder_path)
        else:
            print(f"⚠️  在输入目录中未找到对应文件夹: {folder_name}")
    
    print(f"✅ 在输入目录中找到 {len(patient_folders)} 个对应的患者文件夹")
    return patient_folders


def organize_dicom_files_specified(input_dir, output_dir, progress_file, source_dir):
    """
    根据源目录中的文件夹名来处理对应的DICOM文件

    :param input_dir: 包含DICOM文件的目录 (SDYFY_100)
    :param output_dir: 组织后的DICOM文件保存目录
    :param progress_file: 进度保存文件路径
    :param source_dir: 源目录，提供要处理的文件夹名 (SDYFY_100_exist_dicom)
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    processed_files = load_progress(progress_file)

    # 根据源目录获取要处理的患者文件夹
    patient_folders = get_specified_patient_folders(input_dir, source_dir)

    if not patient_folders:
        print("❌ 没有找到要处理的患者文件夹")
        return

    print(f"📁 要处理的 {len(patient_folders)} 个患者文件夹:")
    for patient_folder in patient_folders:
        print(f"  - {os.path.basename(patient_folder)}")

    # 收集需要处理的文件（只包含指定患者文件夹中的文件）
    files_to_process = []
    for patient_folder in patient_folders:
        for root, _, files in os.walk(patient_folder):
            for file in files:
                file_path = os.path.join(root, file)
                if file_path not in processed_files:
                    files_to_process.append(file_path)

    print(f"📄 找到 {len(files_to_process)} 个未处理的DICOM文件")

    if not files_to_process:
        print("✅ 所有文件都已处理完成")
        return

    # 处理文件
    for file_path in tqdm(files_to_process, desc="处理DICOM文件", ncols=100):
        try:
            # 读取DICOM文件
            dicom = pydicom.dcmread(file_path, force=True)

            # 提取相关元数据
            series_description = dicom.SeriesDescription
            series_number = dicom.SeriesNumber

            # 清理序列描述以确保是有效的目录名
            series_description_clean = clean_filename(series_description)
            series_folder_name = f"{series_number:03}_{series_description_clean}"

            # 获取原始文件夹结构
            original_structure = get_original_folder_structure(file_path, input_dir)

            # 在输出目录下创建原始文件夹结构
            original_structure_dir = os.path.join(output_dir, original_structure)

            # 在原始文件夹结构下创建序列文件夹
            series_dir = os.path.join(original_structure_dir, series_folder_name)

            if not os.path.exists(series_dir):
                os.makedirs(series_dir)

            # 复制DICOM文件到新目录（保持原始文件名）
            shutil.copy2(file_path, series_dir)

            # 更新已处理文件列表并保存进度
            processed_files.append(file_path)
            save_progress(processed_files, progress_file)

        except Exception as e:
            print(f"❌ 处理文件出错 {file_path}: {e}")

    print(f"✅ 处理完成！共处理了 {len(files_to_process)} 个文件")


if __name__ == '__main__':
    input_dir = "/media/dell/T7 Shield/nnunet/AllData/ST/finished/ST_最终入组_96"
    output_dir = "/media/dell/T7 Shield/nnunet/AllData/ST/finished/ST_命名规范化"
    progress_file = "/media/dell/T7 Shield/nnunet/AllData/ST/KMTH_HCC_CT_38_CT_dicom_classification_HCC.json"
    source_dir = "/media/dell/T7 Shield/nnunet/AllData/ST/SDYFY_100_exist_dicom" # 新增源目录

    print("🔄 开始处理指定文件夹中的病例...")
    organize_dicom_files_specified(input_dir, output_dir, progress_file, source_dir)