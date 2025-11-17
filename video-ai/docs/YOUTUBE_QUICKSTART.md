# YouTube 集成快速开始指南

## 5 分钟快速上手

### 第 1 步：安装依赖

```bash
pip install yt-dlp youtube-transcript-api
```

### 第 2 步：下载视频

```python
from src.utils.youtube_downloader import YouTubeDownloader

# 创建下载器
downloader = YouTubeDownloader()

# 下载视频
result = downloader.download_video(
    url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    quality="720p"
)

print(f"✅ 下载完成: {result['filepath']}")
```

### 第 3 步：智能剪辑

```python
from src.core.editor import VideoEditor

# 创建编辑器（设置你的兴趣）
editor = VideoEditor(
    user_interests=["编程", "AI", "技术"],
    output_length="medium"
)

# 一键处理 YouTube 视频
result = editor.process_youtube_video(
    youtube_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    output_path="data/output/edited.mp4",
    quality="720p"
)

print(f"✅ 处理完成: {result.output_path}")
print(f"📊 压缩率: {result.compression_ratio:.1%}")
```

## 运行演示程序

```bash
cd /home/user/tvbox1/video-ai
python examples/youtube_demo.py
```

## 功能特性速览

- ✅ 下载 YouTube 视频（多种质量选择）
- ✅ 提取视频元数据
- ✅ 获取字幕（支持多语言）
- ✅ 智能内容剪辑
- ✅ 批量处理
- ✅ 缓存机制
- ✅ 进度显示

## 常见使用场景

### 场景 1：快速预览

```python
downloader = YouTubeDownloader()

# 获取元数据（不下载）
metadata = downloader.get_metadata(url)
print(f"标题: {metadata['title']}")
print(f"时长: {metadata['duration']} 秒")

# 获取字幕
transcript = downloader.get_transcript(url)
if transcript:
    print(f"字幕预览: {transcript[:200]}...")
```

### 场景 2：批量下载

```python
urls = [
    "https://www.youtube.com/watch?v=VIDEO_ID_1",
    "https://www.youtube.com/watch?v=VIDEO_ID_2",
    "https://www.youtube.com/watch?v=VIDEO_ID_3",
]

results = downloader.batch_download(urls, quality="480p")
print(f"成功下载 {len(results)} 个视频")
```

### 场景 3：个性化剪辑

```python
editor = VideoEditor(
    user_interests=["教程", "实战"],  # 你的兴趣
    output_length="short",            # 输出长度
    transition_style="modern"         # 过渡风格
)

result = editor.process_youtube_video(
    youtube_url,
    output_path="output/my_video.mp4",
    use_transcript=True  # 使用字幕加速处理
)
```

## 质量选择建议

| 场景       | 推荐质量 | 说明                   |
|------------|----------|------------------------|
| 快速测试   | 480p     | 下载快，处理快         |
| 日常使用   | 720p     | 平衡质量和速度         |
| 高质量输出 | 1080p    | 最佳画质               |
| 自动选择   | best     | 让系统选择最佳质量     |

## 故障排除

### 无法下载？

```bash
# 更新 yt-dlp
pip install --upgrade yt-dlp
```

### 找不到字幕？

这是正常的，不是所有视频都有字幕。系统会自动使用语音识别。

### 下载太慢？

- 选择较低质量（480p）
- 检查网络连接
- 使用缓存功能避免重复下载

## 进阶功能

### 自定义进度显示

```python
def my_callback(d):
    if d['status'] == 'downloading':
        print(f"下载: {d.get('_percent_str', 'N/A')}")

downloader.download_video(url, progress_callback=my_callback)
```

### 查看下载历史

```python
history = downloader.get_download_history()
for item in history:
    print(f"{item['title']} - {item['filepath']}")
```

### 清理缓存

```python
# 清理历史记录，保留文件
downloader.clear_cache(keep_files=True)

# 清理历史记录和文件
downloader.clear_cache(keep_files=False)
```

## 下一步

- 📖 阅读 [完整文档](youtube_integration.md)
- 🧪 运行 [测试用例](../tests/test_youtube_downloader.py)
- 💡 查看 [更多示例](../examples/youtube_demo.py)

## 技术支持

遇到问题？查看 [故障排除指南](youtube_integration.md#故障排除)
