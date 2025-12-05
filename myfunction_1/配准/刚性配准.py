import itk
import os
import logging
import json

# 设置日志
logging.basicConfig(level=logging.INFO)

STATUS_FILE = "ST_HBP_registration_status.json"  # 用于记录处理状态的文件

def load_status():
    """加载进度状态，如果没有文件则返回空字典。"""
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_status(status):
    """保存当前进度状态到文件。"""
    with open(STATUS_FILE, 'w') as f:
        json.dump(status, f)

def register_images(fixed_image_path, moving_image_path, output_path, phase, patient):
    """
    Register the moving image to the fixed image and save the result.
    :param fixed_image_path: Path to the fixed image file
    :param moving_image_path: Path to the moving image file
    :param output_path: Directory to save the registered images
    :param phase: Phase name (N, A, D)
    :param patient: Patient ID
    """
    logging.info(f"Registering {moving_image_path} to {fixed_image_path}")

    try:
        # 读取固定图像和移动图像
        fixed_image = itk.imread(fixed_image_path, itk.F)
        moving_image = itk.imread(moving_image_path, itk.F)

        # 创建 ITKElastix 的配准对象
        elastix_object = itk.ElastixRegistrationMethod.New(fixed_image, moving_image)

        # 创建并设置参数对象
        parameter_object = itk.ParameterObject.New()
        par_map = parameter_object.GetDefaultParameterMap('rigid')
        parameter_object.AddParameterMap(par_map)

        elastix_object.SetParameterObject(parameter_object)

        # 执行配准
        elastix_object.UpdateLargestPossibleRegion()

        # 获取配准结果
        result_image = elastix_object.GetOutput()

        # 保存结果图像
        output_phase_path = os.path.join(output_path, phase)
        os.makedirs(output_phase_path, exist_ok=True)
        result_image_filename = os.path.join(output_phase_path, f'{patient}_{phase}_rigid_image.nii.gz')
        itk.imwrite(result_image, result_image_filename)

        logging.info(f"Saved registered image: {result_image_filename}")

    except Exception as e:
        logging.error(f"Error processing {patient} in phase {phase}: {str(e)}")
        raise  # 重新抛出异常以便保存状态

if __name__ == '__main__':
    # 根目录
    fixed_image = '/media/dell/data1/XTT_Registration/PKU/4587566'
    moving_image = '/media/dell/data1/XTT_Registration/PKU/4587566'
    target_root = '/media/dell/data1/XTT_Registration/PKU/Registration_image'

    status = load_status()  # 加载已处理的进度

    patients_list = os.listdir(fixed_image)

    for patient in patients_list:
        patient_path_normalized = os.path.join(fixed_image, patient)
        patient_path_original = os.path.join(moving_image, patient)

        logging.info(f"Processing patient: {patient}")

        # 固定图像路径
        fixed_image_path = os.path.join(patient_path_normalized, 'precontrast', f'{patient}_precontrast_image.nii.gz')

        # 输出目录
        output_patient_path = os.path.join(target_root, patient)
        os.makedirs(output_patient_path, exist_ok=True)

        # 移动图像路径（N, A, D期）
        for phase in ['HBP']:
            moving_image_path = os.path.join(patient_path_original, phase,
                                             f'{patient}_{phase}_image.nii.gz')

            # 检查状态：如果该患者和期相已处理，跳过
            if status.get(patient, {}).get(phase) == "completed":
                logging.info(f"Skipping {patient} phase {phase}, already completed.")
                continue

            if os.path.exists(moving_image_path):
                try:
                    register_images(fixed_image_path, moving_image_path, output_patient_path, phase, patient)
                    # 更新状态并保存
                    if patient not in status:
                        status[patient] = {}
                    status[patient][phase] = "completed"
                    save_status(status)

                except Exception as e:
                    logging.error(f"Failed to process {patient} phase {phase}.")
                    save_status(status)  # 保存当前状态
                    break  # 遇到错误时停止当前运行

            else:
                logging.warning(f"File not found: {moving_image_path}")