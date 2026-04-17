"""
语音生成模块 - 提供文本转语音生成功能
"""

import asyncio
import tempfile
import logging
from typing import Optional, Union
from pathlib import Path

logger = logging.getLogger(__name__)


class TTSGenerator:
    """
    TTS语音生成器 - 将文本转换为语音
    
    功能:
    - 同步/异步生成语音
    - 支持输出到文件或内存
    - 错误处理和日志记录
    """
    
    def __init__(self, voice_name: str):
        """
        初始化TTS生成器
        
        Args:
            voice_name: edge-tts语音名称，如 "zh-CN-XiaoxiaoNeural"
        """
        self.voice_name = voice_name
        logger.info(f"TTSGenerator 初始化，语音: {voice_name}")
    
    def generate(self, text: str, output_path: Optional[str] = None) -> str:
        """
        同步生成语音
        
        Args:
            text: 要转换的文本
            output_path: 输出文件路径，如果为None则使用临时文件
            
        Returns:
            生成的音频文件路径
            
        Raises:
            ValueError: 文本为空
            RuntimeError: 生成失败
        """
        if not text or not text.strip():
            raise ValueError("文本不能为空")
        
        text = text.strip()
        
        # 确定输出路径
        if output_path is None:
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
            output_path = temp_file.name
            temp_file.close()
        
        logger.info(f"开始生成语音，文本长度: {len(text)} 字符，输出: {output_path}")
        
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            import edge_tts
            communicate = edge_tts.Communicate(text, self.voice_name)
            loop.run_until_complete(communicate.save(output_path))
            loop.close()
            
            logger.info(f"语音生成成功: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"语音生成失败: {e}")
            raise RuntimeError(f"语音生成失败: {e}") from e
    
    async def generate_async(self, text: str, output_path: Optional[str] = None) -> str:
        """
        异步生成语音
        
        Args:
            text: 要转换的文本
            output_path: 输出文件路径，如果为None则使用临时文件
            
        Returns:
            生成的音频文件路径
            
        Raises:
            ValueError: 文本为空
            RuntimeError: 生成失败
        """
        if not text or not text.strip():
            raise ValueError("文本不能为空")
        
        text = text.strip()
        
        # 确定输出路径
        if output_path is None:
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
            output_path = temp_file.name
            temp_file.close()
        
        logger.info(f"开始异步生成语音，文本长度: {len(text)} 字符，输出: {output_path}")
        
        try:
            import edge_tts
            communicate = edge_tts.Communicate(text, self.voice_name)
            await communicate.save(output_path)
            
            logger.info(f"异步语音生成成功: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"异步语音生成失败: {e}")
            raise RuntimeError(f"异步语音生成失败: {e}") from e
    
    async def generate_to_bytes(self, text: str) -> bytes:
        """
        异步生成语音到内存
        
        Args:
            text: 要转换的文本
            
        Returns:
            音频数据(bytes)
            
        Raises:
            ValueError: 文本为空
            RuntimeError: 生成失败
        """
        if not text or not text.strip():
            raise ValueError("文本不能为空")
        
        text = text.strip()
        
        logger.info(f"开始生成语音到内存，文本长度: {len(text)} 字符")
        
        try:
            import edge_tts
            communicate = edge_tts.Communicate(text, self.voice_name)
            
            audio_data = bytearray()
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_data.extend(chunk["data"])
            
            logger.info(f"语音生成到内存成功，大小: {len(audio_data)} 字节")
            return bytes(audio_data)
            
        except Exception as e:
            logger.error(f"语音生成到内存失败: {e}")
            raise RuntimeError(f"语音生成到内存失败: {e}") from e
