#!/usr/bin/env python3
"""
生成GitHub SSH密钥的脚本
"""
import os
import subprocess
import sys
from pathlib import Path

def check_ssh_directory():
    """检查并创建SSH目录"""
    ssh_dir = Path.home() / '.ssh'
    if not ssh_dir.exists():
        ssh_dir.mkdir(mode=0o700)
        print(f"✅ 创建SSH目录: {ssh_dir}")
    else:
        print(f"✅ SSH目录已存在: {ssh_dir}")
    return ssh_dir

def check_existing_keys(ssh_dir):
    """检查现有的SSH密钥"""
    key_files = ['id_rsa', 'id_ed25519', 'id_ecdsa']
    existing_keys = []
    
    for key_file in key_files:
        private_key = ssh_dir / key_file
        public_key = ssh_dir / f"{key_file}.pub"
        
        if private_key.exists() and public_key.exists():
            existing_keys.append(key_file)
    
    if existing_keys:
        print(f"🔍 发现现有SSH密钥: {', '.join(existing_keys)}")
        return existing_keys
    else:
        print("🔍 未发现现有SSH密钥")
        return []

def generate_ssh_key(email, key_type='ed25519'):
    """生成新的SSH密钥"""
    ssh_dir = check_ssh_directory()
    
    # 生成密钥文件名
    if key_type == 'ed25519':
        key_file = ssh_dir / 'id_ed25519'
        key_command = ['ssh-keygen', '-t', 'ed25519', '-C', email]
    else:
        key_file = ssh_dir / 'id_rsa'
        key_command = ['ssh-keygen', '-t', 'rsa', '-b', '4096', '-C', email]
    
    # 检查是否已存在
    if key_file.exists():
        print(f"⚠️ 密钥文件已存在: {key_file}")
        overwrite = input("是否覆盖现有密钥？(y/N): ").lower()
        if overwrite not in ['y', 'yes', '是']:
            print("❌ 取消生成新密钥")
            return None
    
    # 添加文件路径参数
    key_command.extend(['-f', str(key_file)])
    
    print(f"🔑 生成SSH密钥...")
    print(f"💻 执行命令: {' '.join(key_command)}")
    
    try:
        # 生成密钥（不设置密码）
        result = subprocess.run(
            key_command,
            input='\n\n',  # 空密码，两次回车
            text=True,
            capture_output=True
        )
        
        if result.returncode == 0:
            print(f"✅ SSH密钥生成成功!")
            print(f"📁 私钥文件: {key_file}")
            print(f"📁 公钥文件: {key_file}.pub")
            return key_file
        else:
            print(f"❌ 生成失败: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"❌ 生成过程出错: {e}")
        return None

def read_public_key(key_file):
    """读取公钥内容"""
    public_key_file = Path(str(key_file) + '.pub')
    
    if public_key_file.exists():
        try:
            with open(public_key_file, 'r') as f:
                public_key = f.read().strip()
            return public_key
        except Exception as e:
            print(f"❌ 读取公钥失败: {e}")
            return None
    else:
        print(f"❌ 公钥文件不存在: {public_key_file}")
        return None

def start_ssh_agent():
    """启动SSH代理"""
    print("🔧 启动SSH代理...")
    
    try:
        # 检查SSH代理是否已运行
        result = subprocess.run(['ssh-add', '-l'], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ SSH代理已运行")
            return True
        elif result.returncode == 1:
            print("✅ SSH代理已运行但无密钥")
            return True
        else:
            # 启动SSH代理
            result = subprocess.run(['ssh-agent', '-s'], capture_output=True, text=True, shell=True)
            if result.returncode == 0:
                print("✅ SSH代理启动成功")
                return True
            else:
                print(f"❌ SSH代理启动失败: {result.stderr}")
                return False
                
    except Exception as e:
        print(f"❌ SSH代理操作失败: {e}")
        return False

def add_key_to_agent(key_file):
    """将密钥添加到SSH代理"""
    print(f"🔑 添加密钥到SSH代理...")
    
    try:
        result = subprocess.run(['ssh-add', str(key_file)], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ 密钥已添加到SSH代理")
            return True
        else:
            print(f"❌ 添加密钥失败: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 添加密钥过程出错: {e}")
        return False

def show_github_setup_instructions(public_key):
    """显示GitHub设置说明"""
    print("\n" + "="*60)
    print("🐙 GitHub SSH密钥设置说明")
    print("="*60)
    
    print("\n1️⃣ 复制以下公钥内容:")
    print("-" * 40)
    print(public_key)
    print("-" * 40)
    
    print("\n2️⃣ 在GitHub上添加SSH密钥:")
    print("   1. 访问 https://github.com/settings/keys")
    print("   2. 点击 'New SSH key'")
    print("   3. 标题填写: 'My Computer SSH Key'")
    print("   4. 密钥类型选择: 'Authentication Key'")
    print("   5. 将上面的公钥内容粘贴到 'Key' 字段")
    print("   6. 点击 'Add SSH key'")
    
    print("\n3️⃣ 测试SSH连接:")
    print("   ssh -T git@github.com")
    
    print("\n4️⃣ 更新Git仓库远程地址:")
    print("   # 查看当前远程地址")
    print("   git remote -v")
    print("   # 更改为SSH地址（替换为您的用户名和仓库名）")
    print("   git remote set-url origin git@github.com:用户名/仓库名.git")
    
    print("\n5️⃣ 推送到GitHub:")
    print("   git push -u origin main")

def test_github_connection():
    """测试GitHub SSH连接"""
    print("\n🧪 测试GitHub SSH连接...")
    
    try:
        result = subprocess.run(
            ['ssh', '-T', 'git@github.com'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if 'successfully authenticated' in result.stderr:
            print("✅ GitHub SSH连接成功!")
            return True
        else:
            print("❌ GitHub SSH连接失败")
            print(f"输出: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("⏰ 连接超时，请检查网络")
        return False
    except Exception as e:
        print(f"❌ 连接测试失败: {e}")
        return False

def main():
    """主函数"""
    print("🔑 GitHub SSH密钥生成工具")
    print("=" * 50)
    
    # 检查现有密钥
    ssh_dir = check_ssh_directory()
    existing_keys = check_existing_keys(ssh_dir)
    
    # 获取邮箱
    print("\n📧 请输入您的GitHub邮箱地址:")
    email = input("邮箱: ").strip()
    
    if not email:
        print("❌ 邮箱地址不能为空")
        return
    
    # 选择密钥类型
    print("\n🔐 选择密钥类型:")
    print("1. Ed25519 (推荐，更安全更快)")
    print("2. RSA 4096 (传统，兼容性好)")
    
    choice = input("请选择 (1/2，默认1): ").strip()
    key_type = 'rsa' if choice == '2' else 'ed25519'
    
    # 生成密钥
    key_file = generate_ssh_key(email, key_type)
    
    if not key_file:
        print("❌ 密钥生成失败")
        return
    
    # 读取公钥
    public_key = read_public_key(key_file)
    
    if not public_key:
        print("❌ 无法读取公钥")
        return
    
    # 启动SSH代理并添加密钥
    if start_ssh_agent():
        add_key_to_agent(key_file)
    
    # 显示设置说明
    show_github_setup_instructions(public_key)
    
    # 询问是否测试连接
    print(f"\n❓ 是否现在测试GitHub连接？(需要先在GitHub上添加公钥)")
    test_now = input("测试连接? (y/N): ").lower()
    
    if test_now in ['y', 'yes', '是']:
        test_github_connection()
    
    print(f"\n🎉 SSH密钥设置完成!")
    print(f"💡 记住：请先在GitHub上添加公钥，然后才能使用SSH连接")

if __name__ == "__main__":
    main()
