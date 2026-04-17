"""
语音生成模块 - 提供文本转语音生成功能
"""

import asyncio
import tempfile
import threading
import logging
from typing import Optional, Union, Callable
from pathlib import Path
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class TTSOptions:
    """
    TTS生成选项
    
    Attributes:
        speed: 语速倍率 (0.5-2.0)
        pitch: 音调倍率 (0.5-2.0)  
        volume: 音量百分比 (0-100)
    """
    speed: float = 1.0
    pitch: float = 1.0
    volume: float = 100.0


def create_tts_options(
    speed: float = 1.0,
    pitch: float = 1.0,
    volume: float = 100.0
) -> TTSOptions:
    """
    创建TTS选项
    
    Args:
        speed: 语速倍率
        pitch: 音调倍率
        volume: 音量百分比
        
    Returns:
        TTSOptions对象
    """
    return TTSOptions(speed=speed, pitch=pitch, volume=volume)


class TTSGenerator:
    """
    TTS语音生成器 - 将文本转换为语音
    
    功能:
    - 同步/异步生成语音
    - 支持输出到文件或内存
    - 回调式异步生成
    - 错误处理和日志记录
    """
    
    def __init__(self):
        """
        初始化TTS生成器
        """
        self._current_voice_name: Optional[str] = None
        logger.info("TTSGenerator 初始化完成")
    
    def generate(
        self,
        text: str,
        voice: Optional[object] = None,
        options: Optional[TTSOptions] = None,
        output_path: Optional[str] = None,
        on_complete: Optional[Callable[[str], None]] = None,
        on_error: Optional[Callable[[Exception], None]] = None
    ) -> Optional[str]:
        """
        生成语音（支持同步和回调两种模式）
        
        Args:
            text: 要转换的文本
            voice: Voice对象（从voice_manager获取）
            options: TTS选项
            output_path: 输出文件路径，如果为None则使用临时文件
            on_complete: 完成回调（异步模式）
            on_error: 错误回调（异步模式）
            
        Returns:
            生成的音频文件路径（同步模式），或None（异步模式）
            
        Raises:
            ValueError: 文本为空
            RuntimeError: 生成失败（同步模式）
        """
        if not text or not text.strip():
            raise ValueError("文本不能为空")
        
        # 获取语音名称
        voice_name = None
        if voice is not None:
            voice_name = voice.short_name
            self._current_voice_name = voice_name
        
        if not voice_name:
            raise ValueError("未指定语音")
        
        text = text.strip()
        
        # 确定输出路径
        if output_path is None:
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
            output_path = temp_file.name
            temp_file.close()
        
        logger.info(f"开始生成语音，文本长度: {len(text)} 字符，语音: {voice_name}，输出: {output_path}")
        
        # 异步模式（有回调）
        if on_complete or on_error:
            def _generate_thread():
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    
                    import edge_tts
                    communicate = edge_tts.Communicate(text, voice_name)
                    loop.run_until_complete(communicate.save(output_path))
                    loop.close()
                    
                    logger.info(f"语音生成成功: {output_path}")
                    if on_complete:
                        on_complete(output_path)
                        
                except Exception as e:
                    logger.error(f"语音生成失败: {e}")
                    if on_error:
                        on_error(e)
            
            thread = threading.Thread(target=_generate_thread, daemon=True)
            thread.start()
            return None
        
        # 同步模式
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            import edge_tts
            communicate = edge_tts.Communicate(text, voice_name)
            loop.run_until_complete(communicate.save(output_path))
            loop.close()
            
            logger.info(f"语音生成成功: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"语音生成失败: {e}")
            raise RuntimeError(f"语音生成失败: {e}") from e
    
    def generate_sync(
        self,
        text: str,
        voice_name: str,
        output_path: Optional[str] = None
    ) -> str:
        """
        同步生成语音（简化接口）
        
        Args:
            text: 要转换的文本
            voice_name: edge-tts语音名称
            output_path: 输出文件路径
            
        Returns:
            生成的音频文件路径
        """
        self._current_voice_name = voice_name
        
        if not text or not text.strip():
            raise ValueError("文本不能为空")
        
        text = text.strip()
        
        if output_path is None:
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
            output_path = temp_file.name
            temp_file.close()
        
        logger.info(f"开始同步生成语音，文本长度: {len(text)} 字符，语音: {voice_name}")
        
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            import edge_tts
            communicate = edge_tts.Communicate(text, voice_name)
            loop.run_until_complete(communicate.save(output_path))
            loop.close()
            
            logger.info(f"同步语音生成成功: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"同步语音生成失败: {e}")
            raise RuntimeError(f"同步语音生成失败: {e}") from e
    
    async def generate_async(self, text: str, voice_name: str, output_path: Optional[str] = None) -> str:
        """
        异步生成语音
        
        Args:
            text: 要转换的文本
            voice_name: edge-tts语音名称
            output_path: 输出文件路径，如果为None则使用临时文件
            
        Returns:
            生成的音频文件路径
        """
        self._current_voice_name = voice_name
        
        if not text or not text.strip():
            raise ValueError("文本不能为空")
        
        text = text.strip()
        
        if output_path is None:
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
            output_path = temp_file.name
            temp_file.close()
        
        logger.info(f"开始异步生成语音，文本长度: {len(text)} 字符，输出: {output_path}")
        
        try:
            import edge_tts
            communicate = edge_tts.Communicate(text, voice_name)
            await communicate.save(output_path)
            
            logger.info(f"异步语音生成成功: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"异步语音生成失败: {e}")
            raise RuntimeError(f"异步语音生成失败: {e}") from e
    
    async def generate_to_bytes(self, text: str, voice_name: str) -> bytes:
        """
        异步生成语音到内存
        
        Args:
            text: 要转换的文本
            voice_name: edge-tts语音名称
            
        Returns:
            音频数据(bytes)
        """
        self._current_voice_name = voice_name
        
        if not text or not text.strip():
            raise ValueError("文本不能为空")
        
        text = text.strip()
        
        logger.info(f"开始生成语音到内存，文本长度: {len(text)} 字符")
        
        try:
            import edge_tts
            communicate = edge_tts.Communicate(text, voice_name)
            
            audio_data = bytearray()
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_data.extend(chunk["data"])
            
            logger.info(f"语音生成到内存成功，大小: {len(audio_data)} 字节")
            return bytes(audio_data)
            
        except Exception as e:
            logger.error(f"语音生成到内存失败: {e}")
            raise RuntimeError(f"语音生成到内存失败: {e}") from e
