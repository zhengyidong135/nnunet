import os
import shutil

def move_deepest_folders():
    # 目标文件夹路径
    target_dir = "/media/dell/T7 Shield1/nnunet/AllData/GXZL/finished/dicom_规范化/Group1"
    
    if not os.path.exists(target_dir):
        print(f"错误: 目标文件夹不存在: {target_dir}")
        return
    
    print(f"处理目录: {target_dir}")
    print("=" * 60)
    
    # 遍历一级子文件夹
    primary_folders = [item for item in os.listdir(target_dir) 
                      if os.path.isdir(os.path.join(target_dir, item))]
    
    print(f"找到 {len(primary_folders)} 个一级子文件夹")
    
    total_moved = 0
    folders_processed = 0
    
    for primary_folder in primary_folders:
        primary_path = os.path.join(target_dir, primary_folder)
        print(f"\n处理一级文件夹: {primary_folder}")
        print("-" * 40)
        
        # 收集当前一级文件夹中已有的文件夹名称（避免冲突）
        existing_folders = set([item for item in os.listdir(primary_path) 
                               if os.path.isdir(os.path.join(primary_path, item))])
        
        # 遍历二级子文件夹
        secondary_items = os.listdir(primary_path)
        secondary_folders = [item for item in secondary_items 
                           if os.path.isdir(os.path.join(primary_path, item))]
        
        if not secondary_folders:
            print(f"  ⚠ 没有二级子文件夹，跳过")
            continue
        
        for secondary_folder in secondary_folders:
            secondary_path = os.path.join(primary_path, secondary_folder)
            print(f"  ↳ 处理二级文件夹: {secondary_folder}")
            
            # 查找并移动最深层的文件夹
            moved_count = find_and_move_deepest_folders(secondary_path, primary_path, existing_folders)
            
            if moved_count > 0:
                folders_processed += moved_count
                total_moved += moved_count
            
            # 检查并删除空的二级文件夹
            if not os.listdir(secondary_path):
                try:
                    os.rmdir(secondary_path)
                    print(f"  ✓ 删除空二级文件夹: {secondary_folder}")
                except Exception as e:
                    print(f"  ⚠ 删除空文件夹失败: {e}")
        
        if folders_processed > 0:
            print(f"  在本文件夹中移动了 {folders_processed} 个最深级文件夹")
        else:
            print(f"  没有需要移动的深层文件夹")
        
        folders_processed = 0
    
    print("\n" + "=" * 60)
    print(f"移动完成！")
    print(f"总计移动了 {total_moved} 个最深级文件夹")

def find_and_move_deepest_folders(current_path, target_primary_path, existing_folders):
    """
    递归查找最深层的文件夹并移动到一级文件夹
    返回移动的文件夹数量
    """
    moved_count = 0
    items = os.listdir(current_path)
    has_subfolders = False
    
    # 首先检查当前文件夹的子文件夹
    for item in items:
        item_path = os.path.join(current_path, item)
        if os.path.isdir(item_path):
            has_subfolders = True
            # 递归处理子文件夹
            moved_count += find_and_move_deepest_folders(item_path, target_primary_path, existing_folders)
    
    # 如果没有子文件夹，当前文件夹就是最深层的文件夹
    if not has_subfolders and current_path != target_primary_path:
        folder_name = os.path.basename(current_path)
        
        # 检查目标文件夹是否已存在
        dest_path = os.path.join(target_primary_path, folder_name)
        
        if folder_name in existing_folders:
            print(f"    ⚠ 文件夹 '{folder_name}' 已存在，跳过移动")
            return moved_count
        
        try:
            # 移动整个文件夹
            shutil.move(current_path, dest_path)
            moved_count += 1
            existing_folders.add(folder_name)  # 添加到已存在的文件夹集合
            print(f"    ✓ 移动: {folder_name} → {os.path.basename(target_primary_path)}/")
        except Exception as e:
            print(f"    ✗ 移动文件夹 '{folder_name}' 时出错: {e}")
    
    return moved_count

def preview_structure():
    """
    预览目录结构，显示哪些文件夹会被移动
    """
    target_dir = "/media/dell/T7 Shield1/nnunet/AllData/GXZL/finished/dicom_规范化/Group1"
    
    if not os.path.exists(target_dir):
        print(f"错误: 目标文件夹不存在: {target_dir}")
        return
    
    print("预览目录结构 (将被移动的文件夹):")
    print("=" * 60)
    
    primary_folders = [item for item in os.listdir(target_dir) 
                      if os.path.isdir(os.path.join(target_dir, item))]
    
    total_preview = 0
    
    for primary_folder in primary_folders:
        primary_path = os.path.join(target_dir, primary_folder)
        print(f"\n一级文件夹: {primary_folder}")
        
        secondary_folders = [item for item in os.listdir(primary_path) 
                           if os.path.isdir(os.path.join(primary_path, item))]
        
        folder_count = 0
        
        for secondary_folder in secondary_folders:
            secondary_path = os.path.join(primary_path, secondary_folder)
            
            # 查找最深文件夹
            deepest_folders = []
            
            def find_preview(current_path, depth=0):
                items = os.listdir(current_path)
                has_subfolders = False
                
                for item in items:
                    item_path = os.path.join(current_path, item)
                    if os.path.isdir(item_path):
                        has_subfolders = True
                        find_preview(item_path, depth + 1)
                
                if not has_subfolders and depth > 1 and current_path != primary_path:
                    folder_name = os.path.basename(current_path)
                    # 计算相对路径
                    rel_path = os.path.relpath(current_path, secondary_path)
                    deepest_folders.append((folder_name, rel_path))
            
            find_preview(secondary_path, 1)
            
            if deepest_folders:
                folder_count += len(deepest_folders)
                total_preview += len(deepest_folders)
                print(f"  ├─ 二级: {secondary_folder}")
                for folder_name, rel_path in deepest_folders[:3]:  # 最多显示3个
                    print(f"  │     └─ 将被移动: {folder_name}")
                if len(deepest_folders) > 3:
                    print(f"  │        ... 和其他 {len(deepest_folders)-3} 个文件夹")
        
        if folder_count > 0:
            print(f"  总计: {folder_count} 个文件夹将被移动")
    
    print(f"\n总计预览: {total_preview} 个文件夹将被移动")

def main():
    print("请选择操作模式:")
    print("1. 预览将被移动的文件夹")
    print("2. 执行移动操作")
    print("3. 退出")
    
    choice = input("\n请输入选择 (1-3): ")
    
    if choice == "1":
        preview_structure()
    elif choice == "2":
        print("\n警告: 将把最深级文件夹移动到对应的一级文件夹中")
        print("注意: 移动操作无法撤销，请确保已备份重要数据！")
        confirm = input("确认执行移动操作吗？(y/N): ")
        if confirm.lower() == "y":
            move_deepest_folders()
        else:
            print("操作已取消")
    elif choice == "3":
        print("退出程序")
    else:
        print("无效选择")

if __name__ == "__main__":
    main()