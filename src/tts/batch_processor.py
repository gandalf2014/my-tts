"""
批量处理模块 - 提供文本分割和批量语音生成功能
"""

import logging
import asyncio
import threading
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Callable, Tuple
from enum import Enum

logger = logging.getLogger(__name__)


class SegmentationMode(Enum):
    """分割模式枚举"""
    PARAGRAPH = "paragraph"  # 按段落分割
    CHARS = "chars"  # 按字符数分割


@dataclass
class Segment:
    """
    文本段落数据类
    
    Attributes:
        index: 段落索引（从0开始）
        text: 段落文本内容
        preview: 段落预览（截断后的文本，用于显示）
        filename: 建议的输出文件名
    """
    index: int
    text: str
    preview: str
    filename: str
    
    def __post_init__(self):
        """初始化后处理：自动生成预览"""
        if not self.preview:
            # 截断文本用于预览，最多显示50个字符
            self.preview = self.text[:50] + "..." if len(self.text) > 50 else self.text
        if not self.filename:
            self.filename = f"segment_{self.index + 1:03d}.mp3"


@dataclass
class BatchConfig:
    """
    批量处理配置数据类
    
    Attributes:
        segmentation_mode: 分割模式
        max_chars_per_segment: 每个段落最大字符数（仅chars模式有效）
        output_directory: 输出目录路径
    """
    segmentation_mode: SegmentationMode = SegmentationMode.PARAGRAPH
    max_chars_per_segment: int = 500
    output_directory: str = ""
    
    def __post_init__(self):
        """初始化后处理：设置默认输出目录"""
        if not self.output_directory:
            # 默认使用用户目录下的tts_output
            self.output_directory = str(Path.home() / "tts_output")


@dataclass
class FailedSegment:
    """
    失败段落数据类
    
    Attributes:
        index: 段落索引
        text: 段落文本
        error: 错误信息
    """
    index: int
    text: str
    error: str


def segment_by_paragraph(text: str) -> List[Segment]:
    """
    按段落分割文本
    
    将文本按照双换行符（\\n\\n）分割成多个段落，
    忽略空段落和只包含空白字符的段落。
    
    Args:
        text: 要分割的文本内容
        
    Returns:
        Segment对象列表，每个对象包含段落索引、文本、预览和文件名
        
    Example:
        >>> text = "第一段\\n\\n第二段\\n\\n第三段"
        >>> segments = segment_by_paragraph(text)
        >>> len(segments)
        3
    """
    if not text or not text.strip():
        return []
    
    # 按双换行符分割
    raw_paragraphs = text.split('\n\n')
    
    segments = []
    index = 0
    
    for para in raw_paragraphs:
        # 去除首尾空白
        para = para.strip()
        # 跳过空段落
        if not para:
            continue
        
        # 将段落内的单换行符替换为空格（保持文本连贯性）
        para_text = para.replace('\n', ' ')
        
        segment = Segment(
            index=index,
            text=para_text,
            preview="",  # 由__post_init__自动生成
            filename=""  # 由__post_init__自动生成
        )
        segments.append(segment)
        index += 1
    
    logger.info(f"按段落分割完成，共 {len(segments)} 个段落")
    return segments


def segment_by_chars(text: str, max_chars: int = 500) -> List[Segment]:
    """
    按字符数分割文本
    
    先按段落分割，然后对于超过max_chars的段落进行二次分割。
    确保每个段落不超过max_chars字符。
    
    Args:
        text: 要分割的文本内容
        max_chars: 每个段落的最大字符数，默认500
        
    Returns:
        Segment对象列表
        
    Raises:
        ValueError: max_chars小于1时抛出
        
    Example:
        >>> text = "这是一个很长的段落..." * 100
        >>> segments = segment_by_chars(text, max_chars=200)
        >>> all(len(s.text) <= 200 for s in segments)
        True
    """
    if max_chars < 1:
        raise ValueError(f"max_chars必须大于0，当前值: {max_chars}")
    
    if not text or not text.strip():
        return []
    
    segments = []
    index = 0
    
    # 先按段落分割
    raw_paragraphs = text.split('\n\n')
    
    for para in raw_paragraphs:
        para = para.strip()
        if not para:
            continue
        
        # 将段落内的单换行符替换为空格
        para_text = para.replace('\n', ' ')
        
        # 如果段落长度超过max_chars，需要进一步分割
        if len(para_text) > max_chars:
            # 按句子分割（优先在句号、问号、感叹号处分割）
            # 简单实现：直接按max_chars分割
            start = 0
            while start < len(para_text):
                end = start + max_chars
                
                # 尝试在句子结束符附近分割
                if end < len(para_text):
                    # 向后查找句子结束符
                    for sep in ['。', '！', '？', '.', '!', '?', '；', ';']:
                        last_sep = para_text.rfind(sep, start, end + 50)
                        if last_sep != -1 and last_sep > start:
                            end = last_sep + 1
                            break
                
                chunk = para_text[start:end].strip()
                if chunk:
                    segment = Segment(
                        index=index,
                        text=chunk,
                        preview="",
                        filename=""
                    )
                    segments.append(segment)
                    index += 1
                
                start = end
        else:
            segment = Segment(
                index=index,
                text=para_text,
                preview="",
                filename=""
            )
            segments.append(segment)
            index += 1
    
    logger.info(f"按字符分割完成，共 {len(segments)} 个段落，最大长度: {max_chars}")
    return segments


