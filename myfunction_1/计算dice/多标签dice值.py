import os
import numpy as np
import nibabel as nib
import pandas as pd
from glob import glob

def load_nifti_file(file_path):
    """加载NIfTI文件并返回数据数组"""
    img = nib.load(file_path)
    return img.get_fdata()

def calculate_dice_multilabel(pred, truth, num_classes):
    """
    计算多标签Dice系数
    
    参数:
    - pred: 预测数据数组
    - truth: 真实标签数据数组
    - num_classes: 类别数量（包括背景类0）
    
    返回:
    - dice_scores: 每个类别的Dice系数列表
    """
    dice_scores = []
    
    for class_id in range(num_classes):
        # 创建当前类别的二值掩码
        pred_binary = (pred == class_id).astype(np.int32)
        truth_binary = (truth == class_id).astype(np.int32)
        
        # 计算交集和并集
        intersection = np.sum(pred_binary * truth_binary)
        union = np.sum(pred_binary) + np.sum(truth_binary)
        
        # 避免除以零，返回NaN
        if union == 0:
            dice_score = np.nan
        else:
            dice_score = 2.0 * intersection / union
        
        dice_scores.append(dice_score)
    
    return dice_scores

def calculate_dice_multilabel_exclude_background(pred, truth, num_classes):
    """
    计算多标签Dice系数（排除背景类0）
    
    参数:
    - pred: 预测数据数组
    - truth: 真实标签数据数组
    - num_classes: 类别数量（包括背景类0）
    
    返回:
    - dice_scores: 每个类别（排除背景）的Dice系数列表
    """
    dice_scores = []
    
    for class_id in range(1, num_classes):  # 从1开始，跳过背景类0
        # 创建当前类别的二值掩码
        pred_binary = (pred == class_id).astype(np.int32)
        truth_binary = (truth == class_id).astype(np.int32)
        
        # 计算交集和并集
        intersection = np.sum(pred_binary * truth_binary)
        union = np.sum(pred_binary) + np.sum(truth_binary)
        
        # 避免除以零，返回NaN
        if union == 0:
            dice_score = np.nan
        else:
            dice_score = 2.0 * intersection / union
        
        dice_scores.append(dice_score)
    
    return dice_scores
def main():
    # 设置路径
    pred_dir = "/media/dell/T7 Shield/nnunet/AllData/HK/mask/HKSZ_38/Couinaud_predicted"
    label_dir = "/media/dell/T7 Shield/nnunet/AllData/HK/mask/Couinaud_modified_HKSZ38"
    output_dir = "/media/dell/T7 Shield/nnunet/AllData/HK/HK_dice值"
    
    # 设置类别数量（根据你的数据调整这个值）
    # 例如：如果标签包含0-8，那么num_classes=9（0-8共9个类别）
    num_classes = 8  # 请根据你的实际类别数量修改
    
    # 是否排除背景类（类别0）
    exclude_background = True  # 如果设置为False，则包含所有类别
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 获取所有预测文件
    pred_files = sorted(glob(os.path.join(pred_dir, "*.nii.gz")))
    # 存储结果
    results = []
    
    # 遍历每个预测文件
    for pred_file in pred_files:
        # 获取文件名
        filename = os.path.basename(pred_file)
        
        # 构建对应的标签文件路径
        label_file = os.path.join(label_dir, filename)
        
        # 检查标签文件是否存在
        if not os.path.exists(label_file):
            print(f"警告: 找不到对应的标签文件 {label_file}")
            continue
        
        try:
            # 加载预测和标签数据
            pred_data = load_nifti_file(pred_file)
            label_data = load_nifti_file(label_file)
            
            # 计算多标签Dice系数
            if exclude_background:
                dice_scores = calculate_dice_multilabel_exclude_background(pred_data, label_data, num_classes)
                class_range = range(1, num_classes)
            else:
                dice_scores = calculate_dice_multilabel(pred_data, label_data, num_classes)
                class_range = range(num_classes)
            
            # 创建结果字典
            result = {"文件名": filename}
            
            # 添加每个类别的Dice系数
            for i, class_id in enumerate(class_range):
                result[f"类别{class_id}_Dice"] = dice_scores[i]
            
            # 计算平均Dice系数（忽略NaN值）
            valid_scores = [score for score in dice_scores if not np.isnan(score)]
            if valid_scores:
                result["平均Dice"] = np.mean(valid_scores)
            else:
                result["平均Dice"] = np.nan
            
            # 添加到结果列表
            results.append(result)
            
            # 打印结果
            print(f"处理完成: {filename}")
            for i, class_id in enumerate(class_range):
                score = dice_scores[i]
                if np.isnan(score):
                    print(f"  类别 {class_id}: NaN")
                else:
                    print(f"  类别 {class_id}: {score:.4f}")
            print(f"  平均Dice: {result['平均Dice']:.4f}")
            
        except Exception as e:
            print(f"处理文件 {filename} 时出错: {str(e)}")
    
    # 创建DataFrame并保存到Excel
    if results:
        df = pd.DataFrame(results)
        
        # 计算每列的平均值（忽略NaN值）
        avg_values = {}
        for col in df.columns:
            if col != "文件名":  # 跳过文件名列
                avg_values[col] = df[col].mean(skipna=True)
        
        # 添加平均行
        avg_row = {"文件名": "平均值"}
        avg_row.update(avg_values)
        avg_df = pd.DataFrame([avg_row])
        df = pd.concat([df, avg_df], ignore_index=True)
        
        excel_path = os.path.join(output_dir, "dice_results_multilabel.xlsx")
        
        # 保存到Excel，不显示NaN值
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, na_rep='')
        
        print(f"结果已保存到: {excel_path}")
        
        # 打印总体平均Dice系数
        if "平均Dice" in avg_values:
            print(f"总体平均Dice系数: {avg_values['平均Dice']:.4f} (已忽略NaN值)")
        
        # 打印每个类别的平均Dice系数
        print("各类别平均Dice系数:")
        for col, avg in avg_values.items():
            if col.startswith("类别") and col.endswith("_Dice"):
                print(f"  {col}: {avg:.4f}")
                
    else:
        print("未找到任何有效文件对进行处理")

if __name__ == "__main__":
    main()