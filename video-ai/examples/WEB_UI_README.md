# Video-AI Web UI 使用指南

## 快速启动

### 方法 1: 使用启动脚本（推荐）

```bash
# 在项目根目录执行
./run_web_ui.sh
```

### 方法 2: 直接运行

```bash
# 在项目根目录执行
streamlit run examples/web_ui.py
```

### 方法 3: 指定端口

```bash
streamlit run examples/web_ui.py --server.port 8501
```

启动后，在浏览器中访问: http://localhost:8501

---

## 功能说明

### 📹 处理视频

视频处理的主要功能页面。

#### 输入方式

1. **📁 本地上传**
   - 支持格式: MP4, AVI, MOV, MKV, WEBM
   - 文件大小限制: 2GB
   - 自动保存到 `data/input/` 目录

2. **🌐 YouTube URL**
   - 输入 YouTube 视频链接
   - 选择下载质量 (360p, 480p, 720p, 1080p)
   - 自动下载并保存

3. **📂 选择已上传**
   - 从已上传的视频中选择
   - 查看文件大小信息

#### 个性化配置

在左侧边栏配置以下参数：

- **🏷️ 兴趣标签**
  - 选择预定义标签或添加自定义标签
  - 系统会优先保留相关内容

- **⏭️ 跳过主题**
  - 选择要自动跳过的内容类型
  - 默认跳过广告和推广

- **⏱️ 输出长度**
  - Short: 保留约30%内容
  - Medium: 保留约50%内容
  - Long: 保留约70%内容

- **🎨 过渡风格**
  - 文字卡片: 显示主题文字
  - 淡入淡出: 平滑过渡
  - 简单切换: 直接切换

- **🔧 高级设置**
  - 语言选择
  - 播放节奏

#### 处理流程

1. 点击 "🚀 开始处理视频"
2. 系统自动执行三个步骤：
   - 📝 步骤 1/3: 转录视频（提取音频并转文字）
   - 🧠 步骤 2/3: 分析内容（AI 分析视频内容）
   - ✂️ 步骤 3/3: 剪辑视频（智能剪辑和合并）
3. 查看处理结果和性能指标
4. 下载处理后的视频

#### 结果指标

- **原始时长**: 原始视频的总时长
- **剪辑后时长**: 处理后的视频时长
- **压缩率**: 压缩掉的内容比例
- **信息密度提升**: 单位时间内信息量的提升比例
- **片段数量**: 关键片段数量

---

### 📊 处理历史

查看所有视频处理历史记录。

#### 功能

- **搜索**: 按文件名搜索历史记录
- **排序**:
  - 时间（最新）
  - 时间（最旧）
  - 压缩率
- **查看详情**: 展开每条记录查看详细信息
  - 输入/输出文件信息
  - 处理时间
  - 性能指标
  - 使用的配置参数
- **清空历史**: 删除所有历史记录

---

### 📂 文件管理

管理输入和输出文件。

#### 输入文件

- 查看所有已上传的视频文件
- 下载已上传的文件
- 删除不需要的文件

#### 输出文件

- 查看所有处理后的视频
- 下载处理结果
- 删除旧文件

#### 批量操作

- 清空所有输入文件
- 清空所有输出文件

---

### ℹ️ 关于

项目信息和系统状态。

#### 内容

- 项目简介和核心功能
- 技术栈说明
- 使用指南
- 系统要求和依赖
- 性能指标
- 相关链接

#### 系统状态

- 输入文件数量
- 输出文件数量
- 历史记录数量

#### 环境检查

自动检测以下依赖是否已安装：
- FFmpeg
- MoviePy
- OpenAI Whisper
- yt-dlp

---

## 安装依赖

### 核心依赖

```bash
pip install streamlit moviepy openai-whisper yt-dlp
```

### 完整依赖

```bash
pip install -r requirements.txt
```

### 系统依赖

#### Ubuntu/Debian

