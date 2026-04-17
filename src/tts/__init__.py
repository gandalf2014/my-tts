"""
TTS模块 - 语音合成核心功能
"""

from .voice_manager import VoiceManager
from .generator import TTSGenerator
from .player import AudioPlayer
from .batch_processor import (
    BatchProcessor,
    BatchConfig,
    Segment,
    FailedSegment,
    SegmentationMode,
    segment_by_paragraph,
    segment_by_chars
)

__all__ = [
    "VoiceManager",
    "TTSGenerator",
    "AudioPlayer",
    "BatchProcessor",
    "BatchConfig",
    "Segment",
    "FailedSegment",
    "SegmentationMode",
    "segment_by_paragraph",
    "segment_by_chars"
]
