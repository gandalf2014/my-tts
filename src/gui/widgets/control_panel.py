"""
控制面板组件 - 右侧控制区域
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable, List, Dict, Any
from dataclasses import dataclass

from ...tts.voice_manager import Voice, VoiceManager
from ...tts.generator import TTSOptions
from ...tts.player import PlaybackState


@dataclass
class ControlState:
    """控制面板状态"""
    language: str = ""
    voice_display_name: str = ""
    speed: float = 1.0
    pitch: float = 1.0
    volume: float = 100.0


class ControlPanel(ttk.Frame):
    """
    控制面板 - 右侧控制区域
    
    功能:
    - 语言选择
    - 语音选择
    - 参数调节（语速、音调、音量）
    - 播放控制按钮
    - 进度显示
    """
    
    def __init__(
        self,
        parent: tk.Widget,
        voice_manager: VoiceManager,
        on_play: Optional[Callable[[], None]] = None,
        on_stop: Optional[Callable[[], None]] = None,
        on_save: Optional[Callable[[], None]] = None,
        on_voice_change: Optional[Callable[[Voice], None]] = None,
        on_param_change: Optional[Callable[[TTSOptions], None]] = None,
        **kwargs
    ):
        """
        初始化控制面板
        
        Args:
            parent: 父组件
            voice_manager: 语音管理器
            on_play: 播放回调
            on_stop: 停止回调
            on_save: 保存回调
            on_voice_change: 语音变化回调
            on_param_change: 参数变化回调
        """
        super().__init__(parent, **kwargs)
        
        self._voice_manager = voice_manager
        self._on_play = on_play
        self._on_stop = on_stop
        self._on_save = on_save
        self._on_voice_change = on_voice_change
        self._on_param_change = on_param_change
        
        self._voices: List[Voice] = []
        self._current_voice: Optional[Voice] = None
        self._is_playing = False
        self._is_paused = False
        
        # 参数状态
        self._speed_var = tk.DoubleVar(value=1.0)
        self._pitch_var = tk.DoubleVar(value=1.0)
        self._volume_var = tk.DoubleVar(value=100.0)
        
        # 构建UI
        self._create_widgets()
    
    def _create_widgets(self) -> None:
        """创建控件"""
        # 配置网格
        self.columnconfigure(1, weight=1)
        
        row = 0
        
        # 语言选择
        ttk.Label(self, text="语言", font=("Microsoft YaHei", 10)).grid(
            row=row, column=0, sticky=tk.W, pady=(0, 5)
        )
        row += 1
        
        self._language_var = tk.StringVar()
        self._language_combo = ttk.Combobox(
            self,
            textvariable=self._language_var,
            state="readonly",
            width=20
        )
        self._language_combo.grid(
            row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15)
        )
        self._language_combo.bind('<<ComboboxSelected>>', self._on_language_selected)
        row += 1
        
        # 语音选择
        ttk.Label(self, text="语音", font=("Microsoft YaHei", 10)).grid(
            row=row, column=0, sticky=tk.W, pady=(0, 5)
        )
        row += 1
        
        self._voice_var = tk.StringVar()
        self._voice_combo = ttk.Combobox(
            self,
            textvariable=self._voice_var,
            state="readonly",
            width=20
        )
        self._voice_combo.grid(
            row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15)
        )
        self._voice_combo.bind('<<ComboboxSelected>>', self._on_voice_selected)
        row += 1
        
        # 语音风格（暂保留，未来扩展）
        ttk.Label(self, text="语音风格", font=("Microsoft YaHei", 10)).grid(
            row=row, column=0, sticky=tk.W, pady=(0, 5)
        )
        row += 1
        
        self._style_var = tk.StringVar(value="默认")
        self._style_combo = ttk.Combobox(
            self,
            textvariable=self._style_var,
            state="readonly",
            width=20,
            values=["默认"]
        )
        self._style_combo.grid(
            row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15)
        )
        row += 1
        
        # 语速控制
        self._speed_label = ttk.Label(
            self, text="语速: 1.0x", font=("Microsoft YaHei", 10)
        )
        self._speed_label.grid(row=row, column=0, sticky=tk.W, pady=(0, 5))
        row += 1
        
        self._speed_scale = ttk.Scale(
            self,
            from_=0.5,
            to=2.0,
            variable=self._speed_var,
            orient=tk.HORIZONTAL,
            command=self._on_speed_change
        )
        self._speed_scale.grid(
            row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15)
        )
        row += 1
        
        # 音调控制
        self._pitch_label = ttk.Label(
            self, text="音调: 1.0", font=("Microsoft YaHei", 10)
        )
        self._pitch_label.grid(row=row, column=0, sticky=tk.W, pady=(0, 5))
        row += 1
        
        self._pitch_scale = ttk.Scale(
            self,
            from_=0.5,
            to=2.0,
            variable=self._pitch_var,
            orient=tk.HORIZONTAL,
            command=self._on_pitch_change
        )
        self._pitch_scale.grid(
            row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15)
        )
        row += 1
        
        # 音量控制
        self._volume_label = ttk.Label(
            self, text="音量: 100%", font=("Microsoft YaHei", 10)
        )
        self._volume_label.grid(row=row, column=0, sticky=tk.W, pady=(0, 5))
        row += 1
        
        self._volume_scale = ttk.Scale(
            self,
            from_=0,
            to=100,
            variable=self._volume_var,
            orient=tk.HORIZONTAL,
            command=self._on_volume_change
        )
        self._volume_scale.grid(
            row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15)
        )
        row += 1
        
        # 进度显示
        self._progress_label = ttk.Label(
            self, text="进度: 00:00:00 / 00:00:00", font=("Microsoft YaHei", 10)
        )
        self._progress_label.grid(
            row=row, column=0, columnspan=2, sticky=tk.W, pady=(0, 5)
        )
        row += 1
        
        self._progress_bar = ttk.Progressbar(self, mode='determinate')
        self._progress_bar.grid(
            row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20)
        )
        row += 1
        
        # 控制按钮
        button_frame = ttk.Frame(self)
        button_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E))
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        
        self._play_btn = ttk.Button(
            button_frame, text="试听", command=self._handle_play_click
        )
        self._play_btn.grid(row=0, column=0, padx=(0, 5), sticky=(tk.W, tk.E))
        
        self._save_btn = ttk.Button(
            button_frame, text="保存", command=self._handle_save_click
        )
        self._save_btn.grid(row=0, column=1, padx=(5, 0), sticky=(tk.W, tk.E))
        row += 1
        
        # 状态标签
        self._status_var = tk.StringVar(value="就绪")
        status_label = ttk.Label(
            self, textvariable=self._status_var, font=("Microsoft YaHei", 9)
        )
        status_label.grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=(10, 0))
    
    def update_voices(self, voices: List[Voice]) -> None:
        """
        更新语音列表
        
        Args:
            voices: Voice对象列表
        """
        self._voices = voices
        
        # 更新语言列表
        languages = self._voice_manager.get_languages()
        self._language_combo['values'] = languages
        
        # 默认选择中文
        if '中文 (所有地区)' in languages:
            self._language_var.set('中文 (所有地区)')
        elif languages:
            self._language_var.set(languages[0])
        
        self._update_voice_list()
    
    def _update_voice_list(self) -> None:
        """根据当前语言更新语音列表"""
        language = self._language_var.get()
        if not language:
            return
        
        filtered_voices = self._voice_manager.filter_by_language(language)
        
        # 生成显示名称
        display_names = [
            self._voice_manager.get_display_name(v) for v in filtered_voices
        ]
        
        # 中文语音排序
        if language == "中文 (所有地区)":
            display_names = self._voice_manager.sort_chinese_voices(display_names)
        
        self._voice_combo['values'] = display_names
        
        if display_names:
            self._voice_var.set(display_names[0])
            self._on_voice_selected(None)
    
    def _on_language_selected(self, event) -> None:
        """语言选择变化处理"""
        self._update_voice_list()
    
    def _on_voice_selected(self, event) -> None:
        """语音选择变化处理"""
        display_name = self._voice_var.get()
        language = self._language_var.get()
        
        self._current_voice = self._voice_manager.get_voice_by_display_name(
            display_name, language
        )
        
        if self._on_voice_change and self._current_voice:
            self._on_voice_change(self._current_voice)
    
    def _on_speed_change(self, value) -> None:
        """语速变化处理"""
        speed = float(value)
        self._speed_label.config(text=f"语速: {speed:.1f}x")
        self._notify_param_change()
    
    def _on_pitch_change(self, value) -> None:
        """音调变化处理"""
        pitch = float(value)
        self._pitch_label.config(text=f"音调: {pitch:.1f}")
        self._notify_param_change()
    
    def _on_volume_change(self, value) -> None:
        """音量变化处理"""
        volume = int(float(value))
        self._volume_label.config(text=f"音量: {volume}%")
        self._notify_param_change()
    
    def _notify_param_change(self) -> None:
        """通知参数变化"""
        if self._on_param_change:
            from ...tts.generator import create_tts_options
            options = create_tts_options(
                speed=self._speed_var.get(),
                pitch=self._pitch_var.get(),
                volume=self._volume_var.get()
            )
            self._on_param_change(options)
    
    def _handle_play_click(self) -> None:
        """播放按钮点击处理"""
        if self._is_playing and not self._is_paused:
            # 正在播放 → 停止
            if self._on_stop:
                self._on_stop()
        else:
            # 未播放或已暂停 → 播放
            if self._on_play:
                self._on_play()
    
    def _handle_save_click(self) -> None:
        """保存按钮点击处理"""
        if self._on_save:
            self._on_save()
    
    @property
    def current_voice(self) -> Optional[Voice]:
        """当前选择的语音"""
        return self._current_voice
    
    @property
    def tts_options(self) -> 'TTSOptions':
        """当前TTS参数"""
        from ...tts.generator import create_tts_options
        return create_tts_options(
            speed=self._speed_var.get(),
            pitch=self._pitch_var.get(),
            volume=self._volume_var.get()
        )
    
    def set_playing_state(self, state: PlaybackState) -> None:
        """设置播放状态"""
        if state == PlaybackState.PLAYING:
            self._is_playing = True
            self._is_paused = False
            self._play_btn.config(text="停止")
        elif state == PlaybackState.PAUSED:
            self._is_paused = True
            self._play_btn.config(text="继续")
        else:  # STOPPED
            self._is_playing = False
            self._is_paused = False
            self._play_btn.config(text="试听")
    
    def set_status(self, status: str) -> None:
        """设置状态文本"""
        self._status_var.set(status)
    
    def set_progress(self, current: float, total: float) -> None:
        """设置进度"""
        if total > 0:
            progress_percent = (current / total) * 100
            self._progress_bar['value'] = progress_percent
            
            # 格式化时间
            current_str = self._format_time(current)
            total_str = self._format_time(total)
            self._progress_label.config(text=f"进度: {current_str} / {total_str}")
    
    @staticmethod
    def _format_time(seconds: float) -> str:
        """格式化时间为 HH:MM:SS"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    
    def start_loading(self) -> None:
        """开始加载状态"""
        self._progress_bar.config(mode='indeterminate')
        self._progress_bar.start()
    
    def stop_loading(self) -> None:
        """停止加载状态"""
        self._progress_bar.stop()
        self._progress_bar.config(mode='determinate')
        self._progress_bar['value'] = 0
    
    def set_controls_enabled(self, enabled: bool) -> None:
        """启用/禁用控件"""
        state = tk.NORMAL if enabled else tk.DISABLED
        self._play_btn.config(state=state)
        self._save_btn.config(state=state)
