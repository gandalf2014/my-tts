"""
语音生成模块 - 文本转语音核心逻辑
"""

import asyncio
import threading
import tempfile
import os
import logging
from typing import Optional, Callable
from dataclasses import dataclass

import edge_tts

from .voice_manager import Voice

logger = logging.getLogger(__name__)


@dataclass
class TTSOptions:
    """TTS生成选项"""
    rate: Optional[str] = None  # 语速: "-50%" to "+100%"
    pitch: Optional[str] = None  # 音调: "-50Hz" to "+50Hz"
    volume: Optional[str] = None  # 音量: "-50%" to "+100%"


class TTSGenerator:
    """
    语音生成器 - 将文本转换为语音
    
    功能:
    - 异步生成语音
    - 支持参数控制（语速、音调、音量）
    - 支持生成到文件或内存
    - 进度回调支持
    """
    
    def __init__(self):
        self._is_generating = False
        self._cancel_flag = False
    
    @property
    def is_generating(self) -> bool:
        """是否正在生成"""
        return self._is_generating
    
    def cancel(self) -> None:
        """取消当前生成任务"""
        self._cancel_flag = True
    
    def generate(
        self,
        text: str,
        voice: Voice,
        output_path: Optional[str] = None,
        options: Optional[TTSOptions] = None,
        on_complete: Optional[Callable[[str], None]] = None,
        on_error: Optional[Callable[[Exception], None]] = None
    ) -> None:
        """
        异步生成语音
        
        Args:
            text: 要转换的文本
            voice: Voice对象
            output_path: 输出文件路径，如果为None则使用临时文件
            options: 生成选项
            on_complete: 完成回调，参数为输出文件路径
            on_error: 错误回调
        """
        def _generate():
            try:
                self._is_generating = True
                self._cancel_flag = False
                
                # 确定输出路径
                if output_path is None:
                    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
                    temp_file.close()
                    file_path = temp_file.name
                else:
                    file_path = output_path
                
                logger.info(f"开始生成语音: voice={voice.short_name}, text_length={len(text)}")
                
                # 创建异步事件循环
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                # 创建Communicate对象
                kwargs = {"text": text, "voice": voice.short_name}
                
                # 添加参数（如果支持）
                if options:
                    if options.rate:
                        kwargs["rate"] = options.rate
                    if options.pitch:
                        kwargs["pitch"] = options.pitch
                    if options.volume:
                        kwargs["volume"] = options.volume
                
                communicate = edge_tts.Communicate(**kwargs)
                
                # 生成音频
                loop.run_until_complete(communicate.save(file_path))
                loop.close()
                
                if self._cancel_flag:
                    logger.info("生成已取消")
                    if os.path.exists(file_path):
                        os.remove(file_path)
                    return
                
                logger.info(f"语音生成完成: {file_path}")
                
                if on_complete:
                    on_complete(file_path)
                    
            except Exception as e:
                logger.error(f"生成语音失败: {e}")
                if on_error:
                    on_error(e)
                    
            finally:
                self._is_generating = False
        
        thread = threading.Thread(target=_generate, daemon=True)
        thread.start()
    
    def generate_sync(
        self,
        text: str,
        voice: Voice,
        output_path: Optional[str] = None,
        options: Optional[TTSOptions] = None
    ) -> str:
        """
        同步生成语音（阻塞）
        
        Args:
            text: 要转换的文本
            voice: Voice对象
            output_path: 输出文件路径
            options: 生成选项
            
        Returns:
            输出文件路径
        """
        result_path = None
        error = None
        
        def on_complete(path):
            nonlocal result_path
            result_path = path
            
        def on_error(e):
            nonlocal error
            error = e
        
        # 在当前线程同步执行
        self._is_generating = True
        self._cancel_flag = False
        
        try:
            if output_path is None:
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
                temp_file.close()
                file_path = temp_file.name
            else:
                file_path = output_path
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            kwargs = {"text": text, "voice": voice.short_name}
            
            if options:
                if options.rate:
                    kwargs["rate"] = options.rate
                if options.pitch:
                    kwargs["pitch"] = options.pitch
                if options.volume:
                    kwargs["volume"] = options.volume
            
            communicate = edge_tts.Communicate(**kwargs)
            loop.run_until_complete(communicate.save(file_path))
            loop.close()
            
            result_path = file_path
            logger.info(f"语音生成完成: {result_path}")
            
        except Exception as e:
            logger.error(f"生成语音失败: {e}")
            error = e
            
        finally:
            self._is_generating = False
        
        if error:
            raise error
            
        return result_path


def create_tts_options(
    speed: float = 1.0,
    pitch: float = 1.0,
    volume: float = 100.0
) -> TTSOptions:
    """
    创建TTS选项的便捷函数
    
    Args:
        speed: 语速倍率 (0.5 - 2.0)
        pitch: 音调倍率 (0.5 - 2.0)
        volume: 音量百分比 (0 - 100)
        
    Returns:
        TTSOptions对象
    """
    options = TTSOptions()
    
    # 语速: 转换为百分比格式
    if speed != 1.0:
        rate_percent = int((speed - 1.0) * 100)
        options.rate = f"{'+' if rate_percent >= 0 else ''}{rate_percent}%"
    
    # 音调: 转换为Hz格式
    if pitch != 1.0:
        pitch_hz = int((pitch - 1.0) * 50)
        options.pitch = f"{'+' if pitch_hz >= 0 else ''}{pitch_hz}Hz"
    
    # 音量: 转换为百分比格式
    if volume != 100.0:
        vol_percent = int(volume - 100)
        options.volume = f"{'+' if vol_percent >= 0 else ''}{vol_percent}%"
    
    return options