class BatchProcessor:
    """
    批量处理器 - 编排文本分割和批量语音生成
    
    功能:
    - 支持按段落或字符数分割文本
    - 批量生成语音文件
    - 进度回调通知
    - 取消机制
    - 错误处理和记录
    
    Attributes:
        generator: TTSGenerator实例
        config: BatchConfig配置
        _is_cancelled: 取消标志
        _failed_segments: 失败段落列表
    """
    
    def __init__(
        self,
        generator,  # TTSGenerator instance
        config: Optional[BatchConfig] = None
    ):
        """
        初始化批量处理器
        
        Args:
            generator: TTSGenerator实例
            config: 批量处理配置，为None时使用默认配置
        """
        self.generator = generator
        self.config = config or BatchConfig()
        self._is_cancelled = False
        self._failed_segments: List[FailedSegment] = []
        logger.info(f"BatchProcessor 初始化完成，配置: {self.config}")
    
    @property
    def failed_segments(self) -> List[FailedSegment]:
        """获取失败段落列表"""
        return self._failed_segments.copy()
    
    @property
    def is_cancelled(self) -> bool:
        """获取取消状态"""
        return self._is_cancelled
    
    def cancel(self) -> None:
        """
        取消当前批量处理
        
        设置取消标志，当前段落处理完成后停止后续处理。
        """
        self._is_cancelled = True
        logger.info("批量处理已请求取消")
    
    def reset(self) -> None:
        """
        重置处理器状态
        
        清除取消标志和失败记录，准备下一次批量处理。
        """
        self._is_cancelled = False
        self._failed_segments = []
        logger.info("BatchProcessor 状态已重置")
    
    def segment_text(self, text: str) -> List[Segment]:
        """
        根据配置分割文本
        
        Args:
            text: 要分割的文本
            
        Returns:
            Segment列表
        """
        if self.config.segmentation_mode == SegmentationMode.PARAGRAPH:
            return segment_by_paragraph(text)
        else:
            return segment_by_chars(text, self.config.max_chars_per_segment)
    
    def process_batch(
        self,
        text: str,
        voice,  # Voice object
        options=None,  # TTSOptions
        progress_callback: Optional[Callable[[int, int, Segment], None]] = None,
        on_complete: Optional[Callable[[List[str], List[FailedSegment]], None]] = None,
        on_error: Optional[Callable[[Exception], None]] = None,
        timeout: float = 30.0
    ) -> Tuple[List[str], List[FailedSegment]]:
        """
        批量处理文本生成语音
        
        同步处理模式：分割文本，逐个生成语音文件。
        支持进度回调和取消机制。
        
        Args:
            text: 要处理的文本内容
            voice: Voice对象
            options: TTS选项
            progress_callback: 进度回调函数，参数为(current, total, segment)
            on_complete: 完成回调函数
            on_error: 错误回调函数
            timeout: 单个段落的超时时间（秒）
            
        Returns:
            元组：(成功生成的文件路径列表, 失败段落列表)
            
        Raises:
            ValueError: 文本为空或无效时抛出
        """
        if not text or not text.strip():
            raise ValueError("文本不能为空")
        
        # 重置状态
        self.reset()
        
        # 分割文本
        segments = self.segment_text(text)
        if not segments:
            logger.warning("文本分割后没有有效段落")
            return [], []
        
        logger.info(f"开始批量处理，共 {len(segments)} 个段落")
        
        # 确保输出目录存在
        output_dir = Path(self.config.output_directory)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        success_files: List[str] = []
        total = len(segments)
        
        for segment in segments:
            # 检查取消标志
            if self._is_cancelled:
                logger.info(f"批量处理已取消，已处理 {segment.index}/{total} 个段落")
                break
            
            try:
                # 生成输出文件路径
                output_path = str(output_dir / segment.filename)
                
                logger.debug(f"处理段落 {segment.index + 1}/{total}: {segment.preview}")
                
                # 调用进度回调
                if progress_callback:
                    progress_callback(segment.index + 1, total, segment)
                
                # 同步生成语音，带超时控制
                # 使用线程+超时实现
                result = [None]
                error = [None]
                
                def _generate():
                    try:
                        result[0] = self.generator.generate_sync(
                            text=segment.text,
                            voice_name=voice.short_name if hasattr(voice, 'short_name') else str(voice),
                            options=options,
                            output_path=output_path
                        )
                    except Exception as e:
                        error[0] = e
                
                thread = threading.Thread(target=_generate, daemon=True)
                thread.start()
                thread.join(timeout=timeout)
                
                if thread.is_alive():
                    # 超时
                    failed = FailedSegment(
                        index=segment.index,
                        text=segment.text,
                        error=f"生成超时（超过{timeout}秒）"
                    )
                    self._failed_segments.append(failed)
                    logger.error(f"段落 {segment.index + 1} 生成超时")
                    continue
                
                if error[0]:
                    # 生成失败
                    failed = FailedSegment(
                        index=segment.index,
                        text=segment.text,
                        error=str(error[0])
                    )
                    self._failed_segments.append(failed)
                    logger.error(f"段落 {segment.index + 1} 生成失败: {error[0]}")
                    continue
                
                if result[0]:
                    success_files.append(result[0])
                    logger.info(f"段落 {segment.index + 1}/{total} 生成成功: {result[0]}")
                
            except Exception as e:
                failed = FailedSegment(
                    index=segment.index,
                    text=segment.text,
                    error=str(e)
                )
                self._failed_segments.append(failed)
                logger.error(f"段落 {segment.index + 1} 处理异常: {e}")
        
        # 完成回调
        if on_complete:
            on_complete(success_files, self._failed_segments)
        
        logger.info(f"批量处理完成，成功: {len(success_files)}，失败: {len(self._failed_segments)}")
        return success_files, self._failed_segments
    
    async def process_batch_async(
        self,
        text: str,
        voice,  # Voice object
        options=None,  # TTSOptions
        progress_callback: Optional[Callable[[int, int, Segment], None]] = None,
        timeout: float = 30.0
    ) -> Tuple[List[str], List[FailedSegment]]:
        """
        异步批量处理文本生成语音
        
        异步处理模式：分割文本，逐个异步生成语音文件。
        支持进度回调和取消机制。
        
        Args:
            text: 要处理的文本内容
            voice: Voice对象
            options: TTS选项
            progress_callback: 进度回调函数
            timeout: 单个段落的超时时间（秒）
            
        Returns:
            元组：(成功生成的文件路径列表, 失败段落列表)
            
        Raises:
            ValueError: 文本为空或无效时抛出
        """
        if not text or not text.strip():
            raise ValueError("文本不能为空")
        
        # 重置状态
        self.reset()
        
        # 分割文本
        segments = self.segment_text(text)
        if not segments:
            logger.warning("文本分割后没有有效段落")
            return [], []
        
        logger.info(f"开始异步批量处理，共 {len(segments)} 个段落")
        
        # 确保输出目录存在
        output_dir = Path(self.config.output_directory)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        success_files: List[str] = []
        total = len(segments)
        
        for segment in segments:
            # 检查取消标志
            if self._is_cancelled:
                logger.info(f"异步批量处理已取消，已处理 {segment.index}/{total} 个段落")
                break
            
            try:
                # 生成输出文件路径
                output_path = str(output_dir / segment.filename)
                
                logger.debug(f"异步处理段落 {segment.index + 1}/{total}: {segment.preview}")
                
                # 调用进度回调
                if progress_callback:
                    progress_callback(segment.index + 1, total, segment)
                
                # 异步生成语音，带超时控制
                try:
                    voice_name = voice.short_name if hasattr(voice, 'short_name') else str(voice)
                    result = await asyncio.wait_for(
                        self.generator.generate_async(
                            text=segment.text,
                            voice_name=voice_name,
                            options=options,
                            output_path=output_path
                        ),
                        timeout=timeout
                    )
                    success_files.append(result)
                    logger.info(f"段落 {segment.index + 1}/{total} 异步生成成功: {result}")
                    
                except asyncio.TimeoutError:
                    failed = FailedSegment(
                        index=segment.index,
                        text=segment.text,
                        error=f"生成超时（超过{timeout}秒）"
                    )
                    self._failed_segments.append(failed)
                    logger.error(f"段落 {segment.index + 1} 异步生成超时")
                    
            except Exception as e:
                failed = FailedSegment(
                    index=segment.index,
                    text=segment.text,
                    error=str(e)
                )
                self._failed_segments.append(failed)
                logger.error(f"段落 {segment.index + 1} 异步处理异常: {e}")
        
        logger.info(f"异步批量处理完成，成功: {len(success_files)}，失败: {len(self._failed_segments)}")
        return success_files, self._failed_segments
