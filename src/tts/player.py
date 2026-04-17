"""
音频播放模块 - 播放MP3音频文件
"""

import os
import logging
import time
from typing import Optional, Callable
from enum import Enum

import pygame

logger = logging.getLogger(__name__)


class PlaybackState(Enum):
    """播放状态"""
    STOPPED = "stopped"
    PLAYING = "playing"
    PAUSED = "paused"


class AudioPlayer:
    """
    音频播放器 - 管理音频播放状态和控制
    
    功能:
    - 播放、暂停、停止音频
    - 播放进度查询
    - 播放完成回调
    """
    
    def __init__(self):
        """初始化播放器"""
        # 初始化pygame mixer
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        
        self._state = PlaybackState.STOPPED
        self._current_file: Optional[str] = None
        self._on_state_change: Optional[Callable[[PlaybackState], None]] = None
        self._on_complete: Optional[Callable[[], None]] = None
        self._check_thread = None
        self._stop_check = False
    
    @property
    def state(self) -> PlaybackState:
        """当前播放状态"""
        return self._state
    
    @property
    def current_file(self) -> Optional[str]:
        """当前加载的文件路径"""
        return self._current_file
    
    @property
    def is_playing(self) -> bool:
        """是否正在播放"""
        return self._state == PlaybackState.PLAYING
    
    @property
    def is_paused(self) -> bool:
        """是否已暂停"""
        return self._state == PlaybackState.PAUSED
    
    @property
    def duration(self) -> float:
        """音频总时长（秒）"""
        if self._current_file and os.path.exists(self._current_file):
            try:
                sound = pygame.mixer.Sound(self._current_file)
                return sound.get_length()
            except Exception:
                pass
        return 0.0
    
    @property
    def position(self) -> float:
        """当前播放位置（秒）- pygame不支持精确查询，返回估计值"""
        return 0.0  # pygame.mixer不支持获取当前播放位置
    
    def set_callbacks(
        self,
        on_state_change: Optional[Callable[[PlaybackState], None]] = None,
        on_complete: Optional[Callable[[], None]] = None
    ) -> None:
        """
        设置回调函数
        
        Args:
            on_state_change: 状态变化回调
            on_complete: 播放完成回调
        """
        self._on_state_change = on_state_change
        self._on_complete = on_complete
    
    def load(self, file_path: str) -> bool:
        """
        加载音频文件
        
        Args:
            file_path: 音频文件路径
            
        Returns:
            是否成功加载
        """
        if not os.path.exists(file_path):
            logger.error(f"音频文件不存在: {file_path}")
            return False
        
        try:
            # 如果正在播放，先停止
            if self._state != PlaybackState.STOPPED:
                self.stop()
            
            self._current_file = file_path
            logger.info(f"已加载音频文件: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"加载音频失败: {e}")
            return False
    
    def play(self, file_path: Optional[str] = None) -> bool:
        """
        播放音频
        
        Args:
            file_path: 音频文件路径，如果为None则播放当前已加载的文件
            
        Returns:
            是否成功开始播放
        """
        # 如果已暂停，恢复播放
        if self._state == PlaybackState.PAUSED:
            return self.resume()
        
        # 加载文件
        if file_path:
            if not self.load(file_path):
                return False
        
        if not self._current_file:
            logger.error("没有可播放的音频文件")
            return False
        
        try:
            pygame.mixer.music.load(self._current_file)
            pygame.mixer.music.play()
            
            self._set_state(PlaybackState.PLAYING)
            self._start_check_thread()
            
            logger.info(f"开始播放: {self._current_file}")
            return True
            
        except Exception as e:
            logger.error(f"播放失败: {e}")
            return False
    
    def pause(self) -> bool:
        """
        暂停播放
        
        Returns:
            是否成功暂停
        """
        if self._state != PlaybackState.PLAYING:
            return False
        
        try:
            pygame.mixer.music.pause()
            self._set_state(PlaybackState.PAUSED)
            logger.info("播放已暂停")
            return True
            
        except Exception as e:
            logger.error(f"暂停失败: {e}")
            return False
    
    def resume(self) -> bool:
        """
        恢复播放
        
        Returns:
            是否成功恢复
        """
        if self._state != PlaybackState.PAUSED:
            return False
        
        try:
            pygame.mixer.music.unpause()
            self._set_state(PlaybackState.PLAYING)
            self._start_check_thread()
            logger.info("播放已恢复")
            return True
            
        except Exception as e:
            logger.error(f"恢复播放失败: {e}")
            return False
    
    def stop(self) -> None:
        """停止播放"""
        try:
            pygame.mixer.music.stop()
            self._stop_check = True
            self._set_state(PlaybackState.STOPPED)
            logger.info("播放已停止")
            
        except Exception as e:
            logger.error(f"停止失败: {e}")
    
    def seek(self, position: float) -> bool:
        """
        跳转到指定位置
        
        注意: pygame.mixer不支持精确seek，此方法仅返回当前状态
        
        Args:
            position: 目标位置（秒）
            
        Returns:
            是否成功跳转
        """
        # pygame.mixer.music不支持seek操作
        logger.warning("pygame.mixer不支持seek操作")
        return False
    
    def set_volume(self, volume: float) -> None:
        """
        设置播放音量
        
        Args:
            volume: 音量 (0.0 - 1.0)
        """
        pygame.mixer.music.set_volume(max(0.0, min(1.0, volume)))
    
    def get_volume(self) -> float:
        """获取当前音量 (0.0 - 1.0)"""
        return pygame.mixer.music.get_volume()
    
    def _set_state(self, state: PlaybackState) -> None:
        """设置状态并触发回调"""
        if self._state != state:
            self._state = state
            if self._on_state_change:
                try:
                    self._on_state_change(state)
                except Exception as e:
                    logger.error(f"状态回调执行失败: {e}")
    
    def _start_check_thread(self) -> None:
        """启动播放完成检查线程"""
        import threading
        
        self._stop_check = False
        
        def _check():
            while not self._stop_check:
                if self._state == PlaybackState.PLAYING:
                    if not pygame.mixer.music.get_busy():
                        # 播放完成
                        self._set_state(PlaybackState.STOPPED)
                        if self._on_complete:
                            try:
                                self._on_complete()
                            except Exception as e:
                                logger.error(f"完成回调执行失败: {e}")
                        break
                time.sleep(0.1)
        
        thread = threading.Thread(target=_check, daemon=True)
        thread.start()
    
    def cleanup(self) -> None:
        """清理资源"""
        self.stop()
        if self._current_file and os.path.exists(self._current_file):
            try:
                # 如果是临时文件，删除它
                if self._current_file.startswith(tempfile.gettempdir()):
                    os.remove(self._current_file)
            except Exception:
                pass
        self._current_file = None


# 导入tempfile用于cleanup
import tempfile
