"""
主窗口模块 - 应用主窗口和协调逻辑
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import logging
import os
from typing import Optional

from .widgets.text_panel import TextPanel
from .widgets.control_panel import ControlPanel
from ..tts.voice_manager import VoiceManager
from ..tts.generator import TTSGenerator, TTSOptions
from ..tts.player import AudioPlayer, PlaybackState
from ..config.settings import Settings

logger = logging.getLogger(__name__)


class MainWindow:
    """
    主窗口 - 协调所有组件和业务逻辑
    
    职责:
    - 创建和布局UI组件
    - 协调模块间通信
    - 处理用户操作
    - 管理应用状态
    """
    
    def __init__(self, root: Optional[tk.Tk] = None):
        """
        初始化主窗口
        
        Args:
            root: Tkinter根窗口，如果为None则创建新窗口
        """
        # 创建或使用现有的根窗口
        if root is None:
            self._root = tk.Tk()
        else:
            self._root = root
        
        # 初始化模块
        self._settings = Settings()
        self._voice_manager = VoiceManager()
        self._tts_generator = TTSGenerator()
        self._audio_player = AudioPlayer()
        
        # 当前状态
        self._current_voice = None
        self._current_audio_file: Optional[str] = None
        self._is_generating = False
        
        # 设置窗口属性
        self._setup_window()
        
        # 创建UI组件
        self._create_widgets()
        
        # 连接信号和回调
        self._connect_signals()
        
        # 加载语音
        self._load_voices()
        
        logger.info("MainWindow 初始化完成")
    
    def _setup_window(self) -> None:
        """设置窗口属性"""
        self._root.title("文本转语音转换器")
        
        # 从设置恢复窗口大小
        width = self._settings.get("window_width", 800)
        height = self._settings.get("window_height", 600)
        self._root.geometry(f"{width}x{height}")
        self._root.minsize(600, 400)
        
        # 窗口关闭事件
        self._root.protocol("WM_DELETE_WINDOW", self._on_close)
        
        logger.debug(f"窗口设置完成: {width}x{height}")
    
    def _create_widgets(self) -> None:
        """创建UI组件"""
        # 配置根窗口网格
        self._root.columnconfigure(0, weight=3)  # 左侧文本区域
        self._root.columnconfigure(1, weight=1)  # 右侧控制面板
        self._root.rowconfigure(0, weight=1)
        
        # 左侧：文本输入面板
        self._text_panel = TextPanel(
            self._root,
            initial_text="123456，你好测试一下"
        )
        self._text_panel.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=10)
        
        # 右侧：控制面板
        self._control_panel = ControlPanel(
            self._root,
            voice_manager=self._voice_manager,
            on_play=self._handle_play,
            on_stop=self._handle_stop,
            on_save=self._handle_save,
            on_voice_change=self._handle_voice_change,
            on_param_change=self._handle_param_change
        )
        self._control_panel.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=10)
        
        logger.debug("UI组件创建完成")
    
    def _connect_signals(self) -> None:
        """连接信号和回调"""
        # 播放器状态变化回调
        self._audio_player.set_callbacks(
            on_state_change=self._on_playback_state_change,
            on_complete=self._on_playback_complete
        )
        
        logger.debug("信号连接完成")
    
    def _load_voices(self) -> None:
        """异步加载语音列表"""
        self._control_panel.set_status("正在加载语音...")
        self._control_panel.start_loading()
        
        def on_voices_loaded(voices):
            self._control_panel.stop_loading()
            self._control_panel.update_voices(voices)
            self._control_panel.set_status(f"已加载 {len(voices)} 个语音")
            
            # 恢复上次选择的语音
            self._restore_voice_selection()
        
        self._voice_manager.load_voices_async(callback=on_voices_loaded)
        
        logger.info("开始异步加载语音")
    
    def _restore_voice_selection(self) -> None:
        """恢复上次选择的语音"""
        # TODO: 从设置中恢复语音选择
        pass
    
    def _handle_play(self) -> None:
        """处理播放按钮点击"""
        # 如果正在生成，忽略
        if self._is_generating:
            return
        
        # 获取文本
        text = self._text_panel.text
        if not text:
            messagebox.showwarning("警告", "请在左侧文本框中输入要转换的文本。")
            return
        
        # 获取语音
        voice = self._control_panel.current_voice
        if not voice:
            messagebox.showwarning("警告", "请选择一个语音。")
            return
        
        # 生成并播放
        self._generate_and_play(text, voice)
    
    def _handle_stop(self) -> None:
        """处理停止按钮点击"""
        self._audio_player.stop()
    
    def _handle_save(self) -> None:
        """处理保存按钮点击"""
        # 获取文本
        text = self._text_panel.text
        if not text:
            messagebox.showwarning("警告", "请在左侧文本框中输入要转换的文本。")
            return
        
        # 获取语音
        voice = self._control_panel.current_voice
        if not voice:
            messagebox.showwarning("警告", "请选择一个语音。")
            return
        
        # 选择保存位置
        file_path = filedialog.asksaveasfilename(
            defaultextension=".mp3",
            filetypes=[("MP3 文件", "*.mp3"), ("所有文件", "*.*")],
            title="保存音频文件"
        )
        
        if not file_path:
            return
        
        # 生成并保存
        self._generate_and_save(text, voice, file_path)
    
    def _handle_voice_change(self, voice) -> None:
        """处理语音选择变化"""
        self._current_voice = voice
        logger.debug(f"当前语音: {voice.short_name if voice else 'None'}")
    
    def _handle_param_change(self, options: TTSOptions) -> None:
        """处理参数变化"""
        # 参数变化时的处理（可选）
        logger.debug(f"参数变化: speed={options.speed}, pitch={options.pitch}, volume={options.volume}")
    
    def _generate_and_play(self, text: str, voice) -> None:
        """生成语音并播放"""
        self._is_generating = True
        self._control_panel.set_status("正在生成语音...")
        self._control_panel.start_loading()
        self._control_panel.set_controls_enabled(False)
        
        def on_complete(audio_path: str):
            self._is_generating = False
            self._current_audio_file = audio_path
            self._control_panel.stop_loading()
            self._control_panel.set_controls_enabled(True)
            self._control_panel.set_status("语音生成成功！")
            
            # 自动播放
            self._play_audio(audio_path)
        
        def on_error(error: Exception):
            self._is_generating = False
            self._control_panel.stop_loading()
            self._control_panel.set_controls_enabled(True)
            self._control_panel.set_status("生成失败")
            messagebox.showerror("错误", f"生成语音失败: {str(error)}")
        
        self._tts_generator.generate(
            text=text,
            voice=voice,
            options=self._control_panel.tts_options,
            on_complete=on_complete,
            on_error=on_error
        )
    
    def _generate_and_save(self, text: str, voice, output_path: str) -> None:
        """生成语音并保存"""
        self._is_generating = True
        self._control_panel.set_status("正在生成语音...")
        self._control_panel.start_loading()
        self._control_panel.set_controls_enabled(False)
        
        def on_complete(audio_path: str):
            self._is_generating = False
            self._current_audio_file = audio_path
            
            # 复制到目标位置
            import shutil
            shutil.copy2(audio_path, output_path)
            
            self._control_panel.stop_loading()
            self._control_panel.set_controls_enabled(True)
            self._control_panel.set_status(f"音频已保存到: {output_path}")
            messagebox.showinfo("成功", f"音频已成功保存到:\n{output_path}")
        
        def on_error(error: Exception):
            self._is_generating = False
            self._control_panel.stop_loading()
            self._control_panel.set_controls_enabled(True)
            self._control_panel.set_status("保存失败")
            messagebox.showerror("错误", f"保存音频失败: {str(error)}")
        
        self._tts_generator.generate(
            text=text,
            voice=voice,
            output_path=output_path,
            options=self._control_panel.tts_options,
            on_complete=on_complete,
            on_error=on_error
        )
    
    def _play_audio(self, audio_path: str) -> None:
        """播放音频文件"""
        try:
            self._audio_player.play(audio_path)
            self._control_panel.set_status("正在播放音频...")
        except Exception as e:
            logger.error(f"播放失败: {e}")
            messagebox.showerror("错误", f"播放音频失败: {str(e)}")
    
    def _on_playback_state_change(self, state: PlaybackState) -> None:
        """播放状态变化回调"""
        self._control_panel.set_playing_state(state)
        
        if state == PlaybackState.PLAYING:
            # 开始播放进度检查
            self._check_playback_progress()
    
    def _on_playback_complete(self) -> None:
        """播放完成回调"""
        self._control_panel.set_status("播放完成。")
    
    def _check_playback_progress(self) -> None:
        """检查播放进度"""
        if self._audio_player.is_playing():
            # 更新进度（如果实现了进度跟踪）
            # 这里暂时只是检查播放是否结束
            self._root.after(100, self._check_playback_progress)
        elif not self._audio_player.is_paused():
            # 播放结束
            pass
    
    def _on_close(self) -> None:
        """窗口关闭处理"""
        # 保存设置
        self._settings.set("window_width", self._root.winfo_width())
        self._settings.set("window_height", self._root.winfo_height())
        self._settings.save()
        
        # 清理资源
        self._audio_player.cleanup()
        
        logger.info("应用关闭")
        
        # 销毁窗口
        self._root.destroy()
    
    def run(self) -> None:
        """运行应用主循环"""
        logger.info("启动应用主循环")
        self._root.mainloop()
    
    @property
    def root(self) -> tk.Tk:
        """获取根窗口"""
        return self._root
