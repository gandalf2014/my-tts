"""
TTS应用主入口
"""

import logging
import sys
import tkinter as tk

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def main():
    """主函数"""
    logger.info("启动文本转语音应用...")
    
    # 创建Tk根窗口
    root = tk.Tk()
    
    # 创建主窗口
    from .gui.main_window import MainWindow
    app = MainWindow(root)
    
    # 运行应用
    app.run()
    
    logger.info("应用已退出")


if __name__ == "__main__":
    main()
