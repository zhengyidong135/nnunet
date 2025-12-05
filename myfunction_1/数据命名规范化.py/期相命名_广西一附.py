import os
import shutil
import pydicom
from pypinyin import lazy_pinyin
import re
from tqdm import tqdm
import json
from pathlib import Path
import time


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


def is_folder_processed(relative_folder_path, output_dir):
    """
    检查文件夹是否已经被处理（在输出目录中存在对应的文件夹结构）

    :param relative_folder_path: 相对于输入目录的文件夹路径
    :param output_dir: 输出目录
    :return: True如果文件夹已被处理，False否则
    """
    output_folder = os.path.join(output_dir, relative_folder_path)
    if os.path.exists(output_folder):
        # 检查输出文件夹是否非空
        if any(os.path.isdir(os.path.join(output_folder, item)) for item in os.listdir(output_folder)):
            return True
    return False


def get_unprocessed_folders(input_dir, output_dir, processed_files):
    """
    获取需要处理的文件夹列表，跳过已经处理好的文件夹

    :param input_dir: 输入目录
    :param output_dir: 输出目录
    :param processed_files: 已处理的文件列表
    :return: 需要处理的文件夹路径列表
    """
    unprocessed_folders = []

    # 遍历输入目录的所有子文件夹
    for root, dirs, files in os.walk(input_dir):
        # 获取相对于输入目录的路径
        relative_path = os.path.relpath(root, input_dir)

        # 跳过根目录本身
        if relative_path == '.':
            continue

        # 检查该文件夹是否已经被处理
        if not is_folder_processed(relative_path, output_dir):
            unprocessed_folders.append(root)
        else:
            print(f"跳过已处理的文件夹: {relative_path}")

    return unprocessed_folders


def process_file_group(file_group, input_dir, output_dir):
    """
    处理一组文件（五个为一组）

    :param file_group: 包含五个文件路径的列表
    :param input_dir: 输入目录
    :param output_dir: 输出目录
    :return: 成功处理的文件列表和失败的文件列表
    """
    processed_files = []
    failed_files = []

    for file_path in file_group:
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
            processed_files.append(file_path)

        except Exception as e:
            print(f"Error processing file {file_path}: {e}")
            failed_files.append(file_path)

    return processed_files, failed_files


