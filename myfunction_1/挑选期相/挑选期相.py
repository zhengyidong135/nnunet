import os
import shutil
from pathlib import Path
import pandas as pd
from datetime import datetime

def copy_first_matching_folder_with_excel():
    """
    复制每个一级子文件夹下的第一个匹配的二级子文件夹，并将无匹配的保存到Excel
    """
    source_dir = "/media/dell/T7 Shield/nnunet/数据中心/北大深圳/命名规范化"
    target_dir = "/media/dell/T7 Shield/nnunet/数据中心/北大深圳/precontrast"
    excel_output = "/media/dell/T7 Shield/nnunet/数据中心/北大深圳/无匹配文件夹统计.xlsx"
    
    keywords = [
        "t1_vibe_fs_tra_p2_bh",
        "t1_vibe_fs_tra_p2_dynamic_1+3", 
        "t1_vibe_dixon_tra_p4_dynamic_1+3_W"
    ]
    
    source_path = Path(source_dir)
    target_path = Path(target_dir)
    
    if not source_path.exists():
        print(f"错误：源目录不存在 {source_dir}")
        return
    
    target_path.mkdir(parents=True, exist_ok=True)
    
    copied_count = 0
    skipped_count = 0
    no_match_folders = []  # 存储无匹配的一级文件夹信息
    
    # 遍历所有一级子文件夹
    for first_level in source_path.iterdir():
        if first_level.is_dir():
            print(f"处理一级文件夹: {first_level.name}")
            
            found_match = False
            match_info = None
            
            # 遍历当前一级文件夹下的所有二级子文件夹
            for second_level in first_level.iterdir():
                if second_level.is_dir() and not found_match:
                    folder_name = second_level.name.lower()
                    
                    # 检查是否包含任一关键词
                    if any(keyword.lower() in folder_name for keyword in keywords):
                        print(f"  找到匹配的二级文件夹: {second_level.name}")
                        
                        # 构建目标路径：目标目录/一级文件夹名/二级文件夹名
                        target_folder = target_path / first_level.name / second_level.name
                        
                        # 如果目标不存在，则复制
                        if not target_folder.exists():
                            shutil.copytree(second_level, target_folder)
                            print(f"    复制成功: {second_level.name}")
                            copied_count += 1
                        else:
                            print(f"    跳过（已存在）: {second_level.name}")
                            skipped_count += 1
                        
                        # 记录匹配信息
                        match_info = {
                            '一级文件夹': first_level.name,
                            '匹配的二级文件夹': second_level.name,
                            '匹配的关键词': next((k for k in keywords if k.lower() in folder_name), '未知')
                        }
                        found_match = True
            
            if not found_match:
                print(f"  未找到匹配的二级文件夹")
                # 记录无匹配的文件夹信息
                no_match_folders.append({
                    '一级文件夹名称': first_level.name,
                    '一级文件夹路径': str(first_level),
                    '二级文件夹列表': [f.name for f in first_level.iterdir() if f.is_dir()],
                    '无匹配原因': '未找到包含关键词的二级文件夹',
                    '检查时间': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })
    
    # 保存无匹配的文件夹信息到Excel
    if no_match_folders:
        df = pd.DataFrame(no_match_folders)
        
        # 展开二级文件夹列表为字符串，便于查看
        df['二级文件夹列表'] = df['二级文件夹列表'].apply(lambda x: ', '.join(x) if x else '无二级文件夹')
        
        try:
            df.to_excel(excel_output, index=False, engine='openpyxl')
            print(f"\n已将 {len(no_match_folders)} 个无匹配的一级文件夹信息保存到: {excel_output}")
        except Exception as e:
            print(f"保存Excel文件时出错: {e}")
            # 尝试保存为CSV格式
            csv_output = excel_output.replace('.xlsx', '.csv')
            df.to_csv(csv_output, index=False, encoding='utf-8-sig')
            print(f"已保存为CSV格式: {csv_output}")
    else:
        print("\n所有一级文件夹都有匹配的二级文件夹")
    
    print(f"\n操作完成！")
    print(f"复制成功: {copied_count} 个文件夹")
    print(f"跳过已存在: {skipped_count} 个文件夹")
    print(f"无匹配的一级文件夹: {len(no_match_folders)} 个")

