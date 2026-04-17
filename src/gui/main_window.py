"""
主窗口模块 - 应用主界面
"""

import tkinter as tk
from tkinter import ttk
import logging
import shutil
import os
from typing import Optional

from ..tts.voice_manager import VoiceManager, Voice
from ..tts.generator import TTSGenerator, TTSOptions
from ..tts.player import AudioPlayer, PlaybackState
from ..config.settings import Settings
from .widgets.text_panel import TextPanel
from .widgets.control_panel import ControlPanel
from . import dialogs

logger = logging.getLogger(__name__)


class MainWindow:
    """
    主窗口 - 应用的主界面
    
    功能:
    - 组装文本面板和控制面板
    - 协调各模块交互
    - 处理用户操作
    """
    
    def __init__(self, root: tk.Tk):
        """
        初始化主窗口
        
        Args:
            root: Tk根窗口
        """
        self._root = root
        
        # 初始化核心模块
        self._settings = Settings()
        self._voice_manager = VoiceManager()
        self._generator = TTSGenerator()
        self._player = AudioPlayer()
        
        # 当前状态
        self._current_audio: Optional[str] = None
        self._pending_save_path: Optional[str] = None
        
        # 配置窗口
        self._setup_window()
        
        # 创建UI组件
        self._create_widgets()
        
        # 设置播放器回调
        self._player.set_callbacks(
            on_state_change=self._on_playback_state_change,
            on_complete=self._on_playback_complete
        )
        
        # 加载语音
        self._load_voices()
    
    def _setup_window(self) -> None:
        """配置窗口"""
        self._root.title("文本转语音转换器")
        
        # 从设置加载窗口大小
        width = self._settings.get("window_width", 800)
        height = self._settings.get("window_height", 600)
        self._root.geometry(f"{width}x{height}")
        self._root.minsize(600, 400)
        
        # 窗口关闭事件
        self._root.protocol("WM_DELETE_WINDOW", self._on_window_close)
    
    def _create_widgets(self) -> None:
        """创建UI组件"""
        # 配置根网格
        self._root.columnconfigure(0, weight=3)
        self._root.columnconfigure(1, weight=1)
        self._root.rowconfigure(0, weight=1)
        
        # 左侧：文本输入面板
        self._text_panel = TextPanel(
            self._root,
            initial_text="123456，你好测试一下",
            padding="10"
        )
        self._text_panel.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 右侧：控制面板
        self._control_panel = ControlPanel(
            self._root,
            voice_manager=self._voice_manager,
            on_play=self._handle_play,
            on_stop=self._handle_stop,
            on_save=self._handle_save,
            on_voice_change=self._on_voice_change,
            padding="10"
        )
        self._control_panel.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    def _load_voices(self) -> None:
        """加载语音列表"""
        self._control_panel.set_status("正在加载语音...")
        self._control_panel.start_loading()
        
        def on_voices_loaded(voices):
            self._root.after(0, self._on_voices_loaded, voices)
        
        self._voice_manager.load_voices_async(callback=on_voices_loaded)
    
    def _on_voices_loaded(self, voices) -> None:
        """语音加载完成回调"""
        self._control_panel.stop_loading()
        self._control_panel.update_voices(voices)
        self._control_panel.set_status(f"已加载 {len(voices)} 个语音")
    
    def _handle_play(self) -> None:
        """处理播放操作"""
        text = self._text_panel.text
        if not text:
            dialogs.show_warning(self._root, "警告", "请输入要转换的文本")
            return
        
        voice = self._control_panel.current_voice
        if not voice:
            dialogs.show_warning(self._root, "警告", "请选择一个语音")
            return
        
        # 生成语音
        self._control_panel.set_status("正在生成语音...")
        self._control_panel.set_controls_enabled(False)
        
        options = self._control_panel.tts_options
        
        self._generator.generate(
            text=text,
            voice=voice,
            options=options,
            on_complete=lambda path: self._root.after(0, self._on_generate_complete, path, True),
            on_error=lambda e: self._root.after(0, self._on_generate_error, e)
        )
    
    def _handle_stop(self) -> None:
        """处理停止操作"""
        self._player.stop()
    
    def _handle_save(self) -> None:
        """处理保存操作"""
        text = self._text_panel.text
        if not text:
            dialogs.show_warning(self._root, "警告", "请输入要转换的文本")
            return
        
        voice = self._control_panel.current_voice
        if not voice:
            dialogs.show_warning(self._root, "警告", "请选择一个语音")
            return
        
        # 选择保存位置
        save_path = dialogs.show_save_dialog(self._root)
        if not save_path:
            return
        
        self._pending_save_path = save_path
        
        # 生成语音
        self._control_panel.set_status("正在生成语音...")
        self._control_panel.set_controls_enabled(False)
        
        options = self._control_panel.tts_options
        
        self._generator.generate(
            text=text,
            voice=voice,
            options=options,
            on_complete=lambda path: self._root.after(0, self._on_generate_complete, path, False),
            on_error=lambda e: self._root.after(0, self._on_generate_error, e)
        )
    
    def _on_generate_complete(self, audio_path: str, play_immediately: bool) -> None:
        """生成完成回调"""
        self._current_audio = audio_path
        self._control_panel.set_controls_enabled(True)
        
        if play_immediately:
            # 立即播放
            self._player.play(audio_path)
            self._control_panel.set_status("正在播放...")
        else:
            # 保存到指定位置
            if self._pending_save_path:
                try:
                    shutil.copy2(audio_path, self._pending_save_path)
                    self._control_panel.set_status(f"已保存: {self._pending_save_path}")
                    dialogs.show_info(
                        self._root,
                        "成功",
                        f"音频已保存到:\n{self._pending_save_path}"
                    )
                except Exception as e:
                    logger.error(f"保存失败: {e}")
                    dialogs.show_error(self._root, "错误", f"保存失败: {e}")
                finally:
                    self._pending_save_path = None
    
    def _on_generate_error(self, error: Exception) -> None:
        """生成错误回调"""
        logger.error(f"生成失败: {error}")
        self._control_panel.set_controls_enabled(True)
        self._control_panel.set_status("生成失败")
        dialogs.show_error(self._root, "错误", f"生成语音失败: {error}")
    
    def _on_voice_change(self, voice: Voice) -> None:
        """语音变化回调"""
        logger.info(f"语音已切换: {voice.short_name}")
    
    def _on_playback_state_change(self, state: PlaybackState) -> None:
        """播放状态变化回调"""
        self._control_panel.set_playing_state(state)
        
        if state == PlaybackState.PLAYING:
            self._control_panel.set_status("正在播放...")
        elif state == PlaybackState.PAUSED:
            self._control_panel.set_status("已暂停")
        else:
            self._control_panel.set_status("就绪")
    
    def _on_playback_complete(self) -> None:
        """播放完成回调"""
        self._control_panel.set_status("播放完成")
    
    def _on_window_close(self) -> None:
        """窗口关闭处理"""
        # 保存设置
        width = self._root.winfo_width()
        height = self._root.winfo_height()
        self._settings.set("window_width", width)
        self._settings.set("window_height", height)
        self._settings.save()
        
        # 清理资源
        self._player.cleanup()
        
        # 关闭窗口
        self._root.destroy()
    
    def run(self) -> None:
        """运行应用"""
        self._root.mainloop()
