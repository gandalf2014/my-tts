#!/usr/bin/env python3
"""
为Git项目创建标签的脚本
"""
import subprocess
import sys
from datetime import datetime

def run_git_command(command, description=""):
    """运行Git命令"""
    if description:
        print(f"📋 {description}")
    
    print(f"💻 执行: {command}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd='.')
        
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

def check_git_status():
    """检查Git状态"""
    print("🔍 检查Git仓库状态...")
    
    # 检查是否在Git仓库中
    result = subprocess.run("git rev-parse --git-dir", shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print("❌ 当前目录不是Git仓库")
        return False
    
    # 检查是否有未提交的更改
    result = subprocess.run("git status --porcelain", shell=True, capture_output=True, text=True)
    if result.stdout.strip():
        print("⚠️ 发现未提交的更改:")
        print(result.stdout)
        
        commit_first = input("是否先提交这些更改？(y/N): ").lower()
        if commit_first in ['y', 'yes', '是']:
            return commit_changes()
        else:
            print("💡 建议先提交更改再创建标签")
            return False
    
    print("✅ 工作目录干净，可以创建标签")
    return True

def commit_changes():
    """提交未提交的更改"""
    print("📝 提交更改...")
    
    # 添加所有更改
    if not run_git_command("git add .", "添加所有更改"):
        return False
    
    # 获取提交信息
    commit_message = input("请输入提交信息: ").strip()
    if not commit_message:
        commit_message = "Update files before tagging"
    
    # 提交更改
    return run_git_command(f'git commit -m "{commit_message}"', "提交更改")

def get_current_commit_info():
    """获取当前提交信息"""
    try:
        # 获取当前提交哈希
        result = subprocess.run("git rev-parse HEAD", shell=True, capture_output=True, text=True)
        commit_hash = result.stdout.strip()[:8]
        
        # 获取当前提交信息
        result = subprocess.run("git log -1 --pretty=format:'%s'", shell=True, capture_output=True, text=True)
        commit_message = result.stdout.strip().strip("'")
        
        # 获取提交日期
        result = subprocess.run("git log -1 --pretty=format:'%ci'", shell=True, capture_output=True, text=True)
        commit_date = result.stdout.strip().strip("'")
        
        return commit_hash, commit_message, commit_date
        
    except Exception as e:
        print(f"❌ 获取提交信息失败: {e}")
        return None, None, None

def list_existing_tags():
    """列出现有标签"""
    print("🏷️ 现有标签:")
    
    try:
        result = subprocess.run("git tag -l", shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            tags = result.stdout.strip().split('\n')
            if tags and tags[0]:
                for tag in tags:
                    if tag.strip():
                        print(f"   📌 {tag}")
                return tags
            else:
                print("   (无现有标签)")
                return []
        else:
            print("   ❌ 无法获取标签列表")
            return []
            
    except Exception as e:
        print(f"   ❌ 获取标签失败: {e}")
        return []

def suggest_tag_name(existing_tags):
    """建议标签名称"""
    print("\n💡 标签命名建议:")
    
    # 检查是否有版本标签
    version_tags = [tag for tag in existing_tags if tag.startswith('v')]
    
    if not version_tags:
        suggested_version = "v1.0.0"
        print(f"   🎯 首个版本: {suggested_version}")
    else:
        # 简单的版本递增建议
        latest_version = sorted(version_tags)[-1]
        print(f"   📈 最新版本: {latest_version}")
        
        # 尝试解析版本号并建议下一个版本
        try:
            if latest_version.startswith('v'):
                version_part = latest_version[1:]
                parts = version_part.split('.')
                if len(parts) >= 3:
                    major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])
                    suggested_version = f"v{major}.{minor}.{patch + 1}"
                    print(f"   🎯 建议版本: {suggested_version}")
                else:
                    suggested_version = "v1.0.1"
            else:
                suggested_version = "v1.0.1"
        except:
            suggested_version = "v1.0.1"
    
    # 其他建议
    today = datetime.now().strftime("%Y%m%d")
    print(f"   📅 日期标签: release-{today}")
    print(f"   🚀 功能标签: feature-tts-gui")
    print(f"   🎤 主题标签: tts-v1.0")
    
    return suggested_version

def create_tag(tag_name, tag_message, annotated=True):
    """创建标签"""
    print(f"🏷️ 创建标签: {tag_name}")
    
    if annotated:
        # 创建带注释的标签
        command = f'git tag -a "{tag_name}" -m "{tag_message}"'
        description = "创建带注释的标签"
    else:
        # 创建轻量级标签
        command = f'git tag "{tag_name}"'
        description = "创建轻量级标签"
    
    return run_git_command(command, description)

def show_tag_info(tag_name):
    """显示标签信息"""
    print(f"📋 标签信息: {tag_name}")
    
    # 显示标签详情
    run_git_command(f"git show {tag_name}", "显示标签详情")

def push_tags():
    """推送标签到远程仓库"""
    print("🚀 推送标签到远程仓库...")
    
    # 检查是否有远程仓库
    result = subprocess.run("git remote", shell=True, capture_output=True, text=True)
    if not result.stdout.strip():
        print("⚠️ 没有配置远程仓库，跳过推送")
        return True
    
    # 推送所有标签
    push_all = input("是否推送所有标签到远程仓库？(Y/n): ").lower()
    if push_all not in ['n', 'no', '否']:
        return run_git_command("git push --tags", "推送所有标签")
    
    return True

def main():
    """主函数"""
    print("🏷️ Git标签创建工具")
    print("=" * 50)
    
    # 检查Git状态
    if not check_git_status():
        return
    
    # 获取当前提交信息
    commit_hash, commit_message, commit_date = get_current_commit_info()
    
    if commit_hash:
        print(f"📍 当前提交: {commit_hash}")
        print(f"💬 提交信息: {commit_message}")
        print(f"📅 提交时间: {commit_date}")
        print()
    
    # 列出现有标签
    existing_tags = list_existing_tags()
    
    # 建议标签名称
    suggested_tag = suggest_tag_name(existing_tags)
    
    # 获取标签名称
    print(f"\n🏷️ 请输入标签名称:")
    tag_name = input(f"标签名称 (默认: {suggested_tag}): ").strip()
    
    if not tag_name:
        tag_name = suggested_tag
    
    # 检查标签是否已存在
    if tag_name in existing_tags:
        print(f"❌ 标签 '{tag_name}' 已存在")
        overwrite = input("是否删除现有标签并重新创建？(y/N): ").lower()
        if overwrite in ['y', 'yes', '是']:
            run_git_command(f"git tag -d {tag_name}", "删除现有标签")
        else:
            print("❌ 取消创建标签")
            return
    
    # 选择标签类型
    print(f"\n🎯 选择标签类型:")
    print("1. 带注释的标签 (推荐，包含详细信息)")
    print("2. 轻量级标签 (简单标记)")
    
    tag_type = input("请选择 (1/2，默认1): ").strip()
    annotated = tag_type != '2'
    
    # 获取标签信息
    if annotated:
        print(f"\n📝 请输入标签描述:")
        default_message = f"🎤 文本转语音GUI转换器 {tag_name}\n\n✨ 功能特点:\n- 支持14种中文语音\n- 现代化GUI界面\n- 实时试听功能\n- MP3保存功能\n- 可打包为exe文件"
        
        print("默认描述:")
        print("-" * 40)
        print(default_message)
        print("-" * 40)
        
        custom_message = input("自定义描述 (回车使用默认): ").strip()
        tag_message = custom_message if custom_message else default_message
    else:
        tag_message = ""
    
    # 创建标签
    if create_tag(tag_name, tag_message, annotated):
        print(f"🎉 标签 '{tag_name}' 创建成功!")
        
        # 显示标签信息
        if annotated:
            show_tag_info(tag_name)
        
        # 推送标签
        push_tags()
        
        print(f"\n✅ 标签创建完成!")
        print(f"🏷️ 标签名称: {tag_name}")
        print(f"📍 标记提交: {commit_hash}")
        
        if annotated:
            print(f"💬 标签描述: {tag_message.split(chr(10))[0]}...")
        
        print(f"\n💡 后续操作:")
        print(f"   查看标签: git show {tag_name}")
        print(f"   删除标签: git tag -d {tag_name}")
        print(f"   推送标签: git push origin {tag_name}")
        
    else:
        print("❌ 标签创建失败")

if __name__ == "__main__":
    main()