def organize_dicom_files(input_dir, output_dir, progress_file, group_size=5, folder_rest_interval=30,
                         folder_rest_duration=45):
    """
    Organize DICOM files into subfolders based on Series information,
    while preserving the original folder structure. Process files in groups.

    :param input_dir: Path to the directory containing DICOM files.
    :param output_dir: Path to the directory where organized DICOM files will be saved.
    :param progress_file: Path to the file where progress will be saved.
    :param group_size: Number of files to process in each group (default: 5).
    :param folder_rest_interval: 处理多少个文件夹后休息（默认：30）
    :param folder_rest_duration: 文件夹处理休息时间（秒）（默认：45）
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    processed_files = load_progress(progress_file)

    # 获取需要处理的文件夹列表
    unprocessed_folders = get_unprocessed_folders(input_dir, output_dir, processed_files)

    if not unprocessed_folders:
        print("所有文件夹都已经被处理完成！")
        return

    print(f"需要处理的文件夹数量: {len(unprocessed_folders)}")

    # 文件夹处理计数器
    folder_processed_count = 0

    # 处理每个未处理的文件夹
    for folder_index, folder_path in enumerate(tqdm(unprocessed_folders, desc="Processing folders", ncols=100)):
        print(f"\n正在处理文件夹: {os.path.relpath(folder_path, input_dir)}")

        # 获取该文件夹中的所有文件
        all_files_in_folder = []
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                all_files_in_folder.append(file_path)

        # 过滤掉已处理的文件
        unprocessed_files = [file for file in all_files_in_folder if file not in processed_files]

        if not unprocessed_files:
            print(f"文件夹 {os.path.basename(folder_path)} 中没有需要处理的文件")
            continue

        # 将未处理的文件分成每组5个
        file_groups = [unprocessed_files[i:i + group_size] for i in range(0, len(unprocessed_files), group_size)]

        for group_index, file_group in enumerate(
                tqdm(file_groups, desc=f"Processing files in {os.path.basename(folder_path)}", ncols=100)):
            try:
                # 处理当前组的文件
                processed_in_group, failed_in_group = process_file_group(file_group, input_dir, output_dir)

                # 更新已处理的文件列表
                processed_files.extend(processed_in_group)

                # 每处理完一组就保存进度
                save_progress(processed_files, progress_file)

                # 输出当前组处理情况
                if failed_in_group:
                    print(
                        f"Group {group_index + 1}: Processed {len(processed_in_group)} files, failed {len(failed_in_group)} files")
                else:
                    print(f"Group {group_index + 1}: Successfully processed {len(processed_in_group)} files")

            except Exception as e:
                print(f"Error processing group {group_index + 1}: {e}")
                # 如果整组处理失败，记录失败的文件
                for file_path in file_group:
                    print(f"Failed to process: {file_path}")

        # 完成一个文件夹的处理，计数器加1
        folder_processed_count += 1

        # 检查是否需要休息（每处理完30个文件夹休息45秒）
        if folder_processed_count >= folder_rest_interval:
            print(f"\n已处理 {folder_processed_count} 个文件夹，休息 {folder_rest_duration} 秒...")

            # 倒计时显示
            for i in range(folder_rest_duration, 0, -1):
                print(f"\r剩余休息时间: {i} 秒", end="", flush=True)
                time.sleep(1)
            print("\r休息结束，继续处理...")

            # 重置计数器
            folder_processed_count = 0


def copy_with_original_structure(input_dir, output_dir):
    """
    直接将输入目录的所有内容复制到输出目录，保持原始文件夹结构

    :param input_dir: 输入目录
    :param output_dir: 输出目录
    """
    print("开始复制文件并保持原始文件夹结构...")

    # 使用shutil.copytree保持原始结构
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)

    shutil.copytree(input_dir, output_dir)
    print(f"复制完成: {input_dir} -> {output_dir}")


def organize_dicom_files_simple(input_dir, output_dir, progress_file, group_size=5, folder_rest_interval=30,
                                folder_rest_duration=45):
    """
    简化的DICOM文件组织，只按序列信息组织，不创建患者子文件夹。五个为一组处理。

    :param input_dir: 输入目录
    :param output_dir: 输出目录
    :param progress_file: 进度文件
    :param group_size: 每组处理的文件数量（默认：5）
    :param folder_rest_interval: 处理多少个文件夹后休息（默认：30）
    :param folder_rest_duration: 文件夹处理休息时间（秒）（默认：45）
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    processed_files = load_progress(progress_file)

    # 获取需要处理的文件夹列表
    unprocessed_folders = get_unprocessed_folders(input_dir, output_dir, processed_files)

    if not unprocessed_folders:
        print("所有文件夹都已经被处理完成！")
        return

    print(f"需要处理的文件夹数量: {len(unprocessed_folders)}")

    # 文件夹处理计数器
    folder_processed_count = 0

    # 处理每个未处理的文件夹
    for folder_index, folder_path in enumerate(tqdm(unprocessed_folders, desc="Processing folders", ncols=100)):
        print(f"\n正在处理文件夹: {os.path.relpath(folder_path, input_dir)}")

        # 获取该文件夹中的所有文件
        all_files_in_folder = []
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                all_files_in_folder.append(file_path)

        # 过滤掉已处理的文件
        unprocessed_files = [file for file in all_files_in_folder if file not in processed_files]

        if not unprocessed_files:
            print(f"文件夹 {os.path.basename(folder_path)} 中没有需要处理的文件")
            continue

        # 将未处理的文件分成每组5个
        file_groups = [unprocessed_files[i:i + group_size] for i in range(0, len(unprocessed_files), group_size)]

        for group_index, file_group in enumerate(
                tqdm(file_groups, desc=f"Processing files in {os.path.basename(folder_path)}", ncols=100)):
            try:
                processed_in_group = []
                failed_in_group = []

                for file_path in file_group:
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
                        processed_in_group.append(file_path)

                    except Exception as e:
                        print(f"Error processing file {file_path}: {e}")
                        failed_in_group.append(file_path)

                # 更新已处理的文件列表
                processed_files.extend(processed_in_group)

                # 每处理完一组就保存进度
                save_progress(processed_files, progress_file)

                # 输出当前组处理情况
                if failed_in_group:
                    print(
                        f"Group {group_index + 1}: Processed {len(processed_in_group)} files, failed {len(failed_in_group)} files")
                else:
                    print(f"Group {group_index + 1}: Successfully processed {len(processed_in_group)} files")

            except Exception as e:
                print(f"Error processing group {group_index + 1}: {e}")
                # 如果整组处理失败，记录失败的文件
                for file_path in file_group:
                    print(f"Failed to process: {file_path}")

        # 完成一个文件夹的处理，计数器加1
        folder_processed_count += 1

        # 检查是否需要休息（每处理完30个文件夹休息45秒）
        if folder_processed_count >= folder_rest_interval:
            print(f"\n已处理 {folder_processed_count} 个文件夹，休息 {folder_rest_duration} 秒...")

            # 倒计时显示
            for i in range(folder_rest_duration, 0, -1):
                print(f"\r剩余休息时间: {i} 秒", end="", flush=True)
                time.sleep(1)
            print("\r休息结束，继续处理...")

            # 重置计数器
            folder_processed_count = 0