```bash
sudo apt-get update
sudo apt-get install ffmpeg
```

#### macOS

```bash
brew install ffmpeg
```

#### Windows

下载 FFmpeg: https://ffmpeg.org/download.html

---

## 目录结构

```
video-ai/
├── data/
│   ├── input/          # 输入视频
│   ├── output/         # 输出视频
│   ├── temp/           # 临时文件
│   └── history.json    # 处理历史
├── examples/
│   ├── web_ui.py       # Web UI 主文件
│   └── WEB_UI_README.md
├── src/
│   ├── core/
│   │   ├── editor.py
│   │   ├── analyzer.py
│   │   └── transcriber.py
│   ├── services/
│   │   └── personalization.py
│   └── utils/
│       └── youtube_downloader.py
└── run_web_ui.sh       # 启动脚本
```

---

## 常见问题

### Q1: 启动失败，提示缺少模块

**A**: 安装缺少的依赖：

```bash
pip install streamlit moviepy openai-whisper yt-dlp
```

### Q2: 处理视频时出现 FFmpeg 错误

**A**: 确保已安装 FFmpeg：

```bash
# 测试 FFmpeg 是否可用
ffmpeg -version

# 如果未安装，根据系统安装
# Ubuntu/Debian:
sudo apt-get install ffmpeg

# macOS:
brew install ffmpeg
```

### Q3: YouTube 下载失败

**A**:
1. 确保网络连接正常
2. 确保 yt-dlp 已安装: `pip install yt-dlp`
3. 尝试更新 yt-dlp: `pip install -U yt-dlp`

### Q4: 视频转录速度慢

**A**:
- Whisper 模型使用 CPU 时较慢
- 可以使用更小的模型（在 `editor.py` 中修改）
- 或者使用 GPU 加速（需要安装 CUDA）

### Q5: 上传文件大小限制

**A**: Streamlit 默认限制 200MB，可以修改配置：

创建 `.streamlit/config.toml`:

```toml
[server]
maxUploadSize = 2000  # MB
```

### Q6: 界面显示不正常

**A**:
1. 刷新浏览器
2. 清除浏览器缓存
3. 重启 Streamlit 应用

---

## 性能优化

### 处理速度

- 使用较小的 Whisper 模型 (`tiny`, `base` 代替 `large`)
- 启用 GPU 加速（需要 CUDA）
- 选择较低的视频质量

### 存储空间

- 定期清理临时文件
- 删除不需要的输入和输出文件
- 使用较低的视频质量

### 内存使用

- 处理长视频时，使用 `short` 输出长度
- 避免同时处理多个大视频
- 定期重启应用

---

## 高级用法

### 自定义配置

修改 `web_ui.py` 中的配置：

```python
# 修改默认兴趣标签
predefined_interests = ["AI", "编程", "技术", "科学"]

# 修改默认跳过主题
predefined_skip = ["广告", "推广"]

# 修改输出目录
OUTPUT_DIR = Path("custom/output/path")
```

### 批量处理

在代码中使用 VideoEditor 的批量处理功能：

```python
from src.core.editor import VideoEditor

editor = VideoEditor(user_interests=["AI", "编程"])
results = editor.batch_process("data/input", "data/output")
```

### API 集成

Web UI 可以与 FastAPI 后端集成，实现更复杂的功能。

---

## 更新日志

### v0.1.0 (2024-11)

- ✅ 初始版本发布
- ✅ 支持本地上传和 YouTube 下载
- ✅ 个性化配置功能
- ✅ 处理历史记录
- ✅ 文件管理功能
- ✅ 完整的错误处理

---

## 反馈与支持

- 问题反馈: [GitHub Issues](https://github.com/yourusername/video-ai/issues)
- 功能建议: [GitHub Discussions](https://github.com/yourusername/video-ai/discussions)
- 文档: [Wiki](https://github.com/yourusername/video-ai/wiki)

---

## 许可证

MIT License

---

**Happy Video Editing! 🎬**
