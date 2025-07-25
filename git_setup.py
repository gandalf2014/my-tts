#!/usr/bin/env python3
"""
Git仓库设置和提交脚本
"""
import os
import subprocess
import sys

def run_command(command, description=""):
    """运行命令并显示结果"""
    if description:
        print(f"📋 {description}")
    
    print(f"💻 执行: {command}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=os.getcwd())
        
        if result.returncode == 0:
            print(f"✅ 成功")
            if result.stdout.strip():
                print(f"📤 输出: {result.stdout.strip()}")
        else:
            print(f"❌ 失败 (返回码: {result.returncode})")
            if result.stderr.strip():
                print(f"❌ 错误: {result.stderr.strip()}")
            return False
        
        print()
        return True
        
    except Exception as e:
        print(f"❌ 执行出错: {e}")
        print()
        return False

def check_git():
    """检查Git是否安装"""
    print("🔍 检查Git环境...")
    return run_command("git --version", "检查Git版本")

def init_git_repo():
    """初始化Git仓库"""
    if os.path.exists('.git'):
        print("✅ Git仓库已存在")
        return True
    
    return run_command("git init", "初始化Git仓库")

def setup_git_config():
    """设置Git配置"""
    print("⚙️ 设置Git配置...")
    
    # 检查是否已有配置
    result = subprocess.run("git config user.name", shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print("请输入您的Git用户名:")
        username = input("用户名: ").strip()
        if username:
            run_command(f'git config user.name "{username}"', "设置用户名")
    
    result = subprocess.run("git config user.email", shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print("请输入您的Git邮箱:")
        email = input("邮箱: ").strip()
        if email:
            run_command(f'git config user.email "{email}"', "设置邮箱")

def clean_project():
    """清理项目文件"""
    print("🧹 清理项目文件...")
    
    # 删除测试文件
    test_files = [
        "test_*.py", "demo_*.py", "compare_*.mp3", "voice_*.mp3", 
        "param_*.mp3", "clean_*.mp3", "preview_*.mp3", "*.tmp"
    ]
    
    import glob
    for pattern in test_files:
        files = glob.glob(pattern)
        for file in files:
            try:
                os.remove(file)
                print(f"🗑️ 删除: {file}")
            except:
                pass

def prepare_core_files():
    """准备核心文件"""
    print("📦 准备核心文件...")
    
    # 核心文件列表
    core_files = [
        "tts_gui.py",
        "requirements.txt", 
        "build_exe.py",
        "build_exe.bat",
        "run_tts_gui.bat",
        "README_GITHUB.md",
        "LICENSE",
        ".gitignore"
    ]
    
    missing_files = []
    for file in core_files:
        if not os.path.exists(file):
            missing_files.append(file)
        else:
            print(f"✅ {file}")
    
    if missing_files:
        print(f"❌ 缺少文件: {', '.join(missing_files)}")
        return False
    
    return True

def add_and_commit():
    """添加文件并提交"""
    print("📝 添加文件到Git...")
    
    # 添加核心文件
    core_files = [
        "tts_gui.py",
        "requirements.txt", 
        "build_exe.py",
        "build_exe.bat", 
        "run_tts_gui.bat",
        "README_GITHUB.md",
        "LICENSE",
        ".gitignore"
    ]
    
    for file in core_files:
        if os.path.exists(file):
            run_command(f"git add {file}", f"添加 {file}")
    
    # 提交
    commit_message = "🎤 初始提交: 文本转语音GUI转换器\n\n✨ 功能特点:\n- 支持14种中文语音\n- 现代化GUI界面\n- 实时试听功能\n- MP3保存功能\n- 可打包为exe文件"
    
    return run_command(f'git commit -m "{commit_message}"', "提交更改")

def show_github_instructions():
    """显示GitHub操作说明"""
    print("🐙 GitHub操作说明")
    print("=" * 50)
    
    print("1️⃣ 在GitHub上创建新仓库:")
    print("   - 访问 https://github.com/new")
    print("   - 仓库名称: my-tts 或 text-to-speech-gui")
    print("   - 描述: 文本转语音GUI转换器")
    print("   - 设为公开仓库")
    print("   - 不要初始化README、.gitignore或LICENSE")
    
    print("\n2️⃣ 连接本地仓库到GitHub:")
    print("   git remote add origin https://github.com/你的用户名/仓库名.git")
    
    print("\n3️⃣ 推送代码到GitHub:")
    print("   git branch -M main")
    print("   git push -u origin main")
    
    print("\n4️⃣ 完成后的仓库将包含:")
    print("   ✅ 主程序文件 (tts_gui.py)")
    print("   ✅ 依赖文件 (requirements.txt)")
    print("   ✅ 打包脚本 (build_exe.py)")
    print("   ✅ 使用说明 (README_GITHUB.md)")
    print("   ✅ 许可证 (LICENSE)")
    print("   ✅ Git配置 (.gitignore)")

def main():
    """主函数"""
    print("🚀 Git仓库设置向导")
    print("=" * 50)
    
    # 检查Git
    if not check_git():
        print("❌ 请先安装Git: https://git-scm.com/")
        return
    
    # 清理项目
    clean_project()
    
    # 准备核心文件
    if not prepare_core_files():
        print("❌ 核心文件缺失，请检查项目完整性")
        return
    
    # 初始化Git仓库
    if not init_git_repo():
        return
    
    # 设置Git配置
    setup_git_config()
    
    # 添加并提交文件
    if not add_and_commit():
        print("❌ 提交失败")
        return
    
    print("🎉 本地Git仓库设置完成！")
    print()
    
    # 显示GitHub操作说明
    show_github_instructions()
    
    print("\n💡 提示:")
    print("- 将README_GITHUB.md重命名为README.md")
    print("- 根据需要修改README中的GitHub链接")
    print("- 考虑添加项目截图到README")

if __name__ == "__main__":
    main()
