import os
import subprocess
import sys

def run_cmd(cmd):
    print(f">>> {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"错误: {result.stderr}")
        return False
    else:
        print(f"成功")
        return True

def upload_to_github():
    repo_path = "/home/dell/下载/my_nnunet"
    os.chdir(repo_path)
    
    print("🚀 开始上传到GitHub...")
    
    # 1. 检查SSH密钥
    print("\n1. 检查SSH配置...")
    ssh_key = os.path.expanduser("~/.ssh/id_ed25519")
    if not os.path.exists(ssh_key):
        print("⚠️ 未找到SSH密钥，请先运行：")
        print("   ssh-keygen -t ed25519 -C 'your_email@example.com'")
        print("   然后将公钥(~/.ssh/id_ed25519.pub)添加到GitHub")
        sys.exit(1)
    
    # 2. 测试SSH连接
    if not run_cmd("ssh -T git@github.com"):
        print("⚠️ SSH连接失败，请检查SSH密钥配置")
        sys.exit(1)
    
    # 3. 设置远程仓库（使用SSH）
    print("\n2. 设置远程仓库...")
    run_cmd("git remote remove origin || true")
    run_cmd("git remote add origin git@github.com:zhengyidong135/nnunet.git")
    
    # 4. 添加文件
    print("\n3. 添加文件...")
    run_cmd("git add .")
    
    # 5. 提交
    print("\n4. 提交更改...")
    run_cmd('git commit -m "上传nnUNet项目"')
    
    # 6. 推送
    print("\n5. 推送到GitHub...")
    if not run_cmd("git push -u origin main"):
        print("尝试强制推送...")
        run_cmd("git push -u origin main --force")
    
    print("\n✅ 上传成功！")

if __name__ == "__main__":
    upload_to_github()