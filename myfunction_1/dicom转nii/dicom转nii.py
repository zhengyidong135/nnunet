import os
import pydicom
import numpy as np
import nibabel as nib
from pathlib import Path
import logging
from tqdm import tqdm
import SimpleITK as sitk
import re
import subprocess
import shutil
import tempfile

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def is_dicom_file(file_path):
    """检查文件是否为DICOM文件"""
    try:
        pydicom.dcmread(file_path, stop_before_pixels=True)
        return True
    except:
        return False

def get_all_dicom_files(directory):
    """获取目录及其所有子目录中的所有DICOM文件"""
    dicom_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            if is_dicom_file(file_path):
                dicom_files.append(file_path)
    return dicom_files

def sort_dicom_files_by_instance_number(dicom_files):
    """根据InstanceNumber对DICOM文件进行排序"""
    files_with_instance = []
    files_without_instance = []
    
    for file_path in dicom_files:
        try:
            ds = pydicom.dcmread(file_path, stop_before_pixels=True)
            if hasattr(ds, 'InstanceNumber') and ds.InstanceNumber is not None:
                files_with_instance.append((file_path, int(ds.InstanceNumber)))
            else:
                files_without_instance.append(file_path)
        except:
            files_without_instance.append(file_path)
    
    # 按InstanceNumber排序
    files_with_instance.sort(key=lambda x: x[1])
    sorted_files = [x[0] for x in files_with_instance] + files_without_instance
    
    return sorted_files

def convert_dicom_series_to_nifti(dicom_files, output_path):
    """将DICOM文件序列转换为NIfTI格式，保持原始方向"""
    try:
        if not dicom_files:
            logger.warning("没有DICOM文件可转换")
            return False
        
        # 使用SimpleITK读取DICOM序列
        reader = sitk.ImageSeriesReader()
        
        # 获取DICOM序列的文件名
        dicom_files_sorted = sort_dicom_files_by_instance_number(dicom_files)
        
        # 设置DICOM文件
        reader.SetFileNames(dicom_files_sorted)
        
        # 读取图像
        image = reader.Execute()
        
        # 获取原始方向信息
        direction = image.GetDirection()
        origin = image.GetOrigin()
        spacing = image.GetSpacing()
        
        # 显示原始方向信息
        orientation_codes = []
        for i in range(3):
            axis_vector = direction[i*3:(i+1)*3]
            if np.allclose(axis_vector, [1, 0, 0]):
                orientation_codes.append('R')
            elif np.allclose(axis_vector, [-1, 0, 0]):
                orientation_codes.append('L')
            elif np.allclose(axis_vector, [0, 1, 0]):
                orientation_codes.append('A')
            elif np.allclose(axis_vector, [0, -1, 0]):
                orientation_codes.append('P')
            elif np.allclose(axis_vector, [0, 0, 1]):
                orientation_codes.append('S')
            elif np.allclose(axis_vector, [0, 0, -1]):
                orientation_codes.append('I')
            else:
                orientation_codes.append('?')
        
        orientation_str = ''.join(orientation_codes)
        print(f"  🧭 原始DICOM方向: {orientation_str}")
        
        # 直接保存为NIfTI，保持原始方向
        sitk.WriteImage(image, output_path)
        
        logger.info(f"成功保存: {output_path} (方向: {orientation_str})")
        return True
        
    except Exception as e:
        logger.error(f"转换失败: {str(e)}")
        return False

def process_first_level_directory(first_level_dir, output_base_dir):
    """处理单个一级子文件夹"""
    dicom_files = get_all_dicom_files(first_level_dir)
    
    if not dicom_files:
        logger.warning(f"在 {first_level_dir} 中未找到DICOM文件")
        return False
    
    # 创建输出文件名（使用一级文件夹名称）
    first_level_name = os.path.basename(first_level_dir)
    output_filename = f"{first_level_name}.nii.gz"
    output_path = os.path.join(output_base_dir, output_filename)
    
    logger.info(f"处理 {first_level_name}, 找到 {len(dicom_files)} 个DICOM文件")
    
    # 转换为NIfTI
    success = convert_dicom_series_to_nifti(dicom_files, output_path)
    
    if success:
        logger.info(f"成功转换: {first_level_name} -> {output_filename}")
    else:
        logger.error(f"转换失败: {first_level_name}")
    
    return success

