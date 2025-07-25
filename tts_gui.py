#!/usr/bin/env python3
"""
Text-to-Speech GUI Application using edge-tts
Author: AI Assistant
Description: A GUI application for converting text to speech with multiple voice options
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import asyncio
import threading
import edge_tts
import os
import tempfile
import pygame
from typing import List, Dict, Optional


class TTSApp:
    def __init__(self, root):
        self.root = root
        self.root.title("文本转语音转换器")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)
        
        # Initialize pygame mixer for audio playback
        pygame.mixer.init()
        
        # Variables
        self.voices: List[Dict] = []
        self.current_audio_file: Optional[str] = None
        self.is_playing = False
        
        # Create GUI
        self.create_widgets()
        
        # Load voices in background
        self.load_voices_async()

        # Store labels for dynamic updates
        self.speed_label = None
        self.pitch_label = None
        self.volume_label = None
    
    def create_widgets(self):
        """Create and arrange GUI widgets"""
        # Configure root grid
        self.root.columnconfigure(0, weight=3)  # Left side (text area) gets more space
        self.root.columnconfigure(1, weight=1)  # Right side (controls)
        self.root.rowconfigure(0, weight=1)

        # Left frame for text input
        left_frame = ttk.Frame(self.root, padding="10")
        left_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        left_frame.columnconfigure(0, weight=1)
        left_frame.rowconfigure(0, weight=1)

        # Text input area
        self.text_input = scrolledtext.ScrolledText(left_frame, font=("Microsoft YaHei", 12))
        self.text_input.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.text_input.insert("1.0", "123456，你好测试一下")

        # Right frame for controls
        right_frame = ttk.Frame(self.root, padding="10")
        right_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        right_frame.columnconfigure(1, weight=1)

        # Language selection
        ttk.Label(right_frame, text="语言", font=("Microsoft YaHei", 10)).grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.language_var = tk.StringVar()
        self.language_combo = ttk.Combobox(right_frame, textvariable=self.language_var,
                                          state="readonly", width=20)
        self.language_combo.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        self.language_combo.bind('<<ComboboxSelected>>', self.on_language_change)

        # Voice selection
        ttk.Label(right_frame, text="语音", font=("Microsoft YaHei", 10)).grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        self.voice_var = tk.StringVar()
        self.voice_combo = ttk.Combobox(right_frame, textvariable=self.voice_var,
                                       state="readonly", width=20)
        self.voice_combo.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))

        # Voice style selection
        ttk.Label(right_frame, text="语音风格", font=("Microsoft YaHei", 10)).grid(row=4, column=0, sticky=tk.W, pady=(0, 5))
        self.style_var = tk.StringVar()
        self.style_combo = ttk.Combobox(right_frame, textvariable=self.style_var,
                                       state="readonly", width=20, values=["默认"])
        self.style_combo.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        self.style_combo.set("默认")

        # Speed control (暂时保留界面，但不影响语音生成)
        self.speed_label = ttk.Label(right_frame, text="语速: 1 (暂不可用)", font=("Microsoft YaHei", 10))
        self.speed_label.grid(row=6, column=0, sticky=tk.W, pady=(0, 5))
        self.speed_var = tk.DoubleVar(value=1.0)
        self.speed_scale = ttk.Scale(right_frame, from_=0.5, to=2.0, variable=self.speed_var,
                                    orient=tk.HORIZONTAL, command=self.update_speed_label, state="disabled")
        self.speed_scale.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))

        # Pitch control (暂时保留界面，但不影响语音生成)
        self.pitch_label = ttk.Label(right_frame, text="音调: 1 (暂不可用)", font=("Microsoft YaHei", 10))
        self.pitch_label.grid(row=8, column=0, sticky=tk.W, pady=(0, 5))
        self.pitch_var = tk.DoubleVar(value=1.0)
        self.pitch_scale = ttk.Scale(right_frame, from_=0.5, to=2.0, variable=self.pitch_var,
                                    orient=tk.HORIZONTAL, command=self.update_pitch_label, state="disabled")
        self.pitch_scale.grid(row=9, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))

        # Volume control (暂时保留界面，但不影响语音生成)
        self.volume_label = ttk.Label(right_frame, text="音量: 100 (暂不可用)", font=("Microsoft YaHei", 10))
        self.volume_label.grid(row=10, column=0, sticky=tk.W, pady=(0, 5))
        self.volume_var = tk.DoubleVar(value=100.0)
        self.volume_scale = ttk.Scale(right_frame, from_=0, to=100, variable=self.volume_var,
                                     orient=tk.HORIZONTAL, command=self.update_volume_label, state="disabled")
        self.volume_scale.grid(row=11, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))

        # Progress display
        ttk.Label(right_frame, text="进度: 00:00:00 / 00:00:00", font=("Microsoft YaHei", 10)).grid(row=12, column=0, columnspan=2, sticky=tk.W, pady=(0, 5))
        self.progress = ttk.Progressbar(right_frame, mode='determinate')
        self.progress.grid(row=13, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))

        # Control buttons
        button_frame = ttk.Frame(right_frame)
        button_frame.grid(row=14, column=0, columnspan=2, sticky=(tk.W, tk.E))
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)

        self.play_btn = ttk.Button(button_frame, text="试听", command=self.generate_and_play)
        self.play_btn.grid(row=0, column=0, padx=(0, 5), sticky=(tk.W, tk.E))

        self.save_btn = ttk.Button(button_frame, text="保存", command=self.save_audio)
        self.save_btn.grid(row=0, column=1, padx=(5, 0), sticky=(tk.W, tk.E))

        # Status label
        self.status_var = tk.StringVar()
        self.status_var.set("就绪")
        status_label = ttk.Label(right_frame, textvariable=self.status_var, font=("Microsoft YaHei", 9))
        status_label.grid(row=15, column=0, columnspan=2, sticky=tk.W, pady=(10, 0))
    
    def load_voices_async(self):
        """Load voices in a separate thread"""
        def load_voices():
            try:
                self.status_var.set("正在加载语音...")
                self.progress.start()
                
                # Run async function in thread
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                voices = loop.run_until_complete(edge_tts.list_voices())
                loop.close()
                
                # Update GUI in main thread
                self.root.after(0, self.update_voices, voices)
                
            except Exception as e:
                self.root.after(0, self.show_error, f"加载语音失败: {str(e)}")
        
        thread = threading.Thread(target=load_voices, daemon=True)
        thread.start()

    def update_speed_label(self, value):
        """Update speed label when slider changes"""
        if self.speed_label:
            self.speed_label.config(text=f"语速: {float(value):.1f}")

    def update_pitch_label(self, value):
        """Update pitch label when slider changes"""
        if self.pitch_label:
            self.pitch_label.config(text=f"音调: {float(value):.1f}")

    def update_volume_label(self, value):
        """Update volume label when slider changes"""
        if self.volume_label:
            self.volume_label.config(text=f"音量: {int(float(value))}")
    
    def update_voices(self, voices):
        """Update voice selection widgets with loaded voices"""
        self.voices = voices
        self.progress.stop()
        
        # Group voices by language
        languages = {}
        for voice in voices:
            locale = voice['Locale']
            if locale not in languages:
                languages[locale] = []
            languages[locale].append(voice)
        
        # Create language options with Chinese regions combined
        language_options = []
        chinese_locales = []

        for locale in sorted(languages.keys()):
            if locale.startswith('zh-'):
                chinese_locales.append(locale)
            else:
                # Add other languages
                language_options.append(locale)

        # Add combined Chinese option at the beginning
        if chinese_locales:
            language_options.insert(0, '中文 (所有地区)')

        self.language_combo['values'] = language_options

        # Set default to Chinese (all regions)
        if '中文 (所有地区)' in language_options:
            self.language_var.set('中文 (所有地区)')
        elif 'zh-CN' in language_options:
            self.language_var.set('zh-CN')
        elif 'en-US' in language_options:
            self.language_var.set('en-US')
        elif language_options:
            self.language_var.set(language_options[0])

        # Store Chinese locales for later use
        self.chinese_locales = chinese_locales

        self.on_language_change()
        self.status_var.set(f"已加载 {len(voices)} 个语音")
    
    def on_language_change(self, event=None):
        """Handle language selection change"""
        selected_language = self.language_var.get()
        if not selected_language:
            return

        # Filter voices by selected language
        if selected_language == '中文 (所有地区)':
            # Show all Chinese voices from all regions
            language_voices = [v for v in self.voices if v['Locale'].startswith('zh-')]
        else:
            # Show voices for specific language
            language_voices = [v for v in self.voices if v['Locale'] == selected_language]

        # Create voice display names with simplified format
        voice_options = []
        for voice in language_voices:
            # Extract the voice name from ShortName
            short_name = voice['ShortName']
            if '-' in short_name:
                voice_name = short_name.split('-')[-1].replace('Neural', '')
            else:
                voice_name = voice['FriendlyName'].split(' ')[1] if ' ' in voice['FriendlyName'] else voice['FriendlyName']

            # Create display format like "晓萱 / Xiaoxuan" for Chinese voices
            if voice['Locale'].startswith('zh-'):
                chinese_name = self.get_chinese_name(voice_name)
                display_name = f"{chinese_name} / {voice_name}"
            else:
                # For non-Chinese voices, use original format
                display_name = f"{voice['FriendlyName']} ({voice['Gender']})"

            voice_options.append(display_name)

        # Sort Chinese voices to match the desired order
        if selected_language == '中文 (所有地区)':
            voice_options = self.sort_chinese_voices(voice_options)

        # Update voice combobox
        self.voice_combo['values'] = voice_options
        if voice_options:
            self.voice_var.set(voice_options[0])

    def sort_chinese_voices(self, voice_options):
        """Sort Chinese voices in a preferred order"""
        # Define preferred order based on the image
        preferred_order = [
            '晓萱 / Xiaoxuan', '晓辰 / Xiaochen', '晓晓 / Xiaoxiao', '晓涵 / Xiaohan',
            '云健 / Yunjian', '晓燕 / Xiaoyan', '云浩 / Yunhao', '晓双 / Xiaoshuang',
            '晓梦 / Xiaomeng', '云峰 / Yunfeng', '云泽 / Yunze', '晓秋 / Xiaoqiu',
            '云野 / Yunye', '晓睿 / Xiaorui', '云曦 / Yunxi', '晓悠 / Xiaoyou',
            '云霞 / Yunxia', '云阳 / Yunyang', '晓墨 / Xiaomo'
        ]

        # Sort existing voices according to preferred order, then add any remaining
        sorted_voices = []
        remaining_voices = voice_options.copy()

        for preferred in preferred_order:
            if preferred in remaining_voices:
                sorted_voices.append(preferred)
                remaining_voices.remove(preferred)

        # Add any remaining voices that weren't in the preferred list
        sorted_voices.extend(sorted(remaining_voices))

        return sorted_voices

    def get_chinese_name(self, english_name):
        """Get Chinese name for voice"""
        name_mapping = {
            # 中国大陆语音 (zh-CN)
            'Xiaoxiao': '晓晓',
            'Xiaoyi': '晓伊',
            'Yunjian': '云健',
            'Yunxi': '云希',
            'Yunxia': '云夏',
            'Yunyang': '云扬',

            # 中国大陆方言语音
            'Xiaobei': '晓北',  # 辽宁
            'Xiaoni': '晓妮',   # 陕西

            # 香港语音 (zh-HK)
            'HiuGaai': '晓佳',
            'HiuMaan': '晓曼',
            'WanLung': '云龙',

            # 台湾语音 (zh-TW)
            'HsiaoChen': '晓臻',
            'YunJhe': '云哲',
            'HsiaoYu': '晓雨',

            # 其他可能的语音名称
            'Xiaoxuan': '晓萱',
            'Xiaochen': '晓辰',
            'Xiaohan': '晓涵',
            'Xiaoyan': '晓燕',
            'Yunhao': '云浩',
            'Xiaoshuang': '晓双',
            'Xiaomeng': '晓梦',
            'Yunfeng': '云峰',
            'Yunze': '云泽',
            'Xiaoqiu': '晓秋',
            'Yunye': '云野',
            'Xiaorui': '晓睿',
            'Xiaoyou': '晓悠',
            'Xiaomo': '晓墨'
        }
        return name_mapping.get(english_name, english_name)
    
    def get_selected_voice(self):
        """Get the currently selected voice"""
        selected_language = self.language_var.get()
        selected_voice_display = self.voice_var.get()

        if not selected_language or not selected_voice_display:
            return None

        # Extract English name from display format
        if ' / ' in selected_voice_display:
            english_name = selected_voice_display.split(' / ')[1]
        elif ' (' in selected_voice_display:
            # For non-Chinese voices format "Name (Gender)"
            english_name = selected_voice_display.split(' (')[0]
        else:
            english_name = selected_voice_display

        # Find the voice object by matching the English name in ShortName
        if selected_language == '中文 (所有地区)':
            # Search in all Chinese voices
            search_voices = [v for v in self.voices if v['Locale'].startswith('zh-')]
        else:
            # Search in specific language voices
            search_voices = [v for v in self.voices if v['Locale'] == selected_language]

        for voice in search_voices:
            if english_name in voice['ShortName'] or english_name in voice['FriendlyName']:
                return voice

        return None
    
    def generate_and_play(self):
        """试听按钮：根据左侧文本框内容生成音频并播放"""
        # 如果正在播放，则停止播放
        if self.is_playing:
            self.stop_audio()
            return

        # 获取文本框内容
        text = self.text_input.get("1.0", tk.END).strip()

        if not text:
            messagebox.showwarning("警告", "请在左侧文本框中输入要转换的文本。")
            return

        voice = self.get_selected_voice()
        if not voice:
            messagebox.showwarning("警告", "请选择一个语音。")
            return

        # 生成并播放音频
        self.generate_speech(text, voice, play_immediately=True)

    def generate_speech(self, text, voice, play_immediately=False):
        """生成语音"""
        
        # Run generation in separate thread
        def generate():
            try:
                self.root.after(0, lambda: self.status_var.set("正在生成语音..."))
                self.root.after(0, lambda: self.progress.config(mode='indeterminate'))
                self.root.after(0, lambda: self.progress.start())
                if play_immediately:
                    self.root.after(0, lambda: self.play_btn.config(text="生成中...", state="disabled"))
                
                # Create temporary file
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
                temp_file.close()

                # Generate speech using plain text (no SSML to avoid extra content)
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

                # Use plain text directly to avoid any extra content
                communicate = edge_tts.Communicate(text, voice['ShortName'])
                loop.run_until_complete(communicate.save(temp_file.name))
                loop.close()

                # Update GUI
                self.root.after(0, self.generation_complete, temp_file.name, play_immediately)
                
            except Exception as e:
                self.root.after(0, self.show_error, f"生成语音失败: {str(e)}")
        
        thread = threading.Thread(target=generate, daemon=True)
        thread.start()
    
    def generation_complete(self, audio_file, play_immediately=False):
        """Handle completion of speech generation"""
        self.current_audio_file = audio_file
        self.progress.stop()
        self.play_btn.config(state="normal")
        self.save_btn.config(state="normal")
        self.status_var.set("语音生成成功！")

        # Auto-play if requested
        if play_immediately:
            self.play_audio()
        else:
            # If this was called from save_audio, proceed with saving
            if hasattr(self, '_pending_save') and self._pending_save:
                self._pending_save = False
                self.do_save_audio()
    
    def play_audio(self):
        """播放生成的音频"""
        if not self.current_audio_file or not os.path.exists(self.current_audio_file):
            messagebox.showerror("错误", "没有音频文件可播放。")
            return

        try:
            pygame.mixer.music.load(self.current_audio_file)
            pygame.mixer.music.play()
            self.is_playing = True
            self.play_btn.config(text="停止", command=self.stop_audio)
            self.status_var.set("正在播放音频...")

            # 检查播放是否完成
            self.check_playback()

        except Exception as e:
            self.show_error(f"播放音频失败: {str(e)}")
    
    def check_playback(self):
        """Check if audio playback is still running"""
        if self.is_playing and not pygame.mixer.music.get_busy():
            self.playback_finished()
        elif self.is_playing:
            self.root.after(100, self.check_playback)
    
    def playback_finished(self):
        """Handle playback completion"""
        self.is_playing = False
        self.play_btn.config(text="试听", command=self.generate_and_play)
        self.status_var.set("播放完成。")
    
    def stop_audio(self):
        """停止音频播放"""
        pygame.mixer.music.stop()
        self.playback_finished()
    
    def save_audio(self):
        """保存按钮：根据左侧文本框内容生成音频并保存为MP3文件"""
        # 获取文本框内容
        text = self.text_input.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("警告", "请在左侧文本框中输入要转换的文本。")
            return

        voice = self.get_selected_voice()
        if not voice:
            messagebox.showwarning("警告", "请选择一个语音。")
            return

        # 先选择保存位置
        file_path = filedialog.asksaveasfilename(
            defaultextension=".mp3",
            filetypes=[("MP3 文件", "*.mp3"), ("所有文件", "*.*")],
            title="保存音频文件"
        )

        if not file_path:
            return  # 用户取消了保存

        # 保存文件路径，生成完成后使用
        self._save_path = file_path
        self._pending_save = True

        # 生成音频
        self.generate_speech(text, voice, play_immediately=False)

    def do_save_audio(self):
        """执行实际的保存操作"""
        if hasattr(self, '_save_path') and self._save_path:
            try:
                # 复制临时文件到选定位置
                import shutil
                shutil.copy2(self.current_audio_file, self._save_path)
                self.status_var.set(f"音频已保存到: {self._save_path}")
                messagebox.showinfo("成功", f"音频已成功保存到:\n{self._save_path}")

                # 清理保存路径
                self._save_path = None

            except Exception as e:
                self.show_error(f"保存音频失败: {str(e)}")
    
    def show_error(self, message):
        """显示错误信息并更新状态"""
        self.progress.stop()
        self.play_btn.config(state="normal", text="试听", command=self.generate_and_play)
        self.save_btn.config(state="normal")
        self.status_var.set("发生错误")
        messagebox.showerror("错误", message)


def main():
    """Main function to run the application"""
    root = tk.Tk()
    app = TTSApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