def process_all_groups(base_input_dir, base_output_dir, base_progress_file, start_group=3, end_group=8,
                       group_rest_duration=60):
    """
    批量处理组3到组8

    :param base_input_dir: 基础输入目录路径（不包含组号）
    :param base_output_dir: 基础输出目录路径（不包含组号）
    :param base_progress_file: 基础进度文件路径（不包含组号）
    :param start_group: 起始组号
    :param end_group: 结束组号
    :param group_rest_duration: 组间休息时间（秒）（默认：60）
    """
    for group_num in range(start_group, end_group + 1):
        print(f"\n{'=' * 60}")
        print(f"开始处理组{group_num}")
        print(f"{'=' * 60}")

        # 构建具体的路径
        input_dir = os.path.join(base_input_dir, f"Group{group_num}")
        output_dir = os.path.join(base_output_dir, f"Group{group_num}_规范化")

        # 修复：动态生成进度文件名，根据组号添加后缀
        progress_file_name, progress_file_ext = os.path.splitext(base_progress_file)
        progress_file = f"{progress_file_name}_{group_num}{progress_file_ext}"

        # 检查输入目录是否存在
        if not os.path.exists(input_dir):
            print(f"警告：输入目录不存在，跳过组{group_num}: {input_dir}")
            continue

        print(f"输入目录: {input_dir}")
        print(f"输出目录: {output_dir}")
        print(f"进度文件: {progress_file}")

        # 处理当前组
        try:
            organize_dicom_files(input_dir, output_dir, progress_file,
                                 group_size=5, folder_rest_interval=30, folder_rest_duration=45)
            print(f"组{group_num}处理完成！")
        except Exception as e:
            print(f"处理组{group_num}时出现错误: {e}")

        # 组间休息1分钟，避免连续处理
        if group_num < end_group:
            print(f"\n组{group_num}处理完成，准备处理下一组，休息{group_rest_duration}秒...")

            # 倒计时显示（分钟:秒格式）
            for i in range(group_rest_duration, 0, -1):
                minutes = i // 60
                seconds = i % 60
                print(f"\r下一组开始倒计时: {minutes:02d}:{seconds:02d}", end="", flush=True)
                time.sleep(1)
            print("\r开始处理下一组...")


if __name__ == '__main__':
    # 基础路径配置
    base_dir = "/media/dell/T7 Shield1/nnunet/AllData/GXZL/finished/dicom"
    base_progress_file = "/media/dell/T7 Shield1/nnunet/AllData/GXZL/finished.json"

    # 选择处理方式：

    # 方式1: 批量处理组3到组8
    print("批量处理组3到组8")
    process_all_groups(base_dir, base_dir, base_progress_file, start_group=1, end_group=1, group_rest_duration=60)

    # 方式2: 单独处理某个组（如果需要）
    # group_num = 2  # 指定要处理的组号
    # input_dir = os.path.join(base_dir, f"组{group_num}")
    # output_dir = os.path.join(base_dir, f"组{group_num}_规范化")
    # progress_file_name, progress_file_ext = os.path.splitext(base_progress_file)
    # progress_file = f"{progress_file_name}_{group_num}{progress_file_ext}"
    # organize_dicom_files(input_dir, output_dir, progress_file,
    #                     group_size=5, folder_rest_interval=30, folder_rest_duration=45)

    # 方式3: 直接复制保持原始结构
    # print("方式2: 直接复制保持原始文件夹结构")
    # copy_with_original_structure(input_dir, output_dir)

    # 方式4: 简化的组织方式
    # print("方式3: 简化的组织方式，只按序列信息组织（五个为一组）")
    # organize_dicom_files_simple(input_dir, output_dir, progress_file,
    #                           group_size=5, folder_rest_interval=30, folder_rest_duration=45)