def main_simpleitk(input_base_dir, output_base_dir):
    """主转换函数 - 使用SimpleITK保持原始方向"""
    print("开始使用SimpleITK转换DICOM到NIfTI (保持原始方向)...")
    print(f"输入目录: {input_base_dir}")
    print(f"输出目录: {output_base_dir}")
    print("=" * 60)
    
    # 检查输入目录是否存在
    if not os.path.exists(input_base_dir):
        print(f"错误: 输入目录不存在: {input_base_dir}")
        return False
    
    # 创建输出目录
    os.makedirs(output_base_dir, exist_ok=True)
    
    # 获取所有一级子文件夹
    try:
        first_level_dirs = []
        for item in os.listdir(input_base_dir):
            item_path = os.path.join(input_base_dir, item)
            if os.path.isdir(item_path):
                first_level_dirs.append(item_path)
    except Exception as e:
        logger.error(f"无法读取输入目录: {str(e)}")
        return False
    
    logger.info(f"找到 {len(first_level_dirs)} 个一级子文件夹")
    
    total_converted = 0
    total_failed = 0
    
    # 处理每个一级子文件夹
    for first_level_dir in tqdm(first_level_dirs, desc="转换DICOM序列"):
        success = process_first_level_directory(first_level_dir, output_base_dir)
        if success:
            total_converted += 1
        else:
            total_failed += 1
    
    print("=" * 60)
    print("SimpleITK转换完成!")
    print(f"成功: {total_converted}, 失败: {total_failed}")
    return total_converted > 0

def is_dcm2niix_available():
    """检查dcm2niix是否可用"""
    try:
        result = subprocess.run(['dcm2niix', '--version'], 
                              capture_output=True, text=True, timeout=10)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return False

