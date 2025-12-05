import itk
import os
import logging
import pandas as pd
from scipy.spatial.distance import dice

# 设置日志
logging.basicConfig(level=logging.INFO)

# 初始化一个列表来保存患者的结果
results = []


def compute_dice(mask1, mask2):
    """
    计算两个mask之间的Dice系数
    :param mask1: 第一个mask的numpy数组
    :param mask2: 第二个mask的numpy数组
    :return: Dice系数
    """
    return 1 - dice(mask1.ravel(), mask2.ravel())


def register_images(fixed_image_path, moving_image_path, fixed_mask_path, moving_mask_path, output_path, phase,
                    patient):
    """
    Register the moving image to the fixed image and save the result, and also process the masks.
    :param fixed_image_path: Path to the fixed image file
    :param moving_image_path: Path to the moving image file
    :param fixed_mask_path: Path to the fixed mask file
    :param moving_mask_path: Path to the moving mask file
    :param output_path: Directory to save the registered images and transformed masks
    :param phase: Phase name (N, A, D)
    :param patient: Patient ID
    """
    logging.info(f"Registering {moving_image_path} to {fixed_image_path}")

    # 读取固定图像和移动图像
    fixed_image = itk.imread(fixed_image_path, itk.F)
    moving_image = itk.imread(moving_image_path, itk.F)

    # 读取固定mask和移动mask
    fixed_mask = itk.imread(fixed_mask_path, itk.F)
    moving_mask = itk.imread(moving_mask_path, itk.F)

    # 创建 ITKElastix 的配准对象
    elastix_object = itk.ElastixRegistrationMethod.New(fixed_image, moving_image)

    # 创建并设置参数对象
    parameter_object = itk.ParameterObject.New()
    par_map = parameter_object.GetDefaultParameterMap('bspline')
    parameter_object.AddParameterMap(par_map)

    elastix_object.SetParameterObject(parameter_object)

    # 执行配准
    elastix_object.UpdateLargestPossibleRegion()

    # 获取配准结果
    result_image = elastix_object.GetOutput()

    # 保存结果图像
    result_image_filename = os.path.join(output_path, f'{patient}_{phase}_Bspline_image.nii.gz')
    itk.imwrite(result_image, result_image_filename)
    logging.info(f"Saved registered image: {result_image_filename}")

    # 应用变换到mask
    logging.info(f"Applying transform to mask for {patient}, phase {phase}")

    rtp = elastix_object.GetTransformParameterObject()
    rtp.SetParameter(0, 'ResampleInterpolator', 'FinalNearestNeighborInterpolator')

    # 变换后的mask
    result_mask = itk.transformix_filter(moving_mask, rtp)

    # 定义新的存放路径
    result_liver_mask_path = os.path.join(
        f'/media/dell/data1/XTT_Registration/PKU/liver_segmentator/Bspline_liver_mask/Bspline_liver_{phase}',
        patient)

    # 确保路径存在
    os.makedirs(result_liver_mask_path, exist_ok=True)

    # 保存变换后的mask到指定目录
    result_mask_filename = os.path.join(result_liver_mask_path, f'{patient}_{phase}_liver_mask.nii.gz')
    itk.imwrite(result_mask, result_mask_filename)
    logging.info(f"Saved transformed mask: {result_mask_filename}")

    # 计算Dice系数
    logging.info("Computing Dice coefficient")
    initial_dice = compute_dice(itk.array_view_from_image(fixed_mask), itk.array_view_from_image(moving_mask))
    result_dice = compute_dice(itk.array_view_from_image(fixed_mask), itk.array_view_from_image(result_mask))

    logging.info(f"Initial Dice: {initial_dice}, Result Dice: {result_dice}")

    # 保存结果到列表
    results.append({
        'Patient ID': patient,
        'Initial Dice': initial_dice,
        'Result Dice': result_dice
    })


if __name__ == '__main__':
    # 根目录
    root_normalized = '/media/dell/data1/XTT_Registration/PKU/Image'
    root_original = '/media/dell/data1/XTT_Registration/PKU/Registration_image/Rigid_image'
    target_root = '/media/dell/data1/XTT_Registration/PKU/Registration_image/Bspline_image'

    patients_list = os.listdir(root_normalized)

    for patient in patients_list:
        patient_path_normalized = os.path.join(root_normalized, patient)
        patient_path_original = os.path.join(root_original, patient)

        logging.info(f"Processing patient: {patient}")

        # 固定图像路径
        fixed_image_path = os.path.join(patient_path_normalized, 'precontrast', f'{patient}_precontrast_image.nii.gz')

        # 固定mask路径（x期的肝脏分割mask）
        fixed_mask_path = os.path.join(
            '/media/dell/data1/XTT_Registration/PKU/liver_segmentator/precontrast_liver_groundtruth',
            patient, f'{patient}_precontrast_liver_groundtruth.nii.gz')

        # 输出目录
        output_patient_path = os.path.join(target_root, patient)
        os.makedirs(output_patient_path, exist_ok=True)

        # 移动图像路径（N, A, D期）
        for phase in ['HBP']:  # 可以改为 ['N', 'A', 'D'] 批量处理所有期相
            moving_image_path = os.path.join(patient_path_original, phase, f'{patient}_{phase}_rigid_image.nii.gz')

            # 移动mask路径（A期的肝脏分割mask）
            # moving_mask_path = os.path.join(
            #     '/media/dell/data1/HCC_Data/Multi_center_HCC/SWMUAH_HCC/1_Preprocessed_data/3_liver_segmentation/Rigid_liver_mask_A',
            #     patient, f'{patient}_{phase}_liver_Segmentator.nii.gz')

            moving_mask_path = os.path.join(
                '/media/dell/data1/XTT_Registration/PKU/liver_segmentator/Rigid_liver_mask',
                patient, f'{patient}_{phase}_liver_rigid_mask.nii.gz')

            if os.path.exists(moving_image_path) and os.path.exists(moving_mask_path):
                register_images(fixed_image_path, moving_image_path, fixed_mask_path, moving_mask_path,
                                output_patient_path, phase, patient)
            else:
                logging.warning(f"File not found: {moving_image_path} or {moving_mask_path}")

    # 将结果保存到Excel文件
    df = pd.DataFrame(results)
    output_excel = '/media/dell/data1/XTT_Registration/PKU/Registration_results_PKU_groundtruth.xlsx'
    df.to_excel(output_excel, index=False)
    logging.info(f"Results saved to {output_excel}")