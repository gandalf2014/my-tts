"""
GUI对话框模块
"""

import tkinter as tk
from tkinter import filedialog, messagebox
from typing import Optional, List, Tuple


def show_save_dialog(
    parent: Optional[tk.Tk] = None,
    default_name: str = "",
    default_ext: str = ".mp3"
) -> Optional[str]:
    """
    显示保存文件对话框
    
    Args:
        parent: 父窗口
        default_name: 默认文件名
        default_ext: 默认扩展名
        
    Returns:
        选择的文件路径，如果取消则返回None
    """
    file_path = filedialog.asksaveasfilename(
        parent=parent,
        defaultextension=default_ext,
        filetypes=[("MP3 文件", "*.mp3"), ("所有文件", "*.*")],
        title="保存音频文件",
        initialfile=default_name
    )
    return file_path if file_path else None


def show_open_dialog(
    parent: Optional[tk.Tk] = None,
    file_types: List[Tuple[str, str]] = None,
    title: str = "选择文件"
) -> Optional[str]:
    """
    显示打开文件对话框
    
    Args:
        parent: 父窗口
        file_types: 文件类型列表
        title: 对话框标题
        
    Returns:
        选择的文件路径，如果取消则返回None
    """
    if file_types is None:
        file_types = [("文本文件", "*.txt"), ("所有文件", "*.*")]
    
    file_path = filedialog.askopenfilename(
        parent=parent,
        filetypes=file_types,
        title=title
    )
    return file_path if file_path else None


def show_info(parent: Optional[tk.Tk] = None, title: str = "提示", message: str = "") -> None:
    """显示信息对话框"""
    messagebox.showinfo(title, message, parent=parent)


def show_warning(parent: Optional[tk.Tk] = None, title: str = "警告", message: str = "") -> None:
    """显示警告对话框"""
    messagebox.showwarning(title, message, parent=parent)


def show_error(parent: Optional[tk.Tk] = None, title: str = "错误", message: str = "") -> None:
    """显示错误对话框"""
    messagebox.showerror(title, message, parent=parent)


def ask_yes_no(
    parent: Optional[tk.Tk] = None,
    title: str = "确认",
    message: str = ""
) -> bool:
    """
    显示是/否确认对话框
    
    Returns:
        用户是否点击了"是"
    """
    return messagebox.askyesno(title, message, parent=parent)


def ask_ok_cancel(
    parent: Optional[tk.Tk] = None,
    title: str = "确认",
    message: str = ""
) -> bool:
    """
    显示确定/取消对话框
    
    Returns:
        用户是否点击了"确定"
    """
    return messagebox.askokcancel(title, message, parent=parent)
