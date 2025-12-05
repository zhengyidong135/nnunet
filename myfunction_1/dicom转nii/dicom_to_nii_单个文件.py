import SimpleITK as sitk
import os

def convert_dicom_to_nii_with_reference(dicom_dir, reference_nii, output_path):
    # 读取DICOM序列
    reader = sitk.ImageSeriesReader()
    dicom_files = reader.GetGDCMSeriesFileNames(dicom_dir)
    reader.SetFileNames(dicom_files)
    image = reader.Execute()
    
    # 读取参考图像获取方向信息
    reference_image = sitk.ReadImage(reference_nii)
    
    # 设置相同方向
    image.SetDirection(reference_image.GetDirection())
    image.SetOrigin(reference_image.GetOrigin())
    
    # 保存为NIFTI
    sitk.WriteImage(image, output_path)
    print(f"转换完成: {output_path}")

# 使用示例
dicom_dir = "/media/dell/T7 Shield/nnunet/AllData/PKUShZh/finished/precontrast/处理异常/4587566/604_mDIXON-All_BH_w"
reference_nii = "/media/dell/T7 Shield/nnunet/AllData/PKUShZh/finished/precontrast/mask/GT_couinaud/4587566.nii.gz"
output_path = "/media/dell/T7 Shield/nnunet/AllData/PKUShZh/finished/precontrast/4587566_precontrast.nii.gz"

convert_dicom_to_nii_with_reference(dicom_dir, reference_nii, output_path)