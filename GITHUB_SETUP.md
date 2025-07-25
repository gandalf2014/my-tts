# 🐙 GitHub 提交指南

## ✅ 本地Git仓库已准备就绪！

您的项目已成功初始化为Git仓库，包含以下核心文件：

### 📦 已提交的文件
- ✅ `tts_gui.py` - 主程序文件
- ✅ `requirements.txt` - 依赖列表
- ✅ `build_exe.py` - 打包脚本
- ✅ `build_exe.bat` - Windows打包批处理
- ✅ `run_tts_gui.bat` - 快速启动脚本
- ✅ `README.md` - 项目说明文档
- ✅ `LICENSE` - MIT许可证
- ✅ `.gitignore` - Git忽略文件配置

## 🚀 推送到GitHub的步骤

### 1️⃣ 在GitHub上创建新仓库

1. 访问 [https://github.com/new](https://github.com/new)
2. 填写仓库信息：
   - **仓库名称**: `text-to-speech-gui` 或 `my-tts`
   - **描述**: `🎤 文本转语音GUI转换器 - 支持14种中文语音的现代化TTS应用`
   - **可见性**: 选择 `Public`（公开）
   - **不要勾选**: "Add a README file", "Add .gitignore", "Choose a license"
3. 点击 `Create repository`

### 2️⃣ 连接本地仓库到GitHub

在项目目录中执行以下命令（替换为您的GitHub用户名和仓库名）：

```bash
# 添加远程仓库
git remote add origin https://github.com/您的用户名/仓库名.git

# 设置主分支名称
git branch -M main

# 首次推送
git push -u origin main
```

### 3️⃣ 示例命令

假设您的GitHub用户名是 `yourname`，仓库名是 `text-to-speech-gui`：

```bash
git remote add origin https://github.com/yourname/text-to-speech-gui.git
git branch -M main
git push -u origin main
```

### 4️⃣ 验证推送成功

推送成功后，您应该能在GitHub仓库页面看到：
- 📄 README.md 文件内容显示在仓库首页
- 📁 所有核心文件都已上传
- 🏷️ 提交历史显示初始提交信息

## 🎯 后续操作建议

### 添加项目截图
1. 运行程序并截取界面截图
2. 将截图保存为 `screenshot.png`
3. 上传到GitHub仓库
4. 在README.md中添加截图展示

### 创建Release版本
1. 在GitHub仓库页面点击 `Releases`
2. 点击 `Create a new release`
3. 标签版本: `v1.0.0`
4. 发布标题: `🎤 文本转语音GUI转换器 v1.0.0`
5. 上传打包好的exe文件
6. 发布Release

### 设置仓库主题
在GitHub仓库页面：
1. 点击设置图标（齿轮）
2. 添加主题标签：`text-to-speech`, `tts`, `gui`, `chinese`, `python`, `tkinter`
3. 添加网站链接（如果有的话）

## 📋 Git命令参考

### 日常使用命令
```bash
# 查看状态
git status

# 添加文件
git add filename.py
git add .  # 添加所有文件

# 提交更改
git commit -m "描述更改内容"

# 推送到GitHub
git push

# 拉取最新更改
git pull
```

### 分支操作
```bash
# 创建新分支
git checkout -b feature-name

# 切换分支
git checkout main

# 合并分支
git merge feature-name
```

## 🔧 常见问题解决

### 问题1: 推送被拒绝
```bash
# 如果远程仓库有更改，先拉取
git pull origin main --allow-unrelated-histories
git push
```

### 问题2: 认证失败
- 使用GitHub Personal Access Token
- 或配置SSH密钥

### 问题3: 文件过大
- 检查.gitignore是否正确配置
- 移除不必要的大文件（如.mp3文件）

## 🎉 完成！

按照以上步骤，您的文本转语音GUI项目将成功发布到GitHub，其他用户可以：

- 🔍 发现和使用您的项目
- 📥 下载源代码
- 🐛 报告问题和建议
- 🤝 贡献代码改进

**祝您的开源项目获得成功！** ⭐

---

## 📞 需要帮助？

如果在推送过程中遇到问题，可以：
1. 检查网络连接
2. 确认GitHub用户名和仓库名正确
3. 查看Git错误信息
4. 参考GitHub官方文档
