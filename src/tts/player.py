"""
音频播放模块 - 提供音频播放控制功能
"""

import os
import logging
import pygame
from typing import Optional, Callable
from pathlib import Path
from enum import Enum
from mutagen.mp3 import MP3

logger = logging.getLogger(__name__)


class PlaybackState(Enum):
    """播放状态枚举"""
    STOPPED = "stopped"
    PLAYING = "playing"
    PAUSED = "paused"


class AudioPlayer:
    """
    音频播放器 - 基于pygame的音频播放控制
    
    功能:
    - 播放、暂停、停止音频
    - 播放状态查询
    - 播放完成回调
    - 音量控制
    """
    
    def __init__(self):
        """初始化音频播放器"""
        self._is_initialized = False
        self._current_file: Optional[str] = None
        self._is_playing = False
        self._is_paused = False
        self._duration: Optional[float] = None  # 音频时长（秒）
        self._on_finished_callback: Optional[Callable[[], None]] = None
        self._on_state_changed_callback: Optional[Callable[[str], None]] = None
        self._on_state_change_enum_callback: Optional[Callable[[PlaybackState], None]] = None
        
        self._init_mixer()
        logger.info("AudioPlayer 初始化完成")
    
    def _init_mixer(self):
        """初始化pygame mixer"""
        if not self._is_initialized:
            try:
                pygame.mixer.init()
                self._is_initialized = True
                logger.debug("pygame mixer 初始化成功")
            except Exception as e:
                logger.error(f"pygame mixer 初始化失败: {e}")
                raise RuntimeError(f"音频系统初始化失败: {e}") from e
    
    def play(self, file_path: str, on_finished: Optional[Callable[[], None]] = None) -> bool:
        """
        播放音频文件
        
        Args:
            file_path: 音频文件路径
            on_finished: 播放完成回调函数
            
        Returns:
            是否成功开始播放
            
        Raises:
            FileNotFoundError: 文件不存在
            RuntimeError: 播放失败
        """
        if not os.path.exists(file_path):
            logger.error(f"音频文件不存在: {file_path}")
            raise FileNotFoundError(f"音频文件不存在: {file_path}")
        
        try:
            # 如果正在播放，先停止
            if self._is_playing:
                self.stop()
            
            # 加载并播放
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
            
            # 检测音频时长
            self._duration = self._detect_duration(file_path)
            
            self._current_file = file_path
            self._is_playing = True
            self._is_paused = False
            self._on_finished_callback = on_finished
            
            logger.info(f"开始播放音频: {file_path}, 时长: {self._duration:.2f}秒")
            self._notify_state_changed("playing")
            
            return True
            
        except Exception as e:
            logger.error(f"播放音频失败: {e}")
            raise RuntimeError(f"播放音频失败: {e}") from e
    
    def stop(self) -> None:
        """
        停止音频播放
        
        停止当前播放并重置状态
        """
        if self._is_playing or self._is_paused:
            pygame.mixer.music.stop()
            self._is_playing = False
            self._is_paused = False
            self._duration = None
            
            logger.info("音频播放已停止")
            self._notify_state_changed("stopped")
    
    def pause(self) -> bool:
        """
        暂停音频播放
        
        Returns:
            是否成功暂停（如果未在播放则返回False）
        """
        if self._is_playing and not self._is_paused:
            pygame.mixer.music.pause()
            self._is_paused = True
            
            logger.info("音频播放已暂停")
            self._notify_state_changed("paused")
            return True
        
        return False
    
    def resume(self) -> bool:
        """
        恢复音频播放
        
        Returns:
            是否成功恢复（如果未暂停则返回False）
        """
        if self._is_paused:
            pygame.mixer.music.unpause()
            self._is_paused = False
            self._is_playing = True
            
            logger.info("音频播放已恢复")
            self._notify_state_changed("playing")
            return True
        
        return False
    
    def is_playing(self) -> bool:
        """
        检查是否正在播放
        
        Returns:
            是否正在播放（不包括暂停状态）
        """
        if not self._is_playing:
            return False
        
        # 检查pygame的实际播放状态
        # 注意：暂停时get_busy()返回True
        if not pygame.mixer.music.get_busy():
            # 播放已自然结束
            self._handle_playback_finished()
            return False
        
        # 如果是暂停状态，返回False
        return not self._is_paused
    
    def is_paused(self) -> bool:
        """
        检查是否暂停
        
        Returns:
            是否处于暂停状态
        """
        return self._is_paused
    
    def get_current_file(self) -> Optional[str]:
        """
        获取当前播放的文件路径
        
        Returns:
            当前音频文件路径，如果未加载则返回None
        """
        return self._current_file
    
    def set_volume(self, volume: float) -> None:
        """
        设置音量
        
        Args:
            volume: 音量值，范围0.0-1.0
            
        Raises:
            ValueError: 音量值超出范围
        """
        if not 0.0 <= volume <= 1.0:
            raise ValueError("音量值必须在0.0到1.0之间")
        
        pygame.mixer.music.set_volume(volume)
        logger.debug(f"音量设置为: {volume}")
    
    def get_volume(self) -> float:
        """
        获取当前音量
        
        Returns:
            当前音量值，范围0.0-1.0
        """
        return pygame.mixer.music.get_volume()
    
    def get_duration(self) -> Optional[float]:
        """
        获取当前音频的总时长
        
        Returns:
            音频总时长（秒），如果未加载音频则返回None
        """
        return self._duration
    
    def _detect_duration(self, file_path: str) -> Optional[float]:
        """
        检测音频文件的时长
        
        Args:
            file_path: 音频文件路径
            
        Returns:
            音频时长（秒），如果检测失败则返回None
        """
        try:
            # 使用mutagen检测MP3文件时长
            audio = MP3(file_path)
            duration = audio.info.length
            logger.debug(f"检测到音频时长: {duration:.2f}秒")
            return duration
        except Exception as e:
            logger.warning(f"检测音频时长失败: {e}")
            return None
    
    def set_on_state_changed(self, callback: Optional[Callable[[str], None]]) -> None:
        """
        设置播放状态变化回调
        
        Args:
            callback: 回调函数，接收状态字符串参数
                     状态值: "playing", "paused", "stopped", "finished"
        """
        self._on_state_changed_callback = callback
        logger.debug(f"状态变化回调已{'设置' if callback else '清除'}")
    
    def set_callbacks(
        self,
        on_state_change: Optional[Callable[[PlaybackState], None]] = None,
        on_complete: Optional[Callable[[], None]] = None
    ) -> None:
        """
        设置播放器回调（支持PlaybackState枚举）
        
        Args:
            on_state_change: 状态变化回调，接收PlaybackState枚举值
            on_complete: 播放完成回调
        """
        self._on_state_change_enum_callback = on_state_change
        if on_complete:
            self._on_finished_callback = on_complete
        logger.debug(f"回调已设置: state_change={on_state_change is not None}, complete={on_complete is not None}")
    
    def _notify_state_changed(self, state: str) -> None:
        """通知状态变化"""
        # 调用字符串回调
        if self._on_state_changed_callback:
            try:
                self._on_state_changed_callback(state)
            except Exception as e:
                logger.error(f"状态变化回调执行失败: {e}")
        
        # 调用枚举回调
        if self._on_state_change_enum_callback:
            try:
                state_enum = {
                    "playing": PlaybackState.PLAYING,
                    "paused": PlaybackState.PAUSED,
                    "stopped": PlaybackState.STOPPED,
                    "finished": PlaybackState.STOPPED
                }.get(state, PlaybackState.STOPPED)
                self._on_state_change_enum_callback(state_enum)
            except Exception as e:
                logger.error(f"枚举状态变化回调执行失败: {e}")
    
    def _handle_playback_finished(self) -> None:
        """处理播放完成"""
        was_playing = self._is_playing
        self._is_playing = False
        self._is_paused = False
        
        if was_playing:
            logger.info("音频播放完成")
            self._notify_state_changed("finished")
            
            # 执行播放完成回调
            if self._on_finished_callback:
                try:
                    self._on_finished_callback()
                except Exception as e:
                    logger.error(f"播放完成回调执行失败: {e}")
    
    def check_playback(self) -> bool:
        """
        检查播放状态并处理播放完成
        
        用于在GUI主循环中定期调用，检测播放是否自然结束
        
        Returns:
            是否仍在播放
        """
        if self._is_playing and not self._is_paused:
            if not pygame.mixer.music.get_busy():
                self._handle_playback_finished()
                return False
            return True
        return False
    
    def cleanup(self) -> None:
        """
        清理资源
        
        停止播放并清理临时资源
        """
        self.stop()
        self._current_file = None
        self._duration = None
        self._on_finished_callback = None
        self._on_state_changed_callback = None
        
        logger.info("AudioPlayer 资源已清理")
    
    def __del__(self):
        """析构时清理资源"""
        try:
            if self._is_initialized and (self._is_playing or self._is_paused):
                self.stop()
        except Exception:
            pass  # 忽略析构时的错误
