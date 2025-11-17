# YouTube 视频集成功能

Video-AI 现已支持直接从 YouTube 下载和处理视频！

## 功能特性

### 核心功能

1. **视频下载**
   - 支持多种质量选择（480p, 720p, 1080p, best）
   - 下载进度实时显示
   - 自动缓存机制（避免重复下载）
   - 错误重试机制

2. **元数据提取**
   - 视频标题、描述
   - 时长、上传者
   - 观看次数、点赞数
   - 标签、分类

3. **字幕获取**
   - 支持多语言字幕（中文、英文等）
   - 自动生成字幕支持
   - 字幕优先级配置

4. **批量处理**
   - 批量下载多个视频
   - 播放列表支持
   - 下载历史记录

5. **智能剪辑集成**
   - 自动下载 + 智能剪辑
   - 利用 YouTube 字幕加速处理
   - 个性化内容提取

## 快速开始

### 1. 安装依赖

```bash
pip install yt-dlp youtube-transcript-api
```

### 2. 基础使用

#### 仅下载视频

```python
from src.utils.youtube_downloader import YouTubeDownloader

# 创建下载器
downloader = YouTubeDownloader(
    output_dir="data/input",
    cache_dir="data/cache"
)

# 下载视频
result = downloader.download_video(
    url="https://www.youtube.com/watch?v=VIDEO_ID",
    quality="720p"
)

print(f"下载完成: {result['filepath']}")
```

#### 完整处理流程（下载 + 剪辑）

```python
from src.core.editor import VideoEditor

# 创建编辑器
editor = VideoEditor(
    user_interests=["编程", "AI", "技术"],
    output_length="medium"
)

# 处理 YouTube 视频
result = editor.process_youtube_video(
    youtube_url="https://www.youtube.com/watch?v=VIDEO_ID",
    output_path="data/output/edited.mp4",
    quality="720p",
    use_transcript=True  # 使用 YouTube 字幕
)

print(f"处理完成: {result.output_path}")
```

### 3. 运行演示

```bash
cd /home/user/tvbox1/video-ai
python examples/youtube_demo.py
```

## API 参考

### YouTubeDownloader

#### 初始化

```python
downloader = YouTubeDownloader(
    output_dir="data/input",  # 视频输出目录
    cache_dir="data/cache"    # 缓存目录
)
```

#### 主要方法

##### download_video()

下载 YouTube 视频

```python
result = downloader.download_video(
    url: str,                           # YouTube 视频 URL
    quality: str = "720p",              # 视频质量 (480p, 720p, 1080p, best)
    progress_callback: Callable = None, # 进度回调函数
    filename: str = None,               # 自定义文件名
    force_download: bool = False        # 强制下载（忽略缓存）
) -> Dict
```

**返回值:**
```python
{
    'video_id': str,       # 视频 ID
    'filepath': str,       # 文件路径
    'filename': str,       # 文件名
    'title': str,          # 视频标题
    'duration': int,       # 时长（秒）
    'quality': str,        # 质量
    'filesize': int,       # 文件大小（字节）
    'download_date': str,  # 下载日期
    'metadata': dict       # 完整元数据
}
```

##### get_metadata()

获取视频元数据（不下载）

```python
metadata = downloader.get_metadata(
    url: str,              # YouTube 视频 URL
    retry_count: int = 3   # 重试次数
) -> Dict
```

##### get_transcript()

获取视频字幕

```python
transcript = downloader.get_transcript(
    url: str,                                    # YouTube 视频 URL
    languages: List[str] = ['zh', 'zh-CN', 'en'] # 语言优先级
) -> Optional[str]
```

##### batch_download()

批量下载视频

```python
results = downloader.batch_download(
    urls: List[str],                    # URL 列表
    quality: str = "720p",              # 视频质量
    progress_callback: Callable = None  # 进度回调
) -> List[Dict]
```

##### download_playlist()

下载播放列表

```python
results = downloader.download_playlist(
    playlist_url: str,                  # 播放列表 URL
    quality: str = "720p",              # 视频质量
    max_videos: int = None,             # 最大下载数量
    progress_callback: Callable = None  # 进度回调
) -> List[Dict]
```

##### get_download_history()

获取下载历史

```python
history = downloader.get_download_history() -> List[Dict]
```

##### clear_cache()

清理缓存

```python
downloader.clear_cache(
    keep_files: bool = True  # 是否保留已下载的文件
)
```

### VideoEditor

#### process_youtube_video()

处理 YouTube 视频（下载 + 剪辑）

```python
result = editor.process_youtube_video(
    youtube_url: str,           # YouTube 视频 URL
    output_path: str,           # 输出路径
    quality: str = "720p",      # 下载质量
    use_transcript: bool = True # 是否使用 YouTube 字幕
) -> EditingResult
```

#### batch_process_youtube()

批量处理 YouTube 视频

```python
results = editor.batch_process_youtube(
    youtube_urls: List[str],  # YouTube 视频 URL 列表
    output_dir: str,          # 输出目录
    quality: str = "720p"     # 视频质量
) -> List[EditingResult]
```

## 高级用法

### 自定义进度回调

