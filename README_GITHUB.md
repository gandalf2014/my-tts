# 🎤 文本转语音GUI转换器

一个基于Microsoft Edge TTS的现代化文本转语音GUI应用程序，支持14种中文语音和322+种多语言语音。

![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)

## ✨ 功能特点

- 🎤 **丰富的中文语音**: 支持14种中文语音，包括大陆、香港、台湾地区及方言
- 🌍 **多语言支持**: 支持322+种不同语言和地区的语音
- 🎨 **现代化界面**: 左右分栏设计，中文友好界面
- 🎧 **实时试听**: 根据文本框内容实时生成纯净音频
- 💾 **MP3保存**: 支持将生成的语音保存为MP3格式
- 📦 **独立运行**: 可打包为exe文件，无需Python环境

## 🖼️ 界面预览

```
┌─────────────────────────────────┬─────────────────────┐
│                                 │ 语言: 中文(所有地区)  │
│                                 │ ┌─────────────────┐ │
│                                 │ │ zh-CN          ▼│ │
│                                 │ └─────────────────┘ │
│        文本输入区域              │                     │
│                                 │ 语音: 晓萱/Xiaoxuan  │
│                                 │ ┌─────────────────┐ │
│                                 │ │ 晓萱/Xiaoxuan  ▼│ │
│                                 │ └─────────────────┘ │
│                                 │                     │
│                                 │ 语音风格: 默认       │
│                                 │ ┌─────────────────┐ │
│                                 │ │ 默认           ▼│ │
│                                 │ └─────────────────┘ │
│                                 │                     │
│                                 │ 进度: 00:00:00      │
│                                 │ ████████████████    │
│                                 │                     │
│                                 │ ┌────────┐┌───────┐│
│                                 │ │  试听  ││ 保存  ││
│                                 │ └────────┘└───────┘│
└─────────────────────────────────┴─────────────────────┘
```

## 🚀 快速开始

### 环境要求

- Python 3.7+
- Windows 操作系统
- 网络连接（用于语音合成服务）

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行程序

```bash
python tts_gui.py
```

## 🎤 支持的语音

### 中文语音 (14种)

#### 🇨🇳 中国大陆 (6种)
- 晓晓 / Xiaoxiao (女声) - 标准普通话
- 晓伊 / Xiaoyi (女声) - 温和甜美
- 云健 / Yunjian (男声) - 成熟稳重
- 云希 / Yunxi (男声) - 年轻活力
- 云夏 / Yunxia (男声) - 温暖亲和
- 云扬 / Yunyang (男声) - 清晰响亮

#### 🇭🇰 香港 (3种)
- 晓佳 / HiuGaai (女声) - 粤语传统
- 晓曼 / HiuMaan (女声) - 港式普通话
- 云龙 / WanLung (男声) - 港式普通话

#### 🇹🇼 台湾 (3种)
- 晓臻 / HsiaoChen (女声) - 台湾国语
- 云哲 / YunJhe (男声) - 台湾国语
- 晓雨 / HsiaoYu (女声) - 台湾官话

#### 🗣️ 方言 (2种)
- 晓北 / Xiaobei (女声) - 东北话
- 晓妮 / Xiaoni (女声) - 陕西话

### 其他语言
支持322+种语言，包括英语、日语、韩语、法语、德语、西班牙语等。

## 📖 使用说明

1. **输入文本**: 在左侧文本框中输入要转换的文本
2. **选择语言**: 选择"中文(所有地区)"或其他语言
3. **选择语音**: 从下拉菜单中选择喜欢的语音
4. **试听**: 点击"试听"按钮生成并播放音频
5. **保存**: 点击"保存"按钮将音频保存为MP3文件

## 🔧 打包为EXE

项目包含自动打包脚本，可以将程序打包为独立的exe文件：

```bash
# 运行打包脚本
python build_exe.py

# 或使用批处理文件 (Windows)
build_exe.bat
```

打包后的exe文件位于`dist/`目录中，可以在没有Python环境的Windows系统上直接运行。

## 📁 项目结构

```
my-tts/
├── tts_gui.py              # 主程序文件
├── requirements.txt        # 依赖列表
├── build_exe.py           # 打包脚本
├── build_exe.bat          # Windows打包批处理
├── README.md              # 项目说明
├── .gitignore             # Git忽略文件
└── dist/                  # 打包输出目录
    └── 文本转语音转换器.exe
```

## 🛠️ 技术栈

- **GUI框架**: Tkinter
- **TTS引擎**: Microsoft Edge TTS (edge-tts)
- **音频播放**: Pygame
- **打包工具**: PyInstaller
- **异步处理**: asyncio

## 🔧 故障排除

### 常见问题

1. **无法生成语音**
   - 检查网络连接
   - 确保防火墙允许程序访问网络

2. **音频无法播放**
   - 检查音频设备
   - 确保系统音量正常

3. **程序启动失败**
   - 检查Python版本 (需要3.7+)
   - 安装所有依赖包

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个项目！

### 开发环境设置

1. Fork 这个仓库
2. 创建你的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交你的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开一个Pull Request

## 📄 许可证

这个项目使用MIT许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- Microsoft Edge TTS团队提供优秀的语音合成服务
- edge-tts库开发者提供Python接口
- 所有为这个项目做出贡献的开发者

## 📞 联系

如果您有任何问题或建议，请通过以下方式联系：

- 提交 [Issue](https://github.com/yourusername/my-tts/issues)
- 发送邮件到: your.email@example.com

---

⭐ 如果这个项目对您有帮助，请给它一个星标！
