import os
import json
from glob import glob

def generate_dataset_json(dataset_folder, dataset_name="LiverTumorSegmentation", description="Liver and tumor segmentation dataset"):
    """
    生成MSD格式的dataset.json文件
    
    参数:
    dataset_folder: 数据集根目录路径
    dataset_name: 数据集名称
    description: 数据集描述
    """
    
    # 定义路径
    images_tr_dir = os.path.join(dataset_folder, "imagesTr")
    labels_tr_dir = os.path.join(dataset_folder, "labelsTr")
    images_ts_dir = os.path.join(dataset_folder, "imagesTs")
    
    # 检查必要的目录是否存在
    if not os.path.exists(images_tr_dir):
        raise ValueError(f"imagesTr目录不存在: {images_tr_dir}")
    if not os.path.exists(labels_tr_dir):
        raise ValueError(f"labelsTr目录不存在: {labels_tr_dir}")
    
    # 获取训练集文件
    train_images = sorted(glob(os.path.join(images_tr_dir, "*.nii.gz")))
    train_labels = sorted(glob(os.path.join(labels_tr_dir, "*.nii.gz")))
    
    # 获取测试集文件（如果存在）
    test_images = []
    if os.path.exists(images_ts_dir):
        test_images = sorted(glob(os.path.join(images_ts_dir, "*.nii.gz")))
    
    # 构建训练数据列表
    training = []
    for img_path, label_path in zip(train_images, train_labels):
        # 确保文件名匹配（可选检查）
        img_name = os.path.basename(img_path)
        label_name = os.path.basename(label_path)
        
        # 这里假设图像和标签文件名相同
        # 如果需要更严格的检查，可以添加验证逻辑
        
        training.append({
            "image": f"imagesTr/{img_name}",
            "label": f"labelsTr/{label_name}"
        })
    
    # 构建测试数据列表
    test = []
    for img_path in test_images:
        img_name = os.path.basename(img_path)
        test.append({
            "image": f"imagesTs/{img_name}"
        })
    
    # 构建dataset.json内容
    dataset_json = {
        "channel_names": {
            "0": "MRI"
        },
        "labels": {
            "0": "background",
            "1": "liver"
        },
        "numTraining": len(training),
        "file_ending": ".nii.gz",
        "name": dataset_name,
        "description": description,
        "modality": {"0": "MRI"},
        "training": training,
        "test": test
    }
    
    # 保存JSON文件
    output_path = os.path.join(dataset_folder, "dataset.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(dataset_json, f, indent=4, ensure_ascii=False)
    
    print(f"dataset.json已生成并保存到: {output_path}")
    print(f"训练样本数量: {len(training)}")
    print(f"测试样本数量: {len(test)}")
    
    return dataset_json

if __name__ == "__main__":
    # 设置数据集路径
    dataset_folder = "DATASET/nnUNet_raw/Task006_example"
    
    # 生成dataset.json
    try:
        dataset_json = generate_dataset_json(dataset_folder)
        print("JSON文件生成成功！")
    except Exception as e:
        print(f"生成JSON文件时出错: {str(e)}")