# README 更新建议

## 建议在主 README.md 中添加以下内容

### 在"功能特性"部分添加:

```markdown
### YouTube 视频集成 🎬

- **直接下载**: 从 YouTube 下载视频（支持多种质量选择）
- **元数据提取**: 自动获取标题、描述、时长等信息
- **字幕获取**: 支持多语言字幕，包括自动生成字幕
- **智能剪辑**: 下载后自动进行个性化剪辑
- **批量处理**: 批量下载和处理多个视频
- **缓存机制**: 避免重复下载，节省时间和带宽
```

### 在"快速开始"部分添加:

```markdown
#### 处理 YouTube 视频

```python
from src.core.editor import VideoEditor

# 创建编辑器
editor = VideoEditor(
    user_interests=["编程", "AI", "技术"],
    output_length="medium"
)

# 一键处理 YouTube 视频
result = editor.process_youtube_video(
    youtube_url="https://www.youtube.com/watch?v=VIDEO_ID",
    output_path="data/output/edited.mp4",
    quality="720p"
)

print(f"处理完成: {result.output_path}")
print(f"压缩率: {result.compression_ratio:.1%}")
```

或使用命令行工具:

```bash
python scripts/youtube_cli.py process \
    https://www.youtube.com/watch?v=VIDEO_ID \
    -o output.mp4 \
    -i "编程,AI"
```
```

### 在"安装"部分添加:

```markdown
#### YouTube 集成依赖

```bash
# YouTube 下载支持
pip install yt-dlp youtube-transcript-api
```
```

### 添加新的章节:

```markdown
## YouTube 视频处理

Video-AI 现已支持直接从 YouTube 下载和处理视频！

### 基础使用

```python
from src.utils.youtube_downloader import YouTubeDownloader

# 下载视频
downloader = YouTubeDownloader()
result = downloader.download_video(
    url="https://www.youtube.com/watch?v=VIDEO_ID",
    quality="720p"
)
```

### 完整工作流

```python
from src.core.editor import VideoEditor

# 下载 + 智能剪辑
editor = VideoEditor(user_interests=["技术", "教程"])
result = editor.process_youtube_video(
    youtube_url="https://www.youtube.com/watch?v=VIDEO_ID",
    output_path="output.mp4"
)
```

### 命令行工具

```bash
# 下载视频
python scripts/youtube_cli.py download URL

# 获取元数据
python scripts/youtube_cli.py metadata URL

# 完整处理
python scripts/youtube_cli.py process URL -o output.mp4

# 批量下载
python scripts/youtube_cli.py batch URL1 URL2 URL3

# 查看历史
python scripts/youtube_cli.py history
```

### 文档

- [YouTube 集成完整文档](docs/youtube_integration.md)
- [快速开始指南](docs/YOUTUBE_QUICKSTART.md)
- [实现总结](docs/IMPLEMENTATION_SUMMARY.md)

### 示例

运行演示程序:

```bash
python examples/youtube_demo.py
```
```

### 在"项目结构"部分添加:

```markdown
├── scripts/
│   └── youtube_cli.py              # YouTube 命令行工具 🆕
├── src/
│   └── utils/
│       └── youtube_downloader.py   # YouTube 下载器 🆕
├── examples/
│   └── youtube_demo.py             # YouTube 演示程序 🆕
├── tests/
│   └── test_youtube_downloader.py  # YouTube 测试 🆕
└── docs/
    ├── youtube_integration.md      # YouTube 文档 🆕
    ├── YOUTUBE_QUICKSTART.md       # 快速开始 🆕
    └── IMPLEMENTATION_SUMMARY.md   # 实现总结 🆕
```

### 在"依赖"部分添加:

```markdown
#### YouTube 支持
- yt-dlp>=2023.11.16 - YouTube 视频下载
- youtube-transcript-api>=0.6.1 - 字幕获取
```

### 在"使用场景"部分添加:

```markdown
### YouTube 内容创作者

**场景**: 从 YouTube 下载长视频，自动提取精华片段

**解决方案**:
```python
editor = VideoEditor(user_interests=["教程", "技术"])
result = editor.process_youtube_video(
    "https://www.youtube.com/watch?v=LONG_VIDEO_ID",
    output_path="highlights.mp4",
    quality="1080p"
)
```

**效果**:
- 自动下载 YouTube 视频
- 使用 AI 提取关键内容
- 生成精华短视频
- 节省人工剪辑时间
```

### 在"特性亮点"部分添加:

```markdown
- 🎬 **YouTube 集成**: 直接下载和处理 YouTube 视频
- 📝 **字幕支持**: 自动获取多语言字幕
- 💾 **智能缓存**: 避免重复下载
- 📊 **批量处理**: 支持批量下载和剪辑
```

## 更新后的完整功能列表

```markdown
## 功能特性

### 🎯 核心功能

- ✅ 视频转录（Whisper）
- ✅ 内容分析（GPT/Claude/Gemini）
- ✅ 智能剪辑（MoviePy）
- ✅ 个性化推荐
- ✅ 批量处理
- ✅ **YouTube 视频集成** 🆕

### 🎬 YouTube 集成

- ✅ 视频下载（多质量选择）
- ✅ 元数据提取
- ✅ 字幕获取
- ✅ 智能剪辑
- ✅ 批量处理
- ✅ 播放列表支持
- ✅ 缓存机制

### 🎨 视频处理

- ✅ 关键片段提取
- ✅ 过渡效果生成
- ✅ 文字卡片
- ✅ 渐变过渡
- ✅ 模糊效果

### 🤖 AI 能力

- ✅ 多 LLM 支持（OpenAI, Anthropic, Google）
- ✅ 语音识别（Whisper, Faster-Whisper）
- ✅ 内容理解和总结
- ✅ 个性化推荐

### 🛠️ 工具

- ✅ Web 界面（Streamlit, Gradio）
- ✅ **命令行工具** 🆕
- ✅ REST API
- ✅ 批量处理脚本
```
