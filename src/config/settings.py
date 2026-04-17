"""
配置管理模块 - 应用设置持久化
"""

import json
import os
import logging
from typing import Any, Dict, Optional
from dataclasses import dataclass, asdict, field
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class VoicePreset:
    """语音预设数据类 - 保存语音配置快照"""
    name: str  # 预设名称，如 "播客女声"
    voice_short_name: str  # 语音短名称，如 "zh-CN-XiaoxiaoMultilingualNeural"
    voice_display_name: str  # 语音显示名称，如 "晓晓 / Xiaoxiao"
    language: str  # 语言，如 "中文 (所有地区)"
    speed: float = 1.0  # 语速
    pitch: float = 1.0  # 音调
    volume: float = 100.0  # 音量


@dataclass
class AppConfig:
    """应用配置数据类"""
    # 窗口设置
    window_width: int = 800
    window_height: int = 600
    
    # 默认语音设置
    default_language: str = "中文 (所有地区)"
    default_voice: str = "晓萱 / Xiaoxuan"
    
    # 音频参数
    default_speed: float = 1.0
    default_pitch: float = 1.0
    default_volume: float = 100.0
    
    # 最近使用
    recent_voices: list = field(default_factory=list)
    
    # 其他设置
    auto_play_after_generate: bool = True
    last_save_directory: str = ""
    
    # 批量处理设置
    last_batch_import_dir: str = ""
    batch_segmentation_mode: str = "paragraph"  # "paragraph" or "chars"
    
    # 语音预设列表
    voice_presets: list = field(default_factory=list)


class Settings:
    """
    设置管理器 - 管理应用配置的读取和保存
    
    功能:
    - 配置持久化到JSON文件
    - 默认配置管理
    - 配置项访问接口
    """
    
    DEFAULT_CONFIG = AppConfig()
    
    def __init__(self, config_path: Optional[str] = None):
        """
        初始化设置管理器
        
        Args:
            config_path: 配置文件路径，默认为用户目录下的.tts_gui/config.json
        """
        if config_path:
            self._config_path = Path(config_path)
        else:
            # 默认配置路径
            config_dir = Path.home() / ".tts_gui"
            config_dir.mkdir(parents=True, exist_ok=True)
            self._config_path = config_dir / "config.json"
        
        self._config: Optional[AppConfig] = None
        self._load()
    
    @property
    def config(self) -> AppConfig:
        """获取当前配置"""
        if self._config is None:
            self._config = AppConfig()
        return self._config
    
    @property
    def config_path(self) -> Path:
        """配置文件路径"""
        return self._config_path
    
    def _load(self) -> None:
        """从文件加载配置"""
        if self._config_path.exists():
            try:
                with open(self._config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self._config = AppConfig(**data)
                logger.info(f"配置已加载: {self._config_path}")
            except Exception as e:
                logger.error(f"加载配置失败: {e}")
                self._config = AppConfig()
        else:
            self._config = AppConfig()
    
    def save(self) -> bool:
        """
        保存配置到文件
        
        Returns:
            是否成功保存
        """
        try:
            # 确保目录存在
            self._config_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 写入配置
            with open(self._config_path, 'w', encoding='utf-8') as f:
                json.dump(asdict(self.config), f, ensure_ascii=False, indent=2)
            
            logger.info(f"配置已保存: {self._config_path}")
            return True
            
        except Exception as e:
            logger.error(f"保存配置失败: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置项
        
        Args:
            key: 配置项名称
            default: 默认值
            
        Returns:
            配置值
        """
        if hasattr(self.config, key):
            return getattr(self.config, key)
        return default
    
    def set(self, key: str, value: Any) -> None:
        """
        设置配置项
        
        Args:
            key: 配置项名称
            value: 配置值
        """
        if hasattr(self.config, key):
            setattr(self.config, key, value)
        else:
            logger.warning(f"未知的配置项: {key}")
    
    def update(self, **kwargs) -> None:
        """
        批量更新配置
        
        Args:
            **kwargs: 配置项键值对
        """
        for key, value in kwargs.items():
            self.set(key, value)
    
    def reset(self) -> None:
        """重置为默认配置"""
        self._config = AppConfig()
        logger.info("配置已重置为默认值")
    
    def reset_to_defaults(self) -> None:
        """重置为默认配置并保存"""
        self.reset()
        self.save()


class PresetManager:
    """
    语音预设管理器 - 管理语音预设的CRUD操作
    
    功能:
    - 保存语音预设（检测重复名称）
    - 加载语音预设
    - 删除语音预设
    - 列出所有预设
    """
    
    @staticmethod
    def save_preset(config: AppConfig, preset: VoicePreset) -> bool:
        """
        保存语音预设到配置
        
        Args:
            config: 应用配置对象
            preset: 语音预设对象
            
        Returns:
            是否成功保存
        """
        try:
            # 检查是否存在同名预设
            existing_index = None
            for i, p in enumerate(config.voice_presets):
                if isinstance(p, dict) and p.get('name') == preset.name:
                    existing_index = i
                    break
                elif isinstance(p, VoicePreset) and p.name == preset.name:
                    existing_index = i
                    break
            
            preset_dict = asdict(preset)
            
            if existing_index is not None:
                # 覆盖现有预设
                logger.warning(f"覆盖同名预设: {preset.name}")
                config.voice_presets[existing_index] = preset_dict
            else:
                # 添加新预设
                config.voice_presets.append(preset_dict)
                logger.info(f"保存语音预设: {preset.name}")
            
            return True
            
        except Exception as e:
            logger.error(f"保存预设失败: {preset.name}, 错误: {e}")
            return False
    
    @staticmethod
    def load_preset(config: AppConfig, name: str) -> Optional[VoicePreset]:
        """
        加载语音预设
        
        Args:
            config: 应用配置对象
            name: 预设名称
            
        Returns:
            VoicePreset对象，如果不存在返回None
        """
        try:
            for p in config.voice_presets:
                if isinstance(p, dict) and p.get('name') == name:
                    logger.info(f"加载语音预设: {name}")
                    return VoicePreset(**p)
                elif isinstance(p, VoicePreset) and p.name == name:
                    logger.info(f"加载语音预设: {name}")
                    return p
            
            logger.warning(f"未找到预设: {name}")
            return None
            
        except Exception as e:
            logger.error(f"加载预设失败: {name}, 错误: {e}")
            return None
    
    @staticmethod
    def delete_preset(config: AppConfig, name: str) -> bool:
        """
        删除语音预设
        
        Args:
            config: 应用配置对象
            name: 预设名称
            
        Returns:
            是否成功删除
        """
        try:
            for i, p in enumerate(config.voice_presets):
                preset_name = p.get('name') if isinstance(p, dict) else p.name
                if preset_name == name:
                    config.voice_presets.pop(i)
                    logger.info(f"删除语音预设: {name}")
                    return True
            
            logger.warning(f"删除预设失败，未找到: {name}")
            return False
            
        except Exception as e:
            logger.error(f"删除预设失败: {name}, 错误: {e}")
            return False
    
    @staticmethod
    def list_presets(config: AppConfig) -> list:
        """
        列出所有语音预设
        
        Args:
            config: 应用配置对象
            
        Returns:
            VoicePreset对象列表
        """
        presets = []
        try:
            for p in config.voice_presets:
                if isinstance(p, dict):
                    presets.append(VoicePreset(**p))
                elif isinstance(p, VoicePreset):
                    presets.append(p)
            
            logger.debug(f"列出语音预设: {len(presets)}个")
            return presets
            
        except Exception as e:
            logger.error(f"列出预设失败: {e}")
            return []
