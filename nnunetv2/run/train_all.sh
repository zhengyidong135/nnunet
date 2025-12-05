#!/bin/bash
# train_all.sh
# 自动顺序执行多个不同任务的训练

# 设置 PYTHONPATH 指向本地源码
export PYTHONPATH=~/下载/my_nnunet:$PYTHONPATH
# 激活 conda 环境
source ~/anaconda3/etc/profile.d/conda.sh
conda activate nnunet

# 定义任务列表
COMMANDS=(
  # "python /home/cqc/下载/Xunqi/my_nnunet/nnunetv2/run/run_training.py 001 2d 2 --c"
  
  # #  训练脾脏
  # "python /home/cqc/下载/Xunqi/my_nnunet/nnunetv2/run/run_training.py 002 2d 0 -pretrained_weights /home/cqc/下载/Xunqi/DATASET/nnUNet_results/data_spleen_02_model/nnUNetTrainer__nnUNetPlans__2d/fold_0/checkpoint_best.pth"
  # "python /home/cqc/下载/Xunqi/my_nnunet/nnunetv2/run/run_training.py 002 2d 1 -pretrained_weights /home/cqc/下载/Xunqi/DATASET/nnUNet_results/data_spleen_02_model/nnUNetTrainer__nnUNetPlans__2d/fold_1/checkpoint_best.pth"
  # "python /home/cqc/下载/Xunqi/my_nnunet/nnunetv2/run/run_training.py 002 2d 2 -pretrained_weights /home/cqc/下载/Xunqi/DATASET/nnUNet_results/data_spleen_02_model/nnUNetTrainer__nnUNetPlans__2d/fold_2/checkpoint_best.pth"
  # #  训练腰大肌
  # "python /home/cqc/下载/Xunqi/my_nnunet/nnunetv2/run/run_training.py 003 2d 0 -pretrained_weights /home/cqc/下载/Xunqi/DATASET/nnUNet_results/data_muscle_02_model/nnUNetTrainer__nnUNetPlans__2d/fold_0/checkpoint_best.pth"
  # "python /home/cqc/下载/Xunqi/my_nnunet/nnunetv2/run/run_training.py 003 2d 1 -pretrained_weights /home/cqc/下载/Xunqi/DATASET/nnUNet_results/data_muscle_02_model/nnUNetTrainer__nnUNetPlans__2d/fold_0/checkpoint_best.pth"
  # "python /home/cqc/下载/Xunqi/my_nnunet/nnunetv2/run/run_training.py 003 2d 2 -pretrained_weights /home/cqc/下载/Xunqi/DATASET/nnUNet_results/data_muscle_02_model/nnUNetTrainer__nnUNetPlans__2d/fold_1/checkpoint_best.pth"
  # "python /home/cqc/下载/Xunqi/my_nnunet/nnunetv2/run/run_training.py 003 2d 3 -pretrained_weights /home/cqc/下载/Xunqi/DATASET/nnUNet_results/data_muscle_02_model/nnUNetTrainer__nnUNetPlans__2d/fold_1/checkpoint_best.pth"

  #  训练肝段
  # "python /home/cqc/下载/Xunqi/my_nnunet/nnunetv2/run/run_training.py 004 3d_fullres 0 -pretrained_weights /home/cqc/下载/Xunqi/DATASET/nnUNet_results/data_liver_duan_01_model/nnUNetTrainer__nnUNetPlans__3d_fullres/fold_0/checkpoint_best.pth"
  # "python /home/cqc/下载/Xunqi/my_nnunet/nnunetv2/run/run_training.py 004 3d_fullres 1 -pretrained_weights /home/cqc/下载/Xunqi/DATASET/nnUNet_results/data_liver_duan_01_model/nnUNetTrainer__nnUNetPlans__3d_fullres/fold_0/checkpoint_best.pth"
  # "python /home/cqc/下载/Xunqi/my_nnunet/nnunetv2/run/run_training.py 004 3d_fullres 2 -pretrained_weights /home/cqc/下载/Xunqi/DATASET/nnUNet_results/data_liver_duan_01_model/nnUNetTrainer__nnUNetPlans__3d_fullres/fold_3/checkpoint_best.pth"
  # "python /home/cqc/下载/Xunqi/my_nnunet/nnunetv2/run/run_training.py 004 3d_fullres 3 -pretrained_weights /home/cqc/下载/Xunqi/DATASET/nnUNet_results/data_liver_duan_01_model/nnUNetTrainer__nnUNetPlans__3d_fullres/fold_3/checkpoint_best.pth"

  # 迭代SSZL的肝段
  # "python /home/dell/下载/my_nnunet/nnunetv2/run/run_training.py 004 3d_fullres 0 --c"
  # "python /home/dell/下载/my_nnunet/nnunetv2/run/run_training.py 004 3d_fullres 1 -pretrained_weights /home/dell/下载/nnunet网络之前的模型/liver_duan_001/nnUNetTrainer__nnUNetPlans__3d_fullres/fold_1/checkpoint_best.pth"
  # "python /home/dell/下载/my_nnunet/nnunetv2/run/run_training.py 004 3d_fullres 2 -pretrained_weights /home/dell/下载/nnunet网络之前的模型/liver_duan_001/nnUNetTrainer__nnUNetPlans__3d_fullres/fold_2/checkpoint_best.pth"
  # "python /home/dell/下载/my_nnunet/nnunetv2/run/run_training.py 004 3d_fullres 3 -pretrained_weights /home/dell/下载/nnunet网络之前的模型/liver_duan_001/nnUNetTrainer__nnUNetPlans__3d_fullres/fold_3/checkpoint_best.pth"

  # 数据预处理
  # "python /home/dell/下载/my_nnunet/nnunetv2/experiment_planning/plan_and_preprocess_entrypoints.py -d 002 --verify_dataset_integrity"
  # "python /home/dell/下载/my_nnunet/nnunetv2/experiment_planning/plan_and_preprocess_entrypoints.py -d 003 --verify_dataset_integrity"
  # "python /home/dell/下载/my_nnunet/nnunetv2/experiment_planning/plan_and_preprocess_entrypoints.py -d 004 --verify_dataset_integrity"

  # 训练脾脏
  # "python /home/dell/下载/my_nnunet/nnunetv2/run/run_training.py 002 2d 0 -pretrained_weights DATASET/nnUNet_results/spleen001/nnUNetTrainer__nnUNetPlans__2d/fold_0/checkpoint_best.pth"
  # "python /home/dell/下载/my_nnunet/nnunetv2/run/run_training.py 002 2d 1 -pretrained_weights DATASET/nnUNet_results/spleen001/nnUNetTrainer__nnUNetPlans__2d/fold_1/checkpoint_best.pth"
  # "python /home/dell/下载/my_nnunet/nnunetv2/run/run_training.py 002 2d 2 -pretrained_weights DATASET/nnUNet_results/spleen001/nnUNetTrainer__nnUNetPlans__2d/fold_2/checkpoint_best.pth"
  # 训练腰大肌
  # "python /home/dell/下载/my_nnunet/nnunetv2/run/run_training.py 003 2d 0 -pretrained_weights DATASET/nnUNet_results/muscle001/nnUNetTrainer__nnUNetPlans__2d/fold_0/checkpoint_best.pth"
  # "python /home/dell/下载/my_nnunet/nnunetv2/run/run_training.py 003 2d 1 -pretrained_weights DATASET/nnUNet_results/muscle001/nnUNetTrainer__nnUNetPlans__2d/fold_1/checkpoint_best.pth"
  # "python /home/dell/下载/my_nnunet/nnunetv2/run/run_training.py 003 2d 2 --c"
  # "python /home/dell/下载/my_nnunet/nnunetv2/run/run_training.py 003 2d 3 --c"
  # 训练干段
  # "python /home/dell/下载/my_nnunet/nnunetv2/run/run_training.py 004 3d_fullres 0 --c"
  # "python /home/dell/下载/my_nnunet/nnunetv2/run/run_training.py 004 3d_fullres 1 -pretrained_weights DATASET/nnUNet_results/couinaud001/nnUNetTrainer__nnUNetPlans__3d_fullres/fold_1/checkpoint_best.pth"
  # "python /home/dell/下载/my_nnunet/nnunetv2/run/run_training.py 004 3d_fullres 2 -pretrained_weights DATASET/nnUNet_results/couinaud001/nnUNetTrainer__nnUNetPlans__3d_fullres/fold_2/checkpoint_best.pth"
  # "python /home/dell/下载/my_nnunet/nnunetv2/run/run_training.py 004 3d_fullres 3 -pretrained_weights DATASET/nnUNet_results/couinaud001/nnUNetTrainer__nnUNetPlans__3d_fullres/fold_3/checkpoint_best.pth"

  # 训练肿瘤分割模型
  # "python /home/dell/下载/my_nnunet/nnunetv2/experiment_planning/plan_and_preprocess_entrypoints.py -d 006 --verify_dataset_integrity"
  # "python /home/dell/下载/my_nnunet/nnunetv2/run/run_training.py 006 2d 0 --c"
  # "python /home/dell/下载/my_nnunet/nnunetv2/run/run_training.py 006 3d_fullres 1 --c"
  # "python /home/dell/下载/my_nnunet/nnunetv2/run/run_training.py 006 3d_fullres 2 --c"
  # "python /home/dell/下载/my_nnunet/nnunetv2/run/run_training.py 006 3d_fullres 3"
  # "python /home/dell/下载/my_nnunet/nnunetv2/run/run_training.py 006 3d_fullres 4 --c"
  # "python /home/dell/下载/my_nnunet/nnunetv2/run/run_training.py 006 2d 1 --c"
  # "python /home/dell/下载/my_nnunet/nnunetv2/run/run_training.py 006 2d 2 --c"
  # "python /home/dell/下载/my_nnunet/nnunetv2/run/run_training.py 006 2d 3 --c"
  # "python /home/dell/下载/my_nnunet/nnunetv2/run/run_training.py 006 3d_fullres 1 --c"
  # "python /home/dell/下载/my_nnunet/nnunetv2/run/run_training.py 006 3d_fullres 2 --c"
  # "python /home/dell/下载/my_nnunet/nnunetv2/run/run_training.py 006 3d_fullres 3 --c"
  # "python /home/dell/下载/my_nnunet/nnunetv2/run/run_training.py 006 3d_fullres 4 --c"
  # "python /home/dell/下载/my_nnunet/nnunetv2/run/run_training.py 006 3d_fullres 0"
  # "python /home/dell/下载/my_nnunet/myfunction_1/非刚性配准.py --fixed '/media/dell/T7 Shield/nnunet/AllData/HK/dicom_to_nii_precontrast' --moving '/media/dell/T7 Shield/nnunet/AllData/HK/dicom_to_nii_gandan' --outdir '/media/dell/T7 Shield/nnunet/AllData/HK/dicom_to_nii_gandan_peizhun'"
  # 训练肿瘤
  # "python /home/dell/下载/my_nnunet/nnunetv2/run/run_training.py 006 3d_fullres 0 --c"
  # "python /home/dell/下载/my_nnunet/nnunetv2/run/run_training.py 006 3d_fullres 1 -pretrained_weights DATASET/nnUNet_results/livertumor001/nnUNetTrainer__nnUNetPlans__3d_fullres/fold_1/checkpoint_best.pth"
  # "python /home/dell/下载/my_nnunet/nnunetv2/run/run_training.py 006 3d_fullres 2 --c"
  # "python /home/dell/下载/my_nnunet/nnunetv2/run/run_training.py 006 3d_fullres 3 --c"
  # "python /home/dell/下载/my_nnunet/nnunetv2/run/run_training.py 006 3d_fullres 4 -pretrained_weights DATASET/nnUNet_results/livertumor001/nnUNetTrainer__nnUNetPlans__3d_fullres/fold_4/checkpoint_best.pth"
  # 训练肝段
  # "python /home/dell/下载/my_nnunet/nnunetv2/run/run_training.py 004 3d_fullres 0 --c"
  # "python /home/dell/下载/my_nnunet/nnunetv2/run/run_training.py 004 3d_fullres 1 -pretrained_weights DATASET/nnUNet_results/couinaud002/nnUNetTrainer__nnUNetPlans__3d_fullres/fold_1/checkpoint_best.pth"
  # "python /home/dell/下载/my_nnunet/nnunetv2/run/run_training.py 004 3d_fullres 2 --c"
#   "python /home/dell/下载/my_nnunet/nnunetv2/run/run_training.py 004 3d_fullres 3 --c"
#   "python /home/dell/下载/my_nnunet/nnunetv2/run/run_training.py 004 3d_fullres 4 -pretrained_weights DATASET/nnUNet_results/couinaud002/nnUNetTrainer__nnUNetPlans__3d_fullres/fold_0/checkpoint_best.pth"
#   # 训练脾脏
#   "python /home/dell/下载/my_nnunet/nnunetv2/run/run_training.py 002 2d 0 -pretrained_weights DATASET/nnUNet_results/spleen002/nnUNetTrainer__nnUNetPlans__2d/fold_0/checkpoint_best.pth"
#   "python /home/dell/下载/my_nnunet/nnunetv2/run/run_training.py 002 2d 1 -pretrained_weights DATASET/nnUNet_results/spleen002/nnUNetTrainer__nnUNetPlans__2d/fold_1/checkpoint_best.pth"
#   "python /home/dell/下载/my_nnunet/nnunetv2/run/run_training.py 002 2d 2 -pretrained_weights DATASET/nnUNet_results/spleen002/nnUNetTrainer__nnUNetPlans__2d/fold_2/checkpoint_best.pth"
#   "python /home/dell/下载/my_nnunet/nnunetv2/run/run_training.py 002 2d 3 -pretrained_weights DATASET/nnUNet_results/spleen002/nnUNetTrainer__nnUNetPlans__2d/fold_0/checkpoint_best.pth"
#   "python /home/dell/下载/my_nnunet/nnunetv2/run/run_training.py 002 2d 4 -pretrained_weights DATASET/nnUNet_results/spleen002/nnUNetTrainer__nnUNetPlans__2d/fold_1/checkpoint_best.pth"
#  # 训练腰大肌
#   "python /home/dell/下载/my_nnunet/nnunetv2/run/run_training.py 003 2d 0 -pretrained_weights DATASET/nnUNet_results/muscle002/nnUNetTrainer__nnUNetPlans__2d/fold_0/checkpoint_best.pth"
#   "python /home/dell/下载/my_nnunet/nnunetv2/run/run_training.py 003 2d 1 -pretrained_weights DATASET/nnUNet_results/muscle002/nnUNetTrainer__nnUNetPlans__2d/fold_1/checkpoint_best.pth"
#   "python /home/dell/下载/my_nnunet/nnunetv2/run/run_training.py 003 2d 2 -pretrained_weights DATASET/nnUNet_results/muscle002/nnUNetTrainer__nnUNetPlans__2d/fold_2/checkpoint_best.pth"
#   "python /home/dell/下载/my_nnunet/nnunetv2/run/run_training.py 003 2d 3 -pretrained_weights DATASET/nnUNet_results/muscle002/nnUNetTrainer__nnUNetPlans__2d/fold_3/checkpoint_best.pth"
#   "python /home/dell/下载/my_nnunet/nnunetv2/run/run_training.py 003 2d 4 -pretrained_weights DATASET/nnUNet_results/muscle002/nnUNetTrainer__nnUNetPlans__2d/fold_0/checkpoint_best.pth"

  # 训练肝脏肿瘤
  # "python /home/dell/下载/my_nnunet/nnunetv2/run/run_training.py 006 3d_fullres 0 -pretrained_weights DATASET/nnUNet_results/livertumor002/nnUNetTrainer__nnUNetPlans__3d_fullres/fold_0/checkpoint_best.pth"
  # "python /home/dell/下载/my_nnunet/nnunetv2/run/run_training.py 006 3d_fullres 1 -pretrained_weights DATASET/nnUNet_results/livertumor002/nnUNetTrainer__nnUNetPlans__3d_fullres/fold_1/checkpoint_best.pth"
  # "python /home/dell/下载/my_nnunet/nnunetv2/run/run_training.py 006 3d_fullres 2 -pretrained_weights DATASET/nnUNet_results/livertumor002/nnUNetTrainer__nnUNetPlans__3d_fullres/fold_2/checkpoint_best.pth"
  # "python /home/dell/下载/my_nnunet/nnunetv2/run/run_training.py 006 3d_fullres 3 -pretrained_weights DATASET/nnUNet_results/livertumor002/nnUNetTrainer__nnUNetPlans__3d_fullres/fold_3/checkpoint_best.pth"
  # "python /home/dell/下载/my_nnunet/nnunetv2/run/run_training.py 006 3d_fullres 4 -pretrained_weights DATASET/nnUNet_results/livertumor002/nnUNetTrainer__nnUNetPlans__3d_fullres/fold_4/checkpoint_best.pth"
  # "python /home/dell/下载/my_nnunet/myfunction_1/非刚性配准_ST.py --fixed '/media/dell/T7 Shield/nnunet/AllData/PKUShZh/dicom_to_nii' --moving '/media/dell/T7 Shield/nnunet/AllData/PKUShZh/肝胆特异期nii' --outdir '/media/dell/T7 Shield/nnunet/AllData/PKUShZh/肝胆特异期nii_peizhun' "
  # "python /home/dell/下载/my_nnunet/myfunction_1/非刚性配准_ST.py --fixed '/media/dell/T7 Shield/nnunet/AllData/ST/pre_nii' --moving '/media/dell/T7 Shield/nnunet/AllData/ST/ST肝胆特异_nii' --outdir '/media/dell/T7 Shield/nnunet/AllData/ST/ST肝胆特异_nii_peizhun' "
  # "python /home/dell/下载/my_nnunet/myfunction_1/非刚性配准_ST.py --fixed '/media/dell/T7 Shield/nnunet/AllData/HK/precontrast_mask_nii/dicom_to_nii_precontrast' --moving '/media/dell/T7 Shield/nnunet/AllData/HK/dicom_to_nii_gandan' --outdir '/media/dell/T7 Shield/nnunet/AllData/HK/dicom_to_nii_gandan_peizhun_new' "
  # 迭代肝脏肿瘤
  # "python /home/dell/下载/my_nnunet/nnunetv2/run/run_training.py 006 3d_fullres 0 -pretrained_weights DATASET/nnUNet_results/livertumor/nnUNetTrainer__nnUNetPlans__3d_fullres/fold_0/checkpoint_best.pth"
  # "python /home/dell/下载/my_nnunet/nnunetv2/run/run_training.py 006 3d_fullres 1 -pretrained_weights DATASET/nnUNet_results/livertumor/nnUNetTrainer__nnUNetPlans__3d_fullres/fold_1/checkpoint_best.pth"
  # "python /home/dell/下载/my_nnunet/nnunetv2/run/run_training.py 006 3d_fullres 2 -pretrained_weights DATASET/nnUNet_results/livertumor/nnUNetTrainer__nnUNetPlans__3d_fullres/fold_2/checkpoint_best.pth"
  # "python /home/dell/下载/my_nnunet/nnunetv2/run/run_training.py 006 3d_fullres 3 --c"
  # "python /home/dell/下载/my_nnunet/nnunetv2/run/run_training.py 006 3d_fullres 4 -pretrained_weights DATASET/nnUNet_results/livertumor/nnUNetTrainer__nnUNetPlans__3d_fullres/fold_4/checkpoint_best.pth"
  # 迭代脾脏（HBP）
  # "python /home/dell/下载/my_nnunet/nnunetv2/run/run_training.py 002 2d 0 -pretrained_weights DATASET/nnUNet_results/spleen001_precontrast/nnUNetTrainer__nnUNetPlans__2d/fold_0/checkpoint_best.pth"
  # "python /home/dell/下载/my_nnunet/nnunetv2/run/run_training.py 002 2d 1 -pretrained_weights DATASET/nnUNet_results/spleen001_precontrast/nnUNetTrainer__nnUNetPlans__2d/fold_1/checkpoint_best.pth"
  # "python /home/dell/下载/my_nnunet/nnunetv2/run/run_training.py 002 2d 2 -pretrained_weights DATASET/nnUNet_results/spleen001_precontrast/nnUNetTrainer__nnUNetPlans__2d/fold_2/checkpoint_best.pth"
  # "python /home/dell/下载/my_nnunet/nnunetv2/run/run_training.py 002 2d 3 -pretrained_weights DATASET/nnUNet_results/spleen001_precontrast/nnUNetTrainer__nnUNetPlans__2d/fold_3/checkpoint_best.pth"
  # "python /home/dell/下载/my_nnunet/nnunetv2/run/run_training.py 002 2d 4 -pretrained_weights DATASET/nnUNet_results/spleen001_precontrast/nnUNetTrainer__nnUNetPlans__2d/fold_4/checkpoint_best.pth"
  # 迭代腰大肌（HBP）
  # "python /home/dell/下载/my_nnunet/nnunetv2/run/run_training.py 003 2d 0 --c"
  # "python /home/dell/下载/my_nnunet/nnunetv2/run/run_training.py 003 2d 1 -pretrained_weights DATASET/nnUNet_results/muscle001_precontrast/nnUNetTrainer__nnUNetPlans__2d/fold_1/checkpoint_best.pth"
  # "python /home/dell/下载/my_nnunet/nnunetv2/run/run_training.py 003 2d 2 -pretrained_weights DATASET/nnUNet_results/muscle001_precontrast/nnUNetTrainer__nnUNetPlans__2d/fold_2/checkpoint_best.pth"
  # "python /home/dell/下载/my_nnunet/nnunetv2/run/run_training.py 003 2d 3 -pretrained_weights DATASET/nnUNet_results/muscle001_precontrast/nnUNetTrainer__nnUNetPlans__2d/fold_3/checkpoint_best.pth"
  # "python /home/dell/下载/my_nnunet/nnunetv2/run/run_training.py 003 2d 4 -pretrained_weights DATASET/nnUNet_results/muscle001_precontrast/nnUNetTrainer__nnUNetPlans__2d/fold_4/checkpoint_best.pth"
  # # 迭代肝脏肿瘤（HBP）
  # "python /home/dell/下载/my_nnunet/nnunetv2/run/run_training.py 006 3d_fullres 0 -pretrained_weights DATASET/nnUNet_results/livertumor003_precontrast/nnUNetTrainer__nnUNetPlans__3d_fullres/fold_0/checkpoint_best.pth"
  # "python /home/dell/下载/my_nnunet/nnunetv2/run/run_training.py 006 3d_fullres 1 -pretrained_weights DATASET/nnUNet_results/livertumor003_precontrast/nnUNetTrainer__nnUNetPlans__3d_fullres/fold_1/checkpoint_best.pth"
  # "python /home/dell/下载/my_nnunet/nnunetv2/run/run_training.py 006 3d_fullres 2 -pretrained_weights DATASET/nnUNet_results/livertumor003_precontrast/nnUNetTrainer__nnUNetPlans__3d_fullres/fold_2/checkpoint_best.pth"
  # "python /home/dell/下载/my_nnunet/nnunetv2/run/run_training.py 006 3d_fullres 3 -pretrained_weights DATASET/nnUNet_results/livertumor003_precontrast/nnUNetTrainer__nnUNetPlans__3d_fullres/fold_3/checkpoint_best.pth"
  # "python /home/dell/下载/my_nnunet/nnunetv2/run/run_training.py 006 3d_fullres 4 -pretrained_weights DATASET/nnUNet_results/livertumor003_precontrast/nnUNetTrainer__nnUNetPlans__3d_fullres/fold_4/checkpoint_best.pth"
  # "python /home/dell/下载/my_nnunet/nnunetv2/experiment_planning/plan_and_preprocess_entrypoints.py -d 005 "
  # "python /home/dell/下载/my_nnunet/nnunetv2/experiment_planning/plan_and_preprocess_entrypoints.py -d 007 "

  # 训练门脉
  # # "python /home/dell/下载/my_nnunet/nnunetv2/run/run_training.py 005 2d 0 --c"
  # "python /home/dell/下载/my_nnunet/nnunetv2/run/run_training.py 005 2d 1"
  # "python /home/dell/下载/my_nnunet/nnunetv2/run/run_training.py 005 2d 2"
  # "python /home/dell/下载/my_nnunet/nnunetv2/run/run_training.py 005 2d 3"
  # "python /home/dell/下载/my_nnunet/nnunetv2/run/run_training.py 005 2d 4"
  # # 训练肝静脉
  # "python /home/dell/下载/my_nnunet/nnunetv2/run/run_training.py 007 2d 1"
  # "python /home/dell/下载/my_nnunet/nnunetv2/run/run_training.py 007 2d 2"
  # "python /home/dell/下载/my_nnunet/nnunetv2/run/run_training.py 007 2d 3"
  # "python /home/dell/下载/my_nnunet/nnunetv2/run/run_training.py 007 2d 4"
  # "python /home/dell/下载/my_nnunet/nnunetv2/run/run_training.py 007 2d 0"
  # 迭代肝段（HBP）
  # "python /home/dell/下载/my_nnunet/nnunetv2/run/run_training.py 004 3d_fullres 0 --c "
  # "python /home/dell/下载/my_nnunet/nnunetv2/run/run_training.py 004 3d_fullres 1 -pretrained_weights '/media/dell/T7 Shield/模型的更迭/HBP/2025-12-01/couinaud_HBP_001/nnUNetTrainer__nnUNetPlans__3d_fullres/fold_1/checkpoint_best.pth'"
  # "python /home/dell/下载/my_nnunet/nnunetv2/run/run_training.py 004 3d_fullres 2 --c"
  # "python /home/dell/下载/my_nnunet/nnunetv2/run/run_training.py 004 3d_fullres 3 --c"
  "python /home/dell/下载/my_nnunet/nnunetv2/run/run_training.py 004 3d_fullres 4 --c"
  





)

# 顺序执行
for CMD in "${COMMANDS[@]}"; do
  echo "====== 开始执行: $CMD ======"
  eval $CMD
  echo "====== 任务完成: $CMD ======"
done
