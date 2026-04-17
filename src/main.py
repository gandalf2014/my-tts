#!/usr/bin/env python3
"""
TTS Application - 主入口文件

模块化文本转语音应用，基于edge-tts。

用法:
    python -m src.main          # 启动GUI应用
    python -m src.main --help   # 显示帮助信息
"""

import sys
import logging
import argparse
from pathlib import Path


def setup_logging(verbose: bool = False) -> None:
    """
    配置日志系统
    
    Args:
        verbose: 是否启用详细日志
    """
    level = logging.DEBUG if verbose else logging.INFO
    
    # 创建日志格式
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 配置根日志器
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # 文件处理器（可选）
    log_dir = Path.home() / ".tts_gui" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "tts_gui.log"
    
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)  # 文件始终记录详细日志
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)


def parse_args() -> argparse.Namespace:
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        prog='tts-gui',
        description='模块化文本转语音应用',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    python -m src.main          启动GUI应用
    python -m src.main -v       启动应用（详细日志）
    python -m src.main --help   显示此帮助信息
        """
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='启用详细日志输出'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 2.0.0'
    )
    
    return parser.parse_args()


def main() -> int:
    """
    主函数
    
    Returns:
        退出码
    """
    # 解析参数
    args = parse_args()
    
    # 配置日志
    setup_logging(verbose=args.verbose)
    logger = logging.getLogger(__name__)
    
    logger.info("TTS Application 启动")
    
    try:
        # 导入GUI模块
        import tkinter as tk
        from src.gui.main_window import MainWindow
        
        # 创建并运行应用
        root = tk.Tk()
        app = MainWindow(root)
        app.run()
        
        logger.info("TTS Application 正常退出")
        return 0
        
    except ImportError as e:
        logger.error(f"导入模块失败: {e}")
        print(f"错误: 导入模块失败 - {e}", file=sys.stderr)
        print("请确保已安装所有依赖: pip install -r requirements.txt", file=sys.stderr)
        return 1
        
    except Exception as e:
        logger.error(f"应用启动失败: {e}", exc_info=True)
        print(f"错误: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
