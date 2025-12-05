import os
import numpy as np
import nibabel as nib
import pandas as pd
from glob import glob

def load_nifti_file(file_path):
    """加载NIfTI文件并返回数据数组"""
    img = nib.load(file_path)
    return img.get_fdata()

def calculate_dice_multiclass(pred, truth, num_classes):
    """
    计算多类别分割的Dice系数
    
    参数:
    pred: 预测分割图像
    truth: 真实分割图像  
    num_classes: 类别数量（包括背景）
    
    返回:
    dice_scores: 每个类别的Dice系数列表
    """
    dice_scores = []
    
    for class_id in range(num_classes):
        # 创建当前类别的二值掩码
        pred_binary = (pred == class_id).astype(np.int32)
        truth_binary = (truth == class_id).astype(np.int32)
        
        # 计算交集和并集
        intersection = np.sum(pred_binary * truth_binary)
        union = np.sum(pred_binary) + np.sum(truth_binary)
        
        # 避免除以零
        if union == 0:
            dice_score = np.nan
        else:
            dice_score = 2.0 * intersection / union
        
        dice_scores.append(dice_score)
    
    return dice_scores

def calculate_dice_multilabel(pred, truth, class_names=None):
    """
    计算多标签分割的Dice系数（每个类别独立计算）
    
    参数:
    pred: 预测分割图像
    truth: 真实分割图像  
    class_names: 类别名称列表，如果为None则使用数字索引
    
    返回:
    dice_dict: 包含每个类别Dice系数的字典
    """
    dice_dict = {}
    
    # 确保数据是整数类型
    pred = pred.astype(np.int32)
    truth = truth.astype(np.int32)
    
    # 获取所有存在的类别（排除背景0）
    unique_classes = np.unique(np.concatenate([pred.flatten(), truth.flatten()]))
    unique_classes = unique_classes[unique_classes != 0]  # 排除背景
    
    if len(unique_classes) == 0:
        # 如果没有非背景类别，只计算背景
        pred_binary = (pred == 0).astype(np.int32)
        truth_binary = (truth == 0).astype(np.int32)
        
        intersection = np.sum(pred_binary * truth_binary)
        union = np.sum(pred_binary) + np.sum(truth_binary)
        
        if union == 0:
            dice_score = np.nan
        else:
            dice_score = 2.0 * intersection / union
        
        dice_dict["背景"] = dice_score
        return dice_dict
    
    # 计算每个类别的Dice系数
    for class_id in unique_classes:
        # 确保class_id是整数
        class_id = int(class_id)
        
        # 创建当前类别的二值掩码
        pred_binary = (pred == class_id).astype(np.int32)
        truth_binary = (truth == class_id).astype(np.int32)
        
        # 计算交集和并集
        intersection = np.sum(pred_binary * truth_binary)
        union = np.sum(pred_binary) + np.sum(truth_binary)
        
        # 避免除以零
        if union == 0:
            dice_score = np.nan
        else:
            dice_score = 2.0 * intersection / union
        
        # 使用类别名称或数字作为键
        if class_names and class_id < len(class_names):
            class_key = class_names[class_id]
        else:
            class_key = f"类别_{class_id}"
        
        dice_dict[class_key] = dice_score
    
    return dice_dict

def main():
    # 设置路径
    pred_dir = "/media/dell/T7 Shield/nnunet/AllData/PKUShZh/finished/测试性能/HBP_precouinaud"
    label_dir = "/media/dell/T7 Shield/nnunet/AllData/NFYShZh/finshed/precontrast/precontrast_nii_mask/GT_couinaud"
    output_dir = "/media/dell/T7 Shield/nnunet/AllData/NFYShZh/finshed/precontrast/dice"
    
    # 配置参数 - 请根据你的实际数据修改这些值
    num_classes = 9  # 根据你的实际类别数量修改，包括背景
    class_names = ["背景", "肝段1", "肝段2", "肝段3", "肝段4", "肝段5", "肝段6", "肝段7","肝段8"]  # 根据你的实际类别名称修改
    
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
            
            print(f"数据形状 - 预测: {pred_data.shape}, 标签: {label_data.shape}")
            print(f"预测值范围: {np.min(pred_data)} - {np.max(pred_data)}")
            print(f"标签值范围: {np.min(label_data)} - {np.max(label_data)}")
            print(f"预测唯一值: {np.unique(pred_data)}")
            print(f"标签唯一值: {np.unique(label_data)}")
            
            # 选择计算方法：
            # 方法1: 多类别分割计算（固定类别数）
            dice_scores = calculate_dice_multiclass(pred_data, label_data, num_classes)
            
            # 创建结果记录
            result_record = {"文件名": filename}
            for i, dice_score in enumerate(dice_scores):
                if i < len(class_names):
                    class_key = class_names[i]
                else:
                    class_key = f"类别_{i}"
                result_record[class_key] = dice_score
            
            # 添加到结果列表
            results.append(result_record)
            
            # 打印结果
            print(f"处理完成: {filename}")
            for i, dice_score in enumerate(dice_scores):
                if i < len(class_names):
                    class_name = class_names[i]
                else:
                    class_name = f"类别_{i}"
                
                if np.isnan(dice_score):
                    print(f"  {class_name}: NaN")
                else:
                    print(f"  {class_name}: {dice_score:.4f}")
            
        except Exception as e:
            print(f"处理文件 {filename} 时出错: {str(e)}")
            import traceback
            traceback.print_exc()
    
    # 创建DataFrame并保存到Excel
    if results:
        df = pd.DataFrame(results)
        
        # 计算每个类别的平均Dice系数（忽略NaN值）
        dice_columns = [col for col in df.columns if col != "文件名"]
        avg_dice = {}
        
        for col in dice_columns:
            avg_dice[col] = df[col].mean(skipna=True)
        
        # 添加平均行
        avg_row = {"文件名": "平均值"}
        avg_row.update(avg_dice)
        df = pd.concat([df, pd.DataFrame([avg_row])], ignore_index=True)
        
        # 保存到Excel
        excel_path = os.path.join(output_dir, "dice_results_multiclass.xlsx")
        
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, na_rep='')
        
        print(f"结果已保存到: {excel_path}")
        print("平均Dice系数:")
        for class_name, avg_score in avg_dice.items():
            print(f"  {class_name}: {avg_score:.4f}")
        
        # 额外保存一个汇总统计文件
        summary_df = pd.DataFrame({
            '类别': list(avg_dice.keys()),
            '平均Dice': list(avg_dice.values())
        })
        summary_path = os.path.join(output_dir, "dice_summary.xlsx")
        summary_df.to_excel(summary_path, index=False)
        print(f"汇总统计已保存到: {summary_path}")
        
    else:
        print("未找到任何有效文件对进行处理")

if __name__ == "__main__":
    main()