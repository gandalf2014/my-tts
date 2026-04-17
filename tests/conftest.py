"""
TTS应用测试配置和fixtures

提供所有测试所需的公共fixtures和配置。
"""

import sys
import os
import tempfile
import shutil
import logging
from pathlib import Path
from typing import Generator, List
from unittest.mock import MagicMock, AsyncMock, patch

import pytest

# 添加src目录到路径
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))


# ============================================================================
# 测试配置
# ============================================================================

def pytest_configure(config):
    """pytest配置钩子"""
    # 设置日志级别
    logging.basicConfig(level=logging.DEBUG)
    # 注册自定义标记
    config.addinivalue_line(
        "markers", "unit: 单元测试"
    )
    config.addinivalue_line(
        "markers", "integration: 集成测试"
    )
    config.addinivalue_line(
        "markers", "slow: 慢速测试"
    )


# ============================================================================
# 临时文件fixtures
# ============================================================================

@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """创建临时目录"""
    dir_path = Path(tempfile.mkdtemp())
    yield dir_path
    shutil.rmtree(dir_path, ignore_errors=True)


@pytest.fixture
def temp_config_file(temp_dir: Path) -> Path:
    """创建临时配置文件路径"""
    return temp_dir / "test_config.json"


@pytest.fixture
def temp_audio_file(temp_dir: Path) -> Path:
    """创建临时音频文件路径"""
    return temp_dir / "test_audio.mp3"


# ============================================================================
# Voice fixtures
# ============================================================================

@pytest.fixture
def sample_voice_data() -> dict:
    """示例语音数据"""
    return {
        "ShortName": "zh-CN-XiaoxuanNeural",
        "FriendlyName": "Microsoft Xiaoxuan Online (Natural) - Chinese (Mainland)",
        "Locale": "zh-CN",
        "Gender": "Female"
    }


@pytest.fixture
def sample_voice():
    """示例Voice对象"""
    from src.tts.voice_manager import Voice
    return Voice(
        short_name="zh-CN-XiaoxuanNeural",
        friendly_name="Microsoft Xiaoxuan Online (Natural) - Chinese (Mainland)",
        locale="zh-CN",
        gender="Female"
    )


@pytest.fixture
def sample_voices() -> List:
    """多个示例Voice对象列表"""
    from src.tts.voice_manager import Voice
    return [
        Voice("zh-CN-XiaoxuanNeural", "Xiaoxuan", "zh-CN", "Female"),
        Voice("zh-CN-XiaochenNeural", "Xiaochen", "zh-CN", "Female"),
        Voice("zh-CN-YunxiNeural", "Yunxi", "zh-CN", "Male"),
        Voice("en-US-JennyNeural", "Jenny", "en-US", "Female"),
        Voice("en-US-GuyNeural", "Guy", "en-US", "Male"),
        Voice("ja-JP-NanamiNeural", "Nanami", "ja-JP", "Female"),
    ]


# ============================================================================
# VoiceManager fixtures
# ============================================================================

@pytest.fixture
def voice_manager():
    """VoiceManager实例（不加载真实语音）"""
    from src.tts.voice_manager import VoiceManager
    return VoiceManager()


@pytest.fixture
def loaded_voice_manager(voice_manager, sample_voices):
    """已加载示例语音的VoiceManager"""
    voice_manager._voices = sample_voices
    voice_manager._is_loaded = True
    return voice_manager


# ============================================================================
# TTSGenerator fixtures
# ============================================================================

@pytest.fixture
def tts_generator():
    """TTSGenerator实例"""
    from src.tts.generator import TTSGenerator
    return TTSGenerator()


@pytest.fixture
def tts_options():
    """默认TTS选项"""
    from src.tts.generator import TTSOptions
    return TTSOptions(speed=1.0, pitch=1.0, volume=100.0)


@pytest.fixture
def mock_edge_tts():
    """Mock edge-tts模块"""
    mock = MagicMock()
    mock.list_voices = AsyncMock(return_value=[
        {"ShortName": "zh-CN-XiaoxuanNeural", "FriendlyName": "Xiaoxuan", "Locale": "zh-CN", "Gender": "Female"}
    ])
    mock.Communicate = MagicMock()
    return mock


# ============================================================================
# Settings fixtures
# ============================================================================

@pytest.fixture
def settings(temp_config_file: Path):
    """Settings实例（使用临时配置文件）"""
    from src.config.settings import Settings
    return Settings(config_path=str(temp_config_file))


@pytest.fixture
def default_config():
    """默认配置"""
    from src.config.settings import AppConfig
    return AppConfig()


# ============================================================================
# AudioPlayer fixtures
# ============================================================================

@pytest.fixture
def audio_player():
    """AudioPlayer实例"""
    from src.tts.player import AudioPlayer
    return AudioPlayer()


@pytest.fixture
def mock_audio_file(temp_dir: Path) -> Path:
    """创建模拟音频文件"""
    audio_path = temp_dir / "test.mp3"
    # 写入最小MP3头部
    audio_path.write_bytes(b'ID3\x03\x00\x00\x00\x00\x00\x00')
    return audio_path


# ============================================================================
# 回调fixtures
# ============================================================================

@pytest.fixture
def mock_callback():
    """Mock回调函数"""
    return MagicMock()


@pytest.fixture
def mock_complete_callback():
    """Mock完成回调函数"""
    return MagicMock()


@pytest.fixture
def mock_error_callback():
    """Mock错误回调函数"""
    return MagicMock()