def preview_with_excel_export():
    """
    预览并导出无匹配的文件夹信息到Excel
    """
    source_dir = "/media/dell/T7 Shield/nnunet/数据中心/北大深圳/命名规范化"
    excel_output = "/media/dell/T7 Shield/nnunet/数据中心/北大深圳/无匹配文件夹预览.xlsx"
    
    keywords = [
        "t1_vibe_fs_tra_p2_bh",
        "t1_vibe_fs_tra_p2_dynamic_1+3", 
        "t1_vibe_dixon_tra_p4_dynamic_1+3_W"
    ]
    
    source_path = Path(source_dir)
    
    if not source_path.exists():
        print(f"错误：源目录不存在 {source_dir}")
        return
    
    print("预览操作：每个一级文件夹只选择第一个匹配的二级文件夹")
    print("=" * 70)
    print("关键词:", keywords)
    print("=" * 70)
    
    match_folders = []
    no_match_folders = []
    
    # 遍历所有一级子文件夹
    for first_level in source_path.iterdir():
        if first_level.is_dir():
            found_match = False
            match_info = None
            
            # 查找第一个匹配的二级文件夹
            for second_level in first_level.iterdir():
                if second_level.is_dir() and not found_match:
                    folder_name = second_level.name.lower()
                    
                    if any(keyword.lower() in folder_name for keyword in keywords):
                        match_info = {
                            '一级文件夹': first_level.name,
                            '匹配的二级文件夹': second_level.name,
                            '匹配的关键词': next((k for k in keywords if k.lower() in folder_name), '未知')
                        }
                        match_folders.append(match_info)
                        found_match = True
                        break
            
            if not found_match:
                no_match_info = {
                    '一级文件夹名称': first_level.name,
                    '一级文件夹路径': str(first_level),
                    '二级文件夹数量': len([f for f in first_level.iterdir() if f.is_dir()]),
                    '二级文件夹列表': [f.name for f in first_level.iterdir() if f.is_dir()],
                    '无匹配原因': '未找到包含关键词的二级文件夹',
                    '检查时间': datetime.now().strftime('%Y-%-%m-%d %H:%M:%S')
                }
                no_match_folders.append(no_match_info)
    
    # 保存结果到Excel
    if no_match_folders or match_folders:
        with pd.ExcelWriter(excel_output, engine='openpyxl') as writer:
            if match_folders:
                match_df = pd.DataFrame(match_folders)
                match_df.to_excel(writer, sheet_name='匹配的文件夹', index=False)
            
            if no_match_folders:
                no_match_df = pd.DataFrame(no_match_folders)
                # 展开二级文件夹列表为字符串
                no_match_df['二级文件夹列表'] = no_match_df['二级文件夹列表'].apply(lambda x: ', '.join(x) if x else '无二级文件夹')
                no_match_df.to_excel(writer, sheet_name='无匹配的文件夹', index=False)
        
        print(f"\n预览结果已保存到: {excel_output}")
        print(f"匹配的文件夹: {len(match_folders)} 个")
        print(f"无匹配的文件夹: {len(no_match_folders)} 个")
        
        # 显示无匹配的文件夹列表
        if no_match_folders:
            print("\n无匹配的一级文件夹列表:")
            for folder in no_match_folders:
                print(f"  - {folder['一级文件夹名称']} (包含 {folder['二级文件夹数量']} 个二级文件夹)")
    
    return len(match_folders), len(no_match_folders)

def detailed_analysis():
    """
    详细分析并生成详细的Excel报告
    """
    source_dir = "/media/dell/T7 Shield/nnunet/数据中心/北大深圳/命名规范化"
    excel_output = "/media/dell/T7 Shield/nnunet/数据中心/北大深圳/文件夹详细分析.xlsx"
    
    keywords = [
        "t1_vibe_fs_tra_p2_bh",
        "t1_vibe_fs_tra_p2_dynamic_1+3", 
        "t1_vibe_dixon_tra_p4_dynamic_1+3_W"
    ]
    
    source_path = Path(source_dir)
    
    if not source_path.exists():
        print(f"错误：源目录不存在 {source_dir}")
        return
    
    all_folders_info = []
    
    # 遍历所有一级子文件夹
    for first_level in source_path.iterdir():
        if first_level.is_dir():
            folder_info = {
                '一级文件夹名称': first_level.name,
                '一级文件夹路径': str(first_level),
                '二级文件夹数量': 0,
                '二级文件夹列表': [],
                '匹配状态': '无匹配',
                '匹配的关键词': '',
                '匹配的二级文件夹': ''
            }
            
            # 收集所有二级文件夹信息
            secondary_folders = []
            for second_level in first_level.iterdir():
                if second_level.is_dir():
                    folder_info['二级文件夹数量'] += 1
                    folder_name = second_level.name
                    secondary_folders.append(folder_name)
                    
                    # 检查是否匹配关键词
                    if any(keyword.lower() in folder_name.lower() for keyword in keywords):
                        if folder_info['匹配状态'] == '无匹配':
                            folder_info['匹配状态'] = '已匹配'
                            folder_info['匹配的关键词'] = next((k for k in keywords if k.lower() in folder_name.lower()), '未知')
                            folder_info['匹配的二级文件夹'] = folder_name
            
            folder_info['二级文件夹列表'] = ', '.join(secondary_folders) if secondary_folders else '无二级文件夹'
            all_folders_info.append(folder_info)
    
    # 保存到Excel
    df = pd.DataFrame(all_folders_info)
    
    try:
        df.to_excel(excel_output, index=False, engine='openpyxl')
        print(f"详细分析报告已保存到: {excel_output}")
        
        # 统计信息
        total = len(all_folders_info)
        matched = len([f for f in all_folders_info if f['匹配状态'] == '已匹配'])
        not_matched = total - matched
        
        print(f"\n统计结果:")
        print(f"总一级文件夹数: {total}")
        print(f"有匹配的文件夹: {matched}")
        print(f"无匹配的文件夹: {not_matched}")
        
    except Exception as e:
        print(f"保存Excel文件时出错: {e}")

if __name__ == '__main__':
    # 选择执行模式：
    
    # 模式1: 只预览并导出Excel（不执行复制）
    print("模式1: 预览并导出Excel报告")
    match_count, no_match_count = preview_with_excel_export()
    
    if match_count > 0:
        # 确认是否执行复制
        confirm = input(f"\n找到 {match_count} 个匹配的文件夹，是否执行复制操作？(y/n): ")
        if confirm.lower() == 'y':
            print("\n开始执行复制操作...")
            copy_first_matching_folder_with_excel()
    
    # 模式2: 生成详细分析报告
    # print("\n模式2: 生成详细分析报告")
    # detailed_analysis()
    
    # 模式3: 直接执行复制并导出无匹配的文件夹
    # print("模式3: 直接执行复制并导出无匹配的文件夹")
    # copy_first_matching_folder_with_excel()