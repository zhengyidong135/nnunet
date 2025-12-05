#!/usr/bin/env python3
import nibabel as nib
import os
import sys

def copy_geometry(source_file, target_file, output_file):
    """直接复制目标文件的几何信息到源文件"""
    print(f"处理: {os.path.basename(source_file)}")
    
    # 加载图像
    source_img = nib.load(source_file)
    target_img = nib.load(target_file)
    
    # 创建新图像：源数据 + 目标几何
    new_img = nib.Nifti1Image(
        source_img.get_fdata(), 
        target_img.affine, 
        header=target_img.header
    )
    
    # 保存
    nib.save(new_img, output_file)
    print(f"保存到: {output_file}")

# 使用示例
if __name__ == "__main__":
    hbp_dir = "/media/dell/T7 Shield/nnunet/AllData/HK/finished/HBP/dicom_to_nii_gandan"
    precontrast_dir = "/media/dell/T7 Shield/nnunet/AllData/HK/finished/precontrast/dicom_to_nii"
    output_dir = "./reoriented_output"
    
    os.makedirs(output_dir, exist_ok=True)
    
    for filename in os.listdir(hbp_dir):
        if filename.endswith('.nii.gz') and os.path.exists(os.path.join(precontrast_dir, filename)):
            copy_geometry(
                os.path.join(hbp_dir, filename),
                os.path.join(precontrast_dir, filename),
                os.path.join(output_dir, filename)
            )
