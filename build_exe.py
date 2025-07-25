#!/usr/bin/env python3
"""
打包TTS GUI程序为exe文件的脚本
"""
import os
import sys
import subprocess
import shutil

def check_pyinstaller():
    """检查PyInstaller是否已安装"""
    try:
        import PyInstaller
        print("✅ PyInstaller 已安装")
        return True
    except ImportError:
        print("❌ PyInstaller 未安装")
        return False

def install_pyinstaller():
    """安装PyInstaller"""
    print("正在安装 PyInstaller...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], 
                      check=True, capture_output=True, text=True)
        print("✅ PyInstaller 安装成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ PyInstaller 安装失败: {e}")
        return False

def create_spec_file():
    """创建PyInstaller规格文件"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['tts_gui.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'edge_tts',
        'pygame',
        'tkinter',
        'asyncio',
        'threading',
        'tempfile',
        'os',
        'messagebox'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='文本转语音转换器',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
'''
    
    with open('tts_gui.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("✅ 创建了 tts_gui.spec 文件")

def build_exe():
    """构建exe文件"""
    print("开始构建exe文件...")
    print("这可能需要几分钟时间，请耐心等待...")
    
    try:
        # 使用spec文件构建
        result = subprocess.run([
            sys.executable, "-m", "PyInstaller", 
            "--clean", 
            "tts_gui.spec"
        ], capture_output=True, text=True, cwd=os.getcwd())
        
        if result.returncode == 0:
            print("✅ exe文件构建成功！")
            return True
        else:
            print(f"❌ 构建失败:")
            print(result.stdout)
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ 构建过程出错: {e}")
        return False

def create_simple_build():
    """创建简单的单文件构建"""
    print("尝试简单构建方式...")
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "PyInstaller",
            "--onefile",
            "--windowed", 
            "--name", "文本转语音转换器",
            "--hidden-import", "edge_tts",
            "--hidden-import", "pygame",
            "--hidden-import", "asyncio",
            "--hidden-import", "threading",
            "tts_gui.py"
        ], capture_output=True, text=True, cwd=os.getcwd())
        
        if result.returncode == 0:
            print("✅ 简单构建成功！")
            return True
        else:
            print(f"❌ 简单构建失败:")
            print(result.stdout)
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ 简单构建出错: {e}")
        return False

def check_dependencies():
    """检查必要的依赖"""
    print("检查依赖包...")
    
    required_packages = ['edge-tts', 'pygame']
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'edge-tts':
                import edge_tts
            elif package == 'pygame':
                import pygame
            print(f"✅ {package} 已安装")
        except ImportError:
            print(f"❌ {package} 未安装")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"请先安装缺失的包: pip install {' '.join(missing_packages)}")
        return False
    
    return True

def cleanup_build_files():
    """清理构建文件"""
    print("清理构建文件...")
    
    cleanup_dirs = ['build', '__pycache__']
    cleanup_files = ['tts_gui.spec']
    
    for dir_name in cleanup_dirs:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"✅ 删除了 {dir_name} 目录")
    
    for file_name in cleanup_files:
        if os.path.exists(file_name):
            os.remove(file_name)
            print(f"✅ 删除了 {file_name} 文件")

def find_exe_file():
    """查找生成的exe文件"""
    possible_paths = [
        os.path.join('dist', '文本转语音转换器.exe'),
        os.path.join('dist', 'tts_gui.exe'),
        os.path.join('dist', 'tts_gui', 'tts_gui.exe')
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    # 查找dist目录下的所有exe文件
    if os.path.exists('dist'):
        for root, dirs, files in os.walk('dist'):
            for file in files:
                if file.endswith('.exe'):
                    return os.path.join(root, file)
    
    return None

def main():
    """主函数"""
    print("🚀 TTS GUI程序打包工具")
    print("=" * 50)
    
    # 检查依赖
    if not check_dependencies():
        return
    
    # 检查PyInstaller
    if not check_pyinstaller():
        if not install_pyinstaller():
            return
    
    # 尝试简单构建
    print("\n📦 开始打包...")
    success = create_simple_build()
    
    if not success:
        print("\n尝试使用spec文件构建...")
        create_spec_file()
        success = build_exe()
    
    if success:
        exe_path = find_exe_file()
        if exe_path:
            file_size = os.path.getsize(exe_path)
            print(f"\n🎉 打包成功！")
            print(f"📁 exe文件位置: {exe_path}")
            print(f"📊 文件大小: {file_size / (1024*1024):.1f} MB")
            print(f"\n✨ 您现在可以直接运行exe文件，无需安装Python环境！")
        else:
            print("\n⚠️ 构建完成但找不到exe文件，请检查dist目录")
    else:
        print("\n❌ 打包失败，请检查错误信息")
    
    # 询问是否清理构建文件
    print(f"\n🧹 是否清理构建文件？(y/n): ", end="")
    try:
        choice = input().lower()
        if choice in ['y', 'yes', '是']:
            cleanup_build_files()
    except:
        pass

if __name__ == "__main__":
    main()
