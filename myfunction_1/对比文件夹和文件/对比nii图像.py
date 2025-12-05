import nibabel as nib
import numpy as np
import os
from pathlib import Path

def compare_nifti_images(img1_path, img2_path):
    """对比两个NIfTI图像的详细信息"""
    
    def get_image_orientation(affine):
        """从仿射矩阵获取图像方向"""
        orient = ''
        for i in range(3):
            if np.argmax(np.abs(affine[:3, i])) == 0:
                orient += 'R' if affine[0, i] > 0 else 'L'
            elif np.argmax(np.abs(affine[:3, i])) == 1:
                orient += 'A' if affine[1, i] > 0 else 'P'
            else:
                orient += 'S' if affine[2, i] > 0 else 'I'
        return orient
    
    def get_detailed_info(img_path, label):
        """获取图像的详细信息"""
        img = nib.load(img_path)
        data = img.get_fdata()
        header = img.header
        affine = img.affine
        
        info = {
            'label': label,
            'path': img_path,
            'shape': img.shape,
            'ndim': img.ndim,
            'dtype': data.dtype,
            'data_range': (float(data.min()), float(data.max())),
            'mean': float(data.mean()),
            'std': float(data.std()),
            'non_zero_voxels': int(np.count_nonzero(data)),
            'voxel_size': header.get_zooms()[:3],
            'orientation': get_image_orientation(affine),
            'affine': affine,
            'data_type': header['datatype'],
            'bitpix': int(header['bitpix']),
            'scl_slope': float(header['scl_slope']),
            'scl_inter': float(header['scl_inter']),
            'file_size_mb': os.path.getsize(img_path) / (1024 * 1024)
        }
        return info, img
    
    print("=" * 80)
    print("🔄 NIfTI 图像详细对比分析")
    print("=" * 80)
    
    # 获取两个图像的信息
    info1, img1 = get_detailed_info(img1_path, "图像1 (precontrast)")
    info2, img2 = get_detailed_info(img2_path, "图像2 (HBP)")
    
    # 打印基本信息对比
    print("\n📊 基本信息对比:")
    print("-" * 50)
    for key in ['shape', 'ndim', 'dtype', 'orientation', 'voxel_size']:
        val1 = info1[key]
        val2 = info2[key]
        status = "✅ 相同" if val1 == val2 else "❌ 不同"
        print(f"   {key:>15}: {str(val1):<20} | {str(val2):<20} {status}")
    
    # 打印数据统计对比
    print("\n📈 数据统计对比:")
    print("-" * 50)
    stats_keys = ['data_range', 'mean', 'std', 'non_zero_voxels']
    for key in stats_keys:
        val1 = info1[key]
        val2 = info2[key]
        if key == 'data_range':
            diff = f"范围差: [{val2[0]-val1[0]:.1f}, {val2[1]-val1[1]:.1f}]"
        else:
            diff = f"差异: {val2 - val1:.1f}"
        print(f"   {key:>15}: {val1} | {val2} ({diff})")
    
    # 打印文件信息
    print("\n📁 文件信息:")
    print("-" * 50)
    print(f"   文件大小: {info1['file_size_mb']:.1f} MB | {info2['file_size_mb']:.1f} MB")
    print(f"   数据格式: {info1['data_type']} | {info2['data_type']}")
    print(f"   位深度: {info1['bitpix']} | {info2['bitpix']}")
    
    # 配准兼容性分析
    print("\n🎯 配准兼容性分析:")
    print("-" * 50)
    
    issues = []
    warnings = []
    
    # 检查关键匹配项
    if info1['shape'] != info2['shape']:
        issues.append(f"形状不匹配: {info1['shape']} vs {info2['shape']}")
    
    if info1['orientation'] != info2['orientation']:
        issues.append(f"方向不匹配: {info1['orientation']} vs {info2['orientation']}")
    
    if info1['voxel_size'] != info2['voxel_size']:
        warnings.append(f"体素尺寸不同: {info1['voxel_size']} vs {info2['voxel_size']}")
    
    # 数据范围差异过大
    range1 = info1['data_range'][1] - info1['data_range'][0]
    range2 = info2['data_range'][1] - info2['data_range'][0]
    if abs(range1 - range2) > max(range1, range2) * 0.5:
        warnings.append("数据范围差异较大，可能影响配准")
    
    # 输出问题和建议
    if issues:
        print("❌ 严重问题 (需要处理):")
        for issue in issues:
            print(f"   - {issue}")
    else:
        print("✅ 无严重兼容性问题")
    
    if warnings:
        print("⚠️ 警告信息:")
        for warning in warnings:
            print(f"   - {warning}")
    
    # 配准建议
    print("\n💡 配准建议:")
    if issues:
        print("   1. 必须进行重采样和方向调整")
        print("   2. 建议使用保守的配准参数")
        print("   3. 密切监控配准过程中的形变场")
    else:
        print("   1. 可以直接进行配准")
        print("   2. 可以使用标准配准参数")
    
    return info1, info2

# 使用示例
if __name__ == "__main__":
    img1_path = "/media/dell/T7 Shield/nnunet/AllData/HK/finished/precontrast/dicom_to_nii/AD5737817.nii.gz"
    img2_path = "/media/dell/T7 Shield/nnunet/AllData/HK/finished/HBP/dicom_to_nii_gandan/AD5737817.nii.gz"
    
    # 检查文件是否存在
    if not os.path.exists(img1_path):
        print(f"❌ 文件不存在: {img1_path}")
    elif not os.path.exists(img2_path):
        print(f"❌ 文件不存在: {img2_path}")
    else:
        info1, info2 = compare_nifti_images(img1_path, img2_path)