```python
def my_progress_callback(d):
    """自定义进度显示"""
    if d['status'] == 'downloading':
        percent = d.get('_percent_str', 'N/A')
        speed = d.get('_speed_str', 'N/A')
        eta = d.get('_eta_str', 'N/A')

        print(f"下载进度: {percent} | 速度: {speed} | 剩余: {eta}")
    elif d['status'] == 'finished':
        print("下载完成，正在处理...")

# 使用自定义回调
result = downloader.download_video(
    url="https://www.youtube.com/watch?v=VIDEO_ID",
    progress_callback=my_progress_callback
)
```

### 批量处理示例

```python
# 1. 批量下载
urls = [
    "https://www.youtube.com/watch?v=VIDEO_ID_1",
    "https://www.youtube.com/watch?v=VIDEO_ID_2",
    "https://www.youtube.com/watch?v=VIDEO_ID_3",
]

results = downloader.batch_download(urls, quality="480p")

# 2. 批量剪辑
editor = VideoEditor(user_interests=["技术", "教程"])

editing_results = editor.batch_process_youtube(
    youtube_urls=urls,
    output_dir="data/output/batch",
    quality="480p"
)
```

### 播放列表处理

```python
# 下载播放列表（限制前 5 个视频）
playlist_url = "https://www.youtube.com/playlist?list=PLAYLIST_ID"

results = downloader.download_playlist(
    playlist_url,
    quality="720p",
    max_videos=5
)

print(f"下载了 {len(results)} 个视频")
```

### 使用缓存

```python
# 首次下载
result1 = downloader.download_video(url, quality="720p")
# 实际下载视频

# 再次调用（使用缓存）
result2 = downloader.download_video(url, quality="720p")
# 直接返回缓存结果，不重复下载

# 强制重新下载
result3 = downloader.download_video(url, quality="720p", force_download=True)
# 忽略缓存，重新下载
```

## 支持的 URL 格式

- `https://www.youtube.com/watch?v=VIDEO_ID`
- `https://youtu.be/VIDEO_ID`
- `https://www.youtube.com/embed/VIDEO_ID`
- `https://m.youtube.com/watch?v=VIDEO_ID`
- `VIDEO_ID`（直接输入 ID）

## 质量选项

| 选项   | 说明           | 推荐场景         |
|--------|----------------|------------------|
| 480p   | 标清           | 快速预览、测试   |
| 720p   | 高清（默认）   | 一般使用         |
| 1080p  | 全高清         | 高质量需求       |
| best   | 最佳质量       | 最终输出         |

## 错误处理

```python
from src.utils.youtube_downloader import YouTubeDownloader

downloader = YouTubeDownloader()

try:
    result = downloader.download_video(
        url="https://www.youtube.com/watch?v=VIDEO_ID",
        quality="720p"
    )
    print(f"成功: {result['filepath']}")

except ValueError as e:
    print(f"无效的 URL: {e}")

except Exception as e:
    print(f"下载失败: {e}")
```

## 注意事项

1. **网络要求**: 需要稳定的网络连接
2. **存储空间**: 确保有足够的磁盘空间
3. **版权**: 请遵守 YouTube 服务条款和版权法
4. **性能**: 高质量视频下载和处理需要更多时间
5. **依赖**: 需要 `ffmpeg` 用于视频处理

## 故障排除

### 问题：下载失败

**解决方案:**
```bash
# 更新 yt-dlp 到最新版本
pip install --upgrade yt-dlp

# 检查网络连接
ping youtube.com
```

### 问题：找不到字幕

**说明:** 不是所有视频都有字幕。系统会自动回退到语音识别。

### 问题：视频质量不可用

**解决方案:** 尝试其他质量选项，或使用 `best` 自动选择。

## 测试

运行单元测试：

```bash
cd /home/user/tvbox1/video-ai
python tests/test_youtube_downloader.py
```

运行演示：

```bash
python examples/youtube_demo.py
```

## 性能优化建议

1. **使用字幕**: 启用 `use_transcript=True` 可跳过语音识别，大幅提升速度
2. **选择合适质量**: 480p 适合快速测试，720p 适合一般使用
3. **批量处理**: 批量操作比单独处理更高效
4. **缓存利用**: 不强制下载时会自动使用缓存

## 示例工作流

### 完整工作流示例

```python
from src.utils.youtube_downloader import YouTubeDownloader
from src.core.editor import VideoEditor

# 1. 下载视频
downloader = YouTubeDownloader()
url = "https://www.youtube.com/watch?v=VIDEO_ID"

# 2. 获取信息
metadata = downloader.get_metadata(url)
print(f"视频: {metadata['title']}")
print(f"时长: {metadata['duration']} 秒")

# 3. 下载
video_info = downloader.download_video(url, quality="720p")

# 4. 智能剪辑
editor = VideoEditor(user_interests=["教程", "技术"])
result = editor.process_video(
    video_info['filepath'],
    "output/edited.mp4"
)

# 或者一步完成
result = editor.process_youtube_video(
    url,
    "output/edited.mp4",
    quality="720p"
)
```

## 更多资源

- [项目主 README](/home/user/tvbox1/video-ai/README.md)
- [API 文档](/home/user/tvbox1/video-ai/docs/)
- [示例代码](/home/user/tvbox1/video-ai/examples/)

## 反馈与支持

如有问题或建议，请提交 Issue 或 Pull Request。