def main_dcm2niix(input_base_dir, output_base_dir):
    """使用dcm2niix进行转换，保持原始方向"""
    print("开始使用dcm2niix转换DICOM到NIfTI (保持原始方向)...")
    print(f"输入目录: {input_base_dir}")
    print(f"输出目录: {output_base_dir}")
    print("=" * 60)
    
    # 检查输入目录是否存在
    if not os.path.exists(input_base_dir):
        print(f"错误: 输入目录不存在: {input_base_dir}")
        return False
    
    # 检查dcm2niix是否可用
    if not is_dcm2niix_available():
        print("错误: dcm2niix未安装或不在PATH中")
        print("将使用SimpleITK方法替代...")
        return main_simpleitk(input_base_dir, output_base_dir)
    
    # 创建输出目录
    os.makedirs(output_base_dir, exist_ok=True)
    
    # 获取所有一级子文件夹
    first_level_dirs = []
    for item in os.listdir(input_base_dir):
        item_path = os.path.join(input_base_dir, item)
        if os.path.isdir(item_path):
            first_level_dirs.append(item_path)
    
    logger.info(f"找到 {len(first_level_dirs)} 个一级子文件夹")
    
    total_converted = 0
    total_failed = 0
    
    # 创建临时工作目录
    with tempfile.TemporaryDirectory() as temp_dir:
        for first_level_dir in tqdm(first_level_dirs, desc="dcm2niix转换"):
            first_level_name = os.path.basename(first_level_dir)
            output_filename = f"{first_level_name}.nii.gz"
            output_path = os.path.join(output_base_dir, output_filename)
            
            try:
                # 清空临时目录
                for file in os.listdir(temp_dir):
                    file_path = os.path.join(temp_dir, file)
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                
                # 使用dcm2niix转换，不强制方向
                cmd = [
                    'dcm2niix',
                    '-b', 'y',          # 生成JSON sidecar
                    '-z', 'y',          # 压缩输出
                    '-f', '%p_%s',      # 文件名格式: 协议_序列
                    '-o', temp_dir,     # 输出目录
                    first_level_dir     # 输入目录
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                
                if result.returncode != 0:
                    logger.warning(f"dcm2niix返回非零状态: {result.stderr}")
                
                # 检查临时目录中生成的文件
                nifti_files = [f for f in os.listdir(temp_dir) 
                              if f.endswith(('.nii.gz', '.nii'))]
                
                if nifti_files:
                    # 如果有多个文件，选择第一个（通常是最主要的）
                    source_file = os.path.join(temp_dir, nifti_files[0])
                    
                    # 移动到目标位置并重命名
                    if source_file.endswith('.nii') and output_path.endswith('.nii.gz'):
                        # 如果需要压缩，重新保存
                        img = nib.load(source_file)
                        nib.save(img, output_path)
                        os.remove(source_file)
                    else:
                        shutil.move(source_file, output_path)
                    
                    logger.info(f"成功转换: {first_level_name} -> {output_filename}")
                    total_converted += 1
                    
                    # 同时移动JSON sidecar文件（如果有）
                    json_files = [f for f in os.listdir(temp_dir) if f.endswith('.json')]
                    for json_file in json_files:
                        json_source = os.path.join(temp_dir, json_file)
                        json_dest = os.path.join(output_base_dir, 
                                               f"{first_level_name}.json")
                        shutil.move(json_source, json_dest)
                    
                else:
                    logger.warning(f"在 {first_level_name} 中未生成NIfTI文件")
                    logger.warning(f"dcm2niix输出: {result.stdout}")
                    if result.stderr:
                        logger.warning(f"dcm2niix错误: {result.stderr}")
                    total_failed += 1
                    
            except subprocess.TimeoutExpired:
                logger.error(f"dcm2niix转换超时: {first_level_name}")
                total_failed += 1
            except Exception as e:
                logger.error(f"dcm2niix转换失败 {first_level_name}: {str(e)}")
                total_failed += 1
    
    print("=" * 60)
    print("dcm2niix转换完成!")
    print(f"成功: {total_converted}, 失败: {total_failed}")
    
    return total_converted > 0

def verify_orientations(output_base_dir):
    """验证输出目录中所有NIfTI文件的方向"""
    print("\n" + "="*60)
    print("🧭 验证输出文件方向...")
    print("="*60)
    
    nifti_files = list(Path(output_base_dir).glob("*.nii.gz"))
    
    if not nifti_files:
        print("未找到NIfTI文件进行验证")
        return
    
    for file_path in nifti_files:
        try:
            img = nib.load(file_path)
            orientation = nib.aff2axcodes(img.affine)
            orientation_str = ''.join(orientation)
            print(f"  {file_path.name}: {orientation_str}")
                
        except Exception as e:
            print(f"❌ {file_path.name}: 读取失败 - {e}")
    
    print("="*60)
    print(f"共验证 {len(nifti_files)} 个文件")

def main(input_base_dir, output_base_dir, method="auto"):
    """主函数 - 保持原始DICOM方向
    
    Args:
        input_base_dir: 输入目录路径
        output_base_dir: 输出目录路径
        method: 转换方法，可选 "auto", "dcm2niix", "simpleitk"
    """
    print("DICOM to NIfTI 转换工具 (保持原始方向)")
    print("=" * 50)
    
    success = False
    
    if method == "auto":
        # 自动选择最佳可用方法
        if is_dcm2niix_available():
            print("✅ 检测到dcm2niix，使用dcm2niix进行转换...")
            success = main_dcm2niix(input_base_dir, output_base_dir)
        else:
            print("✅ 使用SimpleITK进行转换...")
            success = main_simpleitk(input_base_dir, output_base_dir)
    elif method == "dcm2niix":
        success = main_dcm2niix(input_base_dir, output_base_dir)
    elif method == "simpleitk":
        success = main_simpleitk(input_base_dir, output_base_dir)
    else:
        print(f"未知的转换方法: {method}")
        return False
    
    # 验证输出方向
    if success:
        verify_orientations(output_base_dir)
        print("\n🎉 转换完成! 所有输出文件保持原始DICOM方向")
        return True
    else:
        print(f"\n❌ 转换方法失败")
        return False

def install_requirements():
    """显示安装说明"""
    print("请安装以下依赖:")
    print("1. 必需: pip install pydicom nibabel SimpleITK tqdm")
    print("2. 可选 (dcm2niix):")
    print("   Ubuntu/Debian: sudo apt-get install dcm2niix")
    print("   macOS: brew install dcm2niix")
    print("   Windows: 从 https://github.com/rordenlab/dcm2niix/releases 下载")

if __name__ == "__main__":
    # 显示安装说明
    install_requirements()
    print("\n" + "="*50)
    
    # 设置输入输出路径
    input_base_dir = "/media/dell/T7 Shield1/nnunet/AllData/GXYF/Finished/1-8_precontrast/1-8组pre/6_组6_pre"
    output_base_dir = "/media/dell/T7 Shield1/nnunet/AllData/GXYF/Finished/1-8_precontrast/1-8组pre/6_组6_nii"
    
    # 运行主转换程序，使用自动选择方法
    success = main(input_base_dir, output_base_dir, method="auto")
    
    if success:
        print("\n✅ 转换完成!")
    else:
        print("\n❌ 转换失败或部分失败")