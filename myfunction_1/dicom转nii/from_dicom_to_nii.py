#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
DICOM序列转换脚本（三级目录版）
结构：一级文件夹/二级子文件夹/三级子文件夹（包含.DCM文件）
输出：以一级文件夹命名的.nii.gz文件
"""

import os
import SimpleITK as sitk
from tqdm import tqdm
import multiprocessing

def convert_single_series(dicom_dir, output_path):
    """转换单个DICOM序列"""
    try:
        # 严格匹配.DCM文件并按数字排序
        dcm_files = sorted([f for f in os.listdir(dicom_dir) if f.endswith('.dcm')],
                          key=lambda x: int(x.split('.')[0]) if x.split('.')[0].isdigit() else x)
        
        if not dcm_files:
            return False, f"No .DCM files in {dicom_dir}"
        
        # 构建完整文件路径
        dicom_paths = [os.path.join(dicom_dir, f) for f in dcm_files]
        
        # 读取DICOM序列
        reader = sitk.ImageSeriesReader()
        reader.SetFileNames(dicom_paths)
        image = reader.Execute()
        
        # 保存为NIfTI
        sitk.WriteImage(image, output_path)
        return True, output_path
    except Exception as e:
        return False, f"Error in {dicom_dir}: {str(e)}"

def find_dicom_dirs(base_path):
    """递归查找包含.DCM的三级子目录"""
    dicom_dirs = []
    for root, dirs, files in os.walk(base_path):
        # 只处理三级子目录（即 depth=2）
        if root[len(base_path):].count(os.sep) == 1:
            if any(f.endswith('.dcm') for f in files):
                dicom_dirs.append(root)
    return dicom_dirs

def batch_convert(base_path, output_dir):
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 查找所有包含.DCM的三级子目录
    dicom_dirs = find_dicom_dirs(base_path)
    
    if not dicom_dirs:
        print(f"\n❌ 错误: 在 {base_path} 下未找到任何包含.DCM文件的三级子文件夹")
        print("请确认目录结构为：一级文件夹/二级子文件夹/三级子文件夹/*.DCM")
        return
    
    # 构建任务列表（一级文件夹名 -> DICOM目录）
    tasks = []
    for dicom_dir in dicom_dirs:
        # 获取一级文件夹名称
        first_level = dicom_dir.split(os.sep)[-3]
        output_path = os.path.join(output_dir, f"{first_level}.nii.gz")
        tasks.append((dicom_dir, output_path))
        print(f"Found DICOM series: {dicom_dir} -> {output_path}")

    # 多进程处理
    success_count = 0
    with multiprocessing.Pool(processes=min(4, multiprocessing.cpu_count())) as pool:
        results = []
        for task in tasks:
            results.append(pool.apply_async(convert_single_series, task))
        
        # 进度条
        pbar = tqdm(total=len(tasks), desc="Converting", unit="series")
        for res in results:
            success, msg = res.get()
            if success:
                success_count += 1
                pbar.write(f"✅ {msg}")
            else:
                pbar.write(f"⚠️ {msg}")
            pbar.update(1)
        pbar.close()
    
    print(f"\n🎉 转换完成! 成功: {success_count}/{len(tasks)}")
    print(f"输出目录: {output_dir}")

if __name__ == "__main__":
    # 配置路径
    BASE_PATH = "/media/dell/T7 Shield/nnunet/AllData/PKUShZh/重新配置"
    OUTPUT_DIR = "/media/dell/T7 Shield/nnunet/AllData/PKUShZh/重新配置"
    
    if not os.path.exists(BASE_PATH):
        print(f"错误: 路径不存在 {BASE_PATH}")
        exit(1)
    
    print("="*60)
    print(f"扫描目录: {BASE_PATH}")
    print(f"输出目录: {OUTPUT_DIR}")
    print("目录结构要求: 一级文件夹/二级子文件夹/三级子文件夹/*.DCM")
    print("="*60)
    
    batch_convert(BASE_PATH, OUTPUT_DIR)