import pandas as pd

def find_different_accession_patients(file1_path, file2_path):
    """
    找出相同的PatientID但AccessionNumber不同的PatientID
    """
    df1 = pd.read_excel(file1_path)
    df2 = pd.read_excel(file2_path)
    
    # 找出共同的PatientID
    common_patients = set(df1['PatientID']).intersection(set(df2['PatientID']))
    
    different_patients = []
    
    for patient_id in common_patients:
        accession1 = df1[df1['PatientID'] == patient_id]['AccessionNumber'].iloc[0]
        accession2 = df2[df2['PatientID'] == patient_id]['AccessionNumber'].iloc[0]
        
        if str(accession1) != str(accession2):
            different_patients.append(patient_id)
    
    # 输出结果
    if different_patients:
        print(f"找到 {len(different_patients)} 个PatientID相同但AccessionNumber不同的患者:")
        print("=" * 50)
        for patient_id in different_patients:
            print(patient_id)
        print("=" * 50)
        print(f"总计: {len(different_patients)} 个患者")
    else:
        print("✅ 所有共同患者的AccessionNumber都相同！")
    
    return different_patients

# 直接运行
if __name__ == "__main__":
    file1 = "/media/dell/T7 Shield/nnunet/AllData/PKUShZh/finished/precontrast/PKU_accession_number_precontrast.xlsx"
    file2 = "/media/dell/T7 Shield/nnunet/AllData/PKUShZh/finished/HBP/PKU_accession_number_HBP.xlsx"
    
    different_patients = find_different_accession_patients(file1, file2)
