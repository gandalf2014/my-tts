"""
文本输入面板组件
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
from typing import Optional, Callable


class TextPanel(ttk.Frame):
    """
    文本输入面板 - 左侧大型文本输入区域
    
    功能:
    - 多行文本输入
    - 文本获取/设置
    - 文本变化回调
    """
    
    def __init__(
        self,
        parent: tk.Widget,
        initial_text: str = "",
        on_text_change: Optional[Callable[[str], None]] = None,
        **kwargs
    ):
        """
        初始化文本面板
        
        Args:
            parent: 父组件
            initial_text: 初始文本
            on_text_change: 文本变化回调
            **kwargs: 传递给Frame的其他参数
        """
        super().__init__(parent, **kwargs)
        
        self._on_text_change = on_text_change
        
        # 配置网格
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        
        # 创建文本输入框
        self._text_widget = scrolledtext.ScrolledText(
            self,
            font=("Microsoft YaHei", 12),
            wrap=tk.WORD
        )
        self._text_widget.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 设置初始文本
        if initial_text:
            self._text_widget.insert("1.0", initial_text)
        
        # 绑定文本变化事件
        if on_text_change:
            self._text_widget.bind("<KeyRelease>", self._handle_text_change)
    
    @property
    def text(self) -> str:
        """获取文本内容"""
        return self._text_widget.get("1.0", tk.END).strip()
    
    @text.setter
    def text(self, value: str) -> None:
        """设置文本内容"""
        self._text_widget.delete("1.0", tk.END)
        self._text_widget.insert("1.0", value)
    
    def append(self, text: str) -> None:
        """追加文本"""
        self._text_widget.insert(tk.END, text)
    
    def clear(self) -> None:
        """清空文本"""
        self._text_widget.delete("1.0", tk.END)
    
    def _handle_text_change(self, event) -> None:
        """处理文本变化事件"""
        if self._on_text_change:
            self._on_text_change(self.text)
    
    def set_font(self, font_family: str, font_size: int) -> None:
        """设置字体"""
        self._text_widget.config(font=(font_family, font_size))
    
    def set_readonly(self, readonly: bool) -> None:
        """设置只读状态"""
        state = tk.DISABLED if readonly else tk.NORMAL
        self._text_widget.config(state=state)
