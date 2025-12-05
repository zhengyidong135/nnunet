import os
import numpy as np
import nibabel as nib
from tqdm import tqdm
def merge_couinaud_to_liver(input_dir, output_dir):
    """
    将多标签Couinaud肝段分割合并为单个肝脏标签
    
    参数:
        input_dir: 输入目录路径，包含多标签nii.gz文件
        output_dir: 输出目录路径，将保存合并后的单标签文件
    """
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 获取所有nii.gz文件
    nii_files = [f for f in os.listdir(input_dir) if f.endswith('.nii.gz')]
    
    print(f"找到 {len(nii_files)} 个文件需要处理")
    
    for filename in tqdm(nii_files, desc="处理文件中"):
        # 构建完整文件路径
        input_path = os.path.join(input_dir, filename)
        output_path = os.path.join(output_dir, filename)
        
        try:
            # 加载NIfTI文件
            img = nib.load(input_path)
            data = img.get_fdata()
            affine = img.affine
            header = img.header
            
            # 将所有的肝段标签(1-8)合并为肝脏标签(1)
            # 背景保持为0，所有非零值变为1
            liver_mask = (data > 0).astype(np.uint8)
            
            # 创建新的NIfTI图像
            new_img = nib.Nifti1Image(liver_mask, affine, header=header)
            
            # 保存文件
            nib.save(new_img, output_path)
            
        except Exception as e:
            print(f"处理文件 {filename} 时出错: {str(e)}")
    
    print(f"处理完成！所有文件已保存到: {output_dir}")

if __name__ == "__main__":
    # 输入和输出路径
    input_directory = "/media/dell/T7 Shield/nnunet/AllData/PKUShZh/finished/HBP/mask/GT_couinaud"
    output_directory = "/media/dell/T7 Shield/nnunet/AllData/PKUShZh/finished/HBP/mask/GT_liver"
    
    # 执行合并操作
    merge_couinaud_to_liver(input_directory, output_directory)
# /media/dell/T7 Shield/nnunet/AllData/HK/finished/precontrast/precontrast_dicom
# /media/dell/T7 Shield/nnunet/AllData/HK/finished/HBP/HBP_dicom