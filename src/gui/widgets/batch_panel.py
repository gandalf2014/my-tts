"""
批量处理对话框组件 - 批量文本分割和语音生成
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Optional, Callable, List
from dataclasses import dataclass
import logging
import threading
from pathlib import Path

from ...tts.batch_processor import (
    BatchProcessor,
    BatchConfig,
    Segment,
    SegmentationMode,
    FailedSegment
)
from ...tts.voice_manager import Voice
from ...tts.generator import TTSOptions

logger = logging.getLogger(__name__)


class BatchDialog(tk.Toplevel):
    """
    批量处理对话框 - 模态对话框
    
    功能:
    - 选择txt文件导入
    - 预览分割后的文本段落
    - 选择输出目录
    - 批量生成语音文件
    - 显示进度和状态
    - 支持取消操作
    
    Attributes:
        _batch_processor: BatchProcessor实例
        _voice: 当前选择的语音
        _options: TTS选项
        _segments: 分割后的段落列表
        _is_processing: 是否正在处理
    """
    
    def __init__(
        self,
        parent: tk.Widget,
        batch_processor: BatchProcessor,
        voice: Optional[Voice] = None,
        options: Optional[TTSOptions] = None,
        on_complete: Optional[Callable[[List[str], List[FailedSegment]], None]] = None,
        **kwargs
    ):
        """
        初始化批量处理对话框
        
        Args:
            parent: 父窗口
            batch_processor: BatchProcessor实例
            voice: 当前选择的语音
            options: TTS选项
            on_complete: 批量处理完成回调
        """
        super().__init__(parent, **kwargs)
        
        self._batch_processor = batch_processor
        self._voice = voice
        self._options = options
        self._on_complete = on_complete
        
        # 状态
        self._segments: List[Segment] = []
        self._is_processing = False
        self._input_file_path: Optional[str] = None
        self._output_dir_path: str = str(Path.home() / "tts_output")
        
        # 设置对话框属性
        self.title("批量处理")
        self.geometry("700x500")
        self.resizable(True, True)
        self.transient(parent)  # 设置为父窗口的临时窗口
        self.grab_set()  # 模态对话框
        
        # 创建UI组件
        self._create_widgets()
        
        # 绑定关闭事件
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        
        # 居中显示
        self._center_window()
        
        logger.debug("BatchDialog 初始化完成")
    
    def _center_window(self) -> None:
        """将对话框居中显示"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        parent_x = self.master.winfo_x()
        parent_y = self.master.winfo_y()
        parent_width = self.master.winfo_width()
        parent_height = self.master.winfo_height()
        
        x = parent_x + (parent_width - width) // 2
        y = parent_y + (parent_height - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")
    
    def _create_widgets(self) -> None:
        """创建控件"""
        # 主框架
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 配置网格
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)  # 预览列表可扩展
        
        # === 文件选择区域 ===
        file_frame = ttk.LabelFrame(main_frame, text="文件选择", padding="5")
        file_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        file_frame.columnconfigure(1, weight=1)
        
        ttk.Label(file_frame, text="输入文件:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        
        self._file_path_var = tk.StringVar(value="未选择")
        self._file_path_label = ttk.Label(
            file_frame,
            textvariable=self._file_path_var,
            width=50,
            anchor=tk.W
        )
        self._file_path_label.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        
        self._select_file_btn = ttk.Button(
            file_frame,
            text="选择文件",
            command=self._select_file
        )
        self._select_file_btn.grid(row=0, column=2, padx=(5, 0))
        
        # === 分割预览区域 ===
        preview_frame = ttk.LabelFrame(main_frame, text="分割预览", padding="5")
        preview_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        preview_frame.columnconfigure(0, weight=1)
        preview_frame.rowconfigure(0, weight=1)
        
        # Treeview用于显示段落预览
        columns = ("index", "preview", "filename")
        self._preview_tree = ttk.Treeview(
            preview_frame,
            columns=columns,
            show="headings",
            height=10
        )
        
        # 设置列
        self._preview_tree.heading("index", text="序号")
        self._preview_tree.heading("preview", text="文本预览")
        self._preview_tree.heading("filename", text="文件名")
        
        self._preview_tree.column("index", width=60, anchor=tk.CENTER)
        self._preview_tree.column("preview", width=300, anchor=tk.W)
        self._preview_tree.column("filename", width=150, anchor=tk.W)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(
            preview_frame,
            orient=tk.VERTICAL,
            command=self._preview_tree.yview
        )
        self._preview_tree.configure(yscrollcommand=scrollbar.set)
        
        self._preview_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # === 输出目录选择区域 ===
        output_frame = ttk.LabelFrame(main_frame, text="输出设置", padding="5")
        output_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        output_frame.columnconfigure(1, weight=1)
        
        ttk.Label(output_frame, text="输出目录:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        
        self._output_dir_var = tk.StringVar(value=self._output_dir_path)
        self._output_dir_label = ttk.Label(
            output_frame,
            textvariable=self._output_dir_var,
            width=50,
            anchor=tk.W
        )
        self._output_dir_label.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        
        self._select_dir_btn = ttk.Button(
            output_frame,
            text="选择目录",
            command=self._select_output_dir
        )
        self._select_dir_btn.grid(row=0, column=2, padx=(5, 0))
        
        # === 进度和状态区域 ===
        progress_frame = ttk.Frame(main_frame)
        progress_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        progress_frame.columnconfigure(0, weight=1)
        
        # 进度条
        self._progress_var = tk.DoubleVar(value=0)
        self._progress_bar = ttk.Progressbar(
            progress_frame,
            variable=self._progress_var,
            maximum=100,
            mode='determinate'
        )
        self._progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # 进度标签
        self._progress_label_var = tk.StringVar(value="0 / 0")
        self._progress_label = ttk.Label(
            progress_frame,
            textvariable=self._progress_label_var,
            width=15
        )
        self._progress_label.grid(row=0, column=1, padx=(10, 0))
        
        # 状态标签
        self._status_var = tk.StringVar(value="请选择要处理的txt文件")
        status_label = ttk.Label(main_frame, textvariable=self._status_var)
        status_label.grid(row=4, column=0, sticky=tk.W, pady=(0, 10))
        
        # === 按钮区域 ===
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, sticky=(tk.W, tk.E))
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        button_frame.columnconfigure(2, weight=1)
        
        self._generate_btn = ttk.Button(
            button_frame,
            text="生成",
            command=self._start_generation,
            state=tk.DISABLED
        )
        self._generate_btn.grid(row=0, column=0, padx=(0, 5), sticky=(tk.W, tk.E))
        
        self._cancel_btn = ttk.Button(
            button_frame,
            text="取消",
            command=self._cancel_generation,
            state=tk.DISABLED
        )
        self._cancel_btn.grid(row=0, column=1, padx=5, sticky=(tk.W, tk.E))
        
        self._close_btn = ttk.Button(
            button_frame,
            text="关闭",
            command=self._on_close
        )
        self._close_btn.grid(row=0, column=2, padx=(5, 0), sticky=(tk.W, tk.E))
    
    def _select_file(self) -> None:
        """选择输入文件"""
        file_path = filedialog.askopenfilename(
            parent=self,
            title="选择文本文件",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        
        if not file_path:
            return
        
        # 验证文件扩展名
        if not file_path.lower().endswith('.txt'):
            messagebox.showwarning(
                "警告",
                "请选择txt文本文件。",
                parent=self
            )
            return
        
        try:
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            
            if not text.strip():
                messagebox.showwarning(
                    "警告",
                    "文件内容为空。",
                    parent=self
                )
                return
            
            self._input_file_path = file_path
            self._file_path_var.set(file_path)
            
            # 分割文本
            self._segments = self._batch_processor.segment_text(text)
            
            # 更新预览列表
            self._update_preview_list()
            
            # 更新状态
            self._status_var.set(f"已加载 {len(self._segments)} 个段落")
            
            # 启用生成按钮
            if self._segments and self._voice:
                self._generate_btn.config(state=tk.NORMAL)
            
            logger.info(f"文件已加载: {file_path}，共 {len(self._segments)} 个段落")
            
        except PermissionError:
            messagebox.showerror(
                "错误",
                "无法读取文件，请检查文件权限。",
                parent=self
            )
            logger.error(f"文件读取权限错误: {file_path}")
            
        except UnicodeDecodeError:
            messagebox.showerror(
                "错误",
                "文件编码错误，请使用UTF-8编码的文本文件。",
                parent=self
            )
            logger.error(f"文件编码错误: {file_path}")
            
        except Exception as e:
            messagebox.showerror(
                "错误",
                f"读取文件失败: {str(e)}",
                parent=self
            )
            logger.error(f"读取文件异常: {e}")
    
    def _select_output_dir(self) -> None:
        """选择输出目录"""
        dir_path = filedialog.askdirectory(
            parent=self,
            title="选择输出目录",
            initialdir=self._output_dir_path
        )
        
        if not dir_path:
            return
        
        # 验证目录是否可写
        try:
            test_file = Path(dir_path) / ".write_test"
            test_file.touch()
            test_file.unlink()
        except PermissionError:
            messagebox.showwarning(
                "警告",
                "输出目录不可写，请选择其他目录。",
                parent=self
            )
            return
        
        self._output_dir_path = dir_path
        self._output_dir_var.set(dir_path)
        
        # 更新BatchProcessor配置
        self._batch_processor.config.output_directory = dir_path
        
        logger.info(f"输出目录已设置: {dir_path}")
    
    def _update_preview_list(self) -> None:
        """更新预览列表"""
        # 清空现有项
        for item in self._preview_tree.get_children():
            self._preview_tree.delete(item)
        
        # 添加新项
        for segment in self._segments:
            self._preview_tree.insert(
                "",
                tk.END,
                values=(
                    segment.index + 1,
                    segment.preview,
                    segment.filename
                )
            )
        
        logger.debug(f"预览列表已更新，共 {len(self._segments)} 项")
    
    def _start_generation(self) -> None:
        """开始批量生成"""
        if not self._segments:
            messagebox.showwarning("警告", "没有可处理的段落。", parent=self)
            return
        
        if not self._voice:
            messagebox.showwarning("警告", "请先在主界面选择语音。", parent=self)
            return
        
        # 确保输出目录存在
        output_dir = Path(self._output_dir_path)
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
        except PermissionError:
            messagebox.showerror(
                "错误",
                "无法创建输出目录，请检查权限。",
                parent=self
            )
            return
        
        # 更新UI状态
        self._is_processing = True
        self._generate_btn.config(state=tk.DISABLED)
        self._cancel_btn.config(state=tk.NORMAL)
        self._close_btn.config(state=tk.DISABLED)
        self._select_file_btn.config(state=tk.DISABLED)
        self._select_dir_btn.config(state=tk.DISABLED)
        
        self._status_var.set("正在生成...")
        self._progress_var.set(0)
        
        # 更新BatchProcessor配置
        self._batch_processor.config.output_directory = self._output_dir_path
        
        # 在后台线程执行批量处理
        def run_batch():
            try:
                success_files, failed_segments = self._batch_processor.process_batch(
                    text="",  # 已分割，不需要再次分割
                    voice=self._voice,
                    options=self._options,
                    progress_callback=self._on_progress,
                    timeout=30.0
                )
                
                # 在主线程更新UI
                self.after(0, lambda: self._on_batch_complete(success_files, failed_segments))
                
            except Exception as e:
                logger.error(f"批量处理异常: {e}")
                self.after(0, lambda: self._on_batch_error(e))
        
        # 由于process_batch需要text参数，我们需要直接使用已分割的段落
        # 重新实现批量处理逻辑
        def run_batch_with_segments():
            try:
                self._batch_processor.reset()
                
                success_files = []
                failed_segments = []
                total = len(self._segments)
                
                for segment in self._segments:
                    if self._batch_processor.is_cancelled:
                        break
                    
                    # 更新进度
                    self.after(0, lambda s=segment: self._on_progress(s.index + 1, total, s))
                    
                    try:
                        output_path = str(output_dir / segment.filename)
                        
                        # 生成语音
                        result = self._batch_processor.generator.generate_sync(
                            text=segment.text,
                            voice_name=self._voice.short_name if hasattr(self._voice, 'short_name') else str(self._voice),
                            options=self._options,
                            output_path=output_path
                        )
                        
                        if result:
                            success_files.append(result)
                            logger.info(f"段落 {segment.index + 1}/{total} 生成成功")
                        else:
                            failed_segments.append(FailedSegment(
                                index=segment.index,
                                text=segment.text,
                                error="生成返回空结果"
                            ))
                            
                    except Exception as e:
                        failed_segments.append(FailedSegment(
                            index=segment.index,
                            text=segment.text,
                            error=str(e)
                        ))
                        logger.error(f"段落 {segment.index + 1} 生成失败: {e}")
                
                # 在主线程更新UI
                self.after(0, lambda: self._on_batch_complete(success_files, failed_segments))
                
            except Exception as e:
                logger.error(f"批量处理异常: {e}")
                self.after(0, lambda: self._on_batch_error(e))
        
        thread = threading.Thread(target=run_batch_with_segments, daemon=True)
        thread.start()
        
        logger.info("批量生成已启动")
    
    def _on_progress(self, current: int, total: int, segment: Segment) -> None:
        """进度回调"""
        if total > 0:
            progress = (current / total) * 100
            self._progress_var.set(progress)
            self._progress_label_var.set(f"{current} / {total}")
            self._status_var.set(f"正在处理段落 {current}/{total}: {segment.preview[:30]}...")
    
    def _on_batch_complete(
        self,
        success_files: List[str],
        failed_segments: List[FailedSegment]
    ) -> None:
        """批量处理完成"""
        self._is_processing = False
        self._generate_btn.config(state=tk.NORMAL)
        self._cancel_btn.config(state=tk.DISABLED)
        self._close_btn.config(state=tk.NORMAL)
        self._select_file_btn.config(state=tk.NORMAL)
        self._select_dir_btn.config(state=tk.NORMAL)
        
        # 更新进度
        total = len(self._segments)
        success_count = len(success_files)
        failed_count = len(failed_segments)
        
        self._progress_var.set(100)
        self._progress_label_var.set(f"{success_count} / {total}")
        
        # 显示结果
        if failed_count == 0:
            self._status_var.set(f"生成完成！共 {success_count} 个文件")
            messagebox.showinfo(
                "完成",
                f"批量生成完成！\n成功: {success_count} 个文件\n输出目录: {self._output_dir_path}",
                parent=self
            )
        else:
            self._status_var.set(f"完成，{failed_count} 个失败")
            
            # 构建失败信息
            failed_info = "\n".join([
                f"段落 {f.index + 1}: {f.error[:50]}"
                for f in failed_segments[:5]  # 最多显示5个
            ])
            if len(failed_segments) > 5:
                failed_info += f"\n... 还有 {len(failed_segments) - 5} 个失败"
            
            messagebox.showwarning(
                "部分完成",
                f"批量生成完成，但有部分失败:\n\n"
                f"成功: {success_count} 个\n"
                f"失败: {failed_count} 个\n\n"
                f"失败详情:\n{failed_info}",
                parent=self
            )
        
        # 调用完成回调
        if self._on_complete:
            self._on_complete(success_files, failed_segments)
        
        logger.info(f"批量处理完成: 成功 {success_count}, 失败 {failed_count}")
    
    def _on_batch_error(self, error: Exception) -> None:
        """批量处理错误"""
        self._is_processing = False
        self._generate_btn.config(state=tk.NORMAL)
        self._cancel_btn.config(state=tk.DISABLED)
        self._close_btn.config(state=tk.NORMAL)
        self._select_file_btn.config(state=tk.NORMAL)
        self._select_dir_btn.config(state=tk.NORMAL)
        
        self._status_var.set("生成失败")
        
        messagebox.showerror(
            "错误",
            f"批量生成失败: {str(error)}",
            parent=self
        )
        
        logger.error(f"批量处理错误: {error}")
    
    def _cancel_generation(self) -> None:
        """取消批量生成"""
        if self._is_processing:
            self._batch_processor.cancel()
            self._status_var.set("正在取消...")
            self._cancel_btn.config(state=tk.DISABLED)
            logger.info("用户请求取消批量处理")
    
    def _on_close(self) -> None:
        """关闭对话框"""
        if self._is_processing:
            # 询问是否确认关闭
            if messagebox.askyesno(
                "确认",
                "正在处理中，确定要关闭吗？\n关闭将取消当前操作。",
                parent=self
            ):
                self._batch_processor.cancel()
                self._is_processing = False
            else:
                return
        
        self.grab_release()
        self.destroy()
        logger.debug("BatchDialog 已关闭")
    
    def set_voice(self, voice: Voice) -> None:
        """设置语音"""
        self._voice = voice
        if self._segments and voice:
            self._generate_btn.config(state=tk.NORMAL)
        logger.debug(f"语音已设置: {voice.short_name if voice else 'None'}")
    
    def set_options(self, options: TTSOptions) -> None:
        """设置TTS选项"""
        self._options = options
        logger.debug(f"TTS选项已设置")
