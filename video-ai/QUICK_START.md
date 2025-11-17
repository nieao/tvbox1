# Video-AI Web UI 快速开始指南

## 5分钟快速启动

### 步骤 1: 安装依赖

```bash
# 进入项目目录
cd /home/user/tvbox1/video-ai

# 安装核心依赖（必需）
pip install streamlit moviepy openai-whisper yt-dlp

# 或安装完整依赖（推荐）
pip install -r requirements.txt
```

### 步骤 2: 安装 FFmpeg

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**验证安装:**
```bash
ffmpeg -version
```

### 步骤 3: 启动 Web UI

**方法 1: 使用启动脚本（推荐）**
```bash
./run_web_ui.sh
```

**方法 2: 直接运行**
```bash
streamlit run examples/web_ui.py
```

### 步骤 4: 打开浏览器

访问: http://localhost:8501

---

## 快速测试

### 测试 1: 本地视频

1. 切换到 "📹 处理视频" 标签
2. 选择 "📁 本地上传"
3. 上传一个测试视频（建议 < 100MB）
4. 配置兴趣标签（左侧边栏）
5. 点击 "🚀 开始处理视频"
6. 等待处理完成
7. 下载结果

### 测试 2: YouTube 视频

1. 切换到 "📹 处理视频" 标签
2. 选择 "🌐 YouTube URL"
3. 输入 YouTube URL（例如: https://www.youtube.com/watch?v=...）
4. 选择质量（推荐 720p）
5. 点击 "⬇️ 下载视频"
6. 等待下载完成
7. 点击 "🚀 开始处理视频"
8. 下载结果

---

## 验证安装

运行验证脚本：

```bash
python3 examples/test_web_ui.py
```

预期输出：
```
✅ VideoEditor
✅ PersonalizationConfig
✅ YouTubeDownloader
✅ 配置创建成功
```

---

## 常见问题速查

### Q: Streamlit 未安装？

```bash
pip install streamlit
```

### Q: FFmpeg 未找到？

```bash
# Ubuntu/Debian
sudo apt-get install ffmpeg

# macOS
brew install ffmpeg

# Windows
# 下载: https://ffmpeg.org/download.html
```

### Q: YouTube 下载失败？

```bash
# 更新 yt-dlp
pip install -U yt-dlp
```

### Q: MoviePy 错误？

```bash
pip install moviepy
```

### Q: Whisper 未安装？

```bash
pip install openai-whisper
```

---

## 目录结构

确保以下目录存在：

```
video-ai/
├── data/
│   ├── input/      # 自动创建
│   ├── output/     # 自动创建
│   └── temp/       # 自动创建
├── examples/
│   └── web_ui.py   # Web UI 主文件
└── src/
    ├── core/
    ├── services/
    └── utils/
```

---

## 配置 API Keys（可选）

如果使用 OpenAI API：

```bash
# 创建 .env 文件
echo "OPENAI_API_KEY=your-api-key-here" > .env
```

如果使用 Google Gemini API：

```bash
echo "GOOGLE_API_KEY=your-api-key-here" >> .env
```

---

## 性能建议

### 首次使用

1. 使用小视频测试（< 5分钟）
2. 选择 "short" 输出长度
3. 使用 "720p" 质量下载

### 生产使用

1. 根据需求选择输出长度
2. 定期清理临时文件
3. 使用 GPU 加速（如果可用）

---

## 下一步

1. 📖 阅读完整文档: `examples/WEB_UI_README.md`
2. 🔍 查看功能特性: `examples/FEATURES.md`
3. 💡 探索示例代码: `examples/`
4. 🐛 报告问题: GitHub Issues

---

## 支持

- 📧 Email: support@video-ai.com
- 💬 Discord: https://discord.gg/video-ai
- 📖 文档: https://docs.video-ai.com
- 🐛 Issues: https://github.com/yourusername/video-ai/issues

---

**准备好了吗？开始您的智能视频编辑之旅！** 🚀
