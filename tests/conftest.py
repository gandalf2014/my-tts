"""
TTS应用测试配置
"""

import sys
from pathlib import Path

# 添加src目录到路径
src_path = Path(__file__).parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))
