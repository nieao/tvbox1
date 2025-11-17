# Video-AI API 参考文档

完整的 Video-AI Python API 参考。

---

## 核心模块 (src/core/)

### VideoTranscriber

视频转录器，使用 Whisper 进行语音识别。

```python
from src.core.transcriber import VideoTranscriber

transcriber = VideoTranscriber(
    model_size: str = "base",      # tiny, base, small, medium, large
    device: str = "cuda",           # cuda, cpu
    language: str = None            # zh, en, None (自动检测)
)
```

**方法**:

#### transcribe(video_path: str) -> Dict

转录视频并返回文本和时间戳。

**参数**:
- `video_path` (str): 视频文件路径

**返回**: Dict
```python
{
    'text': str,                    # 完整转录文本
    'segments': List[Dict],         # 分段信息
    'language': str,                # 检测到的语言
    'duration': float               # 视频时长(秒)
}
```

**示例**:
```python
result = transcriber.transcribe("video.mp4")
print(result['text'])
for seg in result['segments']:
    print(f"{seg['start']:.2f}s - {seg['end']:.2f}s: {seg['text']}")
```

---

### ContentAnalyzer

内容分析器，支持 LLM 和 NLP 两种模式。

```python
from src.core.analyzer import ContentAnalyzer

analyzer = ContentAnalyzer(
    use_llm: bool = False,          # 是否使用LLM
    llm_provider: str = "openai",   # openai, gemini, claude
    api_key: str = None,            # API密钥
    model: str = "gpt-4"            # 模型名称
)
```

**方法**:

#### analyze(transcript: str, user_interests: List[str]) -> Dict

分析转录内容，提取相关片段。

**参数**:
- `transcript` (str): 转录文本
- `user_interests` (List[str]): 用户兴趣标签

**返回**: Dict
```python
{
    'segments': List[Dict],         # 相关片段
    'topics': List[str],            # 识别的主题
    'summary': str,                 # 内容摘要
    'mode': str                     # 使用的模式 (llm/nlp)
}
```

每个片段包含:
```python
{
    'start': float,                 # 开始时间
    'end': float,                   # 结束时间
    'text': str,                    # 片段文本
    'relevance_score': float,       # 相关性分数 (0-1)
    'topics': List[str]             # 片段主题
}
```

**示例**:
```python
result = analyzer.analyze(
    transcript="视频转录文本...",
    user_interests=["AI", "机器学习"]
)

for seg in result['segments']:
    if seg['relevance_score'] > 0.7:
        print(f"相关片段: {seg['text']} (分数: {seg['relevance_score']:.2f})")
```

---

### VideoEditor

视频编辑器，执行剪辑和拼接。

```python
from src.core.editor import VideoEditor

editor = VideoEditor(
    user_interests: List[str],             # 用户兴趣
    skip_topics: List[str] = None,         # 跳过的主题
    output_length: str = "medium",         # short/medium/long
    pace: str = "normal",                  # slow/normal/fast
    transition_style: str = "text",        # text/fade/blur/zoom/ai_generated
    use_llm: bool = False,                 # 是否使用LLM
    llm_provider: str = "openai",          # LLM提供商
    quality_threshold: float = 5.0         # 质量阈值 (1-10)
)
```

**方法**:

#### edit_video(input_path: str, output_path: str) -> Dict

编辑视频。

**参数**:
- `input_path` (str): 输入视频路径
- `output_path` (str): 输出视频路径

**返回**: Dict
```python
{
    'success': bool,                       # 是否成功
    'output_path': str,                    # 输出路径
    'original_duration': float,            # 原始时长(秒)
    'edited_duration': float,              # 编辑后时长(秒)
    'compression_ratio': float,            # 压缩率
    'segments_included': int,              # 包含片段数
    'processing_time': float,              # 处理时间(秒)
    'quality_score': float                 # 质量分数
}
```

**示例**:
```python
result = editor.edit_video("input.mp4", "output.mp4")
print(f"压缩率: {result['compression_ratio']:.1%}")
print(f"从 {result['original_duration']:.0f}秒 压缩到 {result['edited_duration']:.0f}秒")
```

---

### LLMFactory

LLM 工厂，统一创建不同的 LLM 提供商。

```python
from src.core.llm_factory import LLMFactory

# 创建LLM实例
llm = LLMFactory.create(
    provider: str,              # openai, gemini, claude
    api_key: str,               # API密钥
    model: str = None,          # 模型名称(可选)
    **kwargs                    # 其他参数
)
```

**支持的提供商**:
- `openai`: GPT-4, GPT-3.5-turbo
- `gemini`: gemini-pro, gemini-1.5-pro
- `claude`: claude-3-sonnet, claude-3-opus

**LLM 接口方法**:

#### generate(prompt: str, **kwargs) -> str

生成文本。

```python
response = await llm.generate(
    prompt="分析这段视频内容...",
    max_tokens=1000,
    temperature=0.7
)
```

#### generate_json(prompt: str, schema: Dict = None, **kwargs) -> Dict

生成 JSON 格式响应。

```python
result = await llm.generate_json(
    prompt="提取视频主题和摘要",
    schema={
        "type": "object",
        "properties": {
            "topics": {"type": "array"},
            "summary": {"type": "string"}
        }
    }
)
```

**示例**:
```python
# OpenAI
openai_llm = LLMFactory.create("openai", api_key="sk-...", model="gpt-4")
result = await openai_llm.generate("Analyze this content")

# Gemini
gemini_llm = LLMFactory.create("gemini", api_key="...", model="gemini-pro")
result = await gemini_llm.generate_json("Extract topics", schema={...})
```

---

## 服务模块 (src/services/)

### PersonalizationService

个性化服务，管理用户画像和推荐。

```python
from src.services.personalization import PersonalizationService

service = PersonalizationService(
    enable_realtime: bool = True,      # 启用实时推荐
    profile_dir: str = "data/profiles" # 用户画像目录
)
```

**方法**:

#### create_user_profile(user_id: str, initial_interests: List[str], **kwargs) -> None

创建用户画像。

```python
service.create_user_profile(
    user_id="user_001",
    initial_interests=["AI", "机器学习"]
)
```

#### track_user_action(user_id: str, action: str, video_id: str, **kwargs) -> None

追踪用户行为。

**参数**:
- `user_id` (str): 用户ID
- `action` (str): 行为类型 (view, like, dislike, share, skip)
- `video_id` (str): 视频ID
- `duration` (float): 观看时长(秒) [可选]
- `timestamp` (float): 时间戳 [可选]

```python
service.track_user_action(
    user_id="user_001",
    action="view",
    video_id="video_001",
    duration=600
)
```

#### get_realtime_recommendations(user_id: str, num: int = 10) -> List[Dict]

获取实时推荐。

**返回**: List[Dict]
```python
[
    {
        'video_id': str,                # 视频ID
        'score': float,                 # 相关度分数 (0-1)
        'reason': str,                  # 推荐原因
        'topics': List[str]             # 视频主题
    },
    ...
]
```

```python
recommendations = service.get_realtime_recommendations("user_001", num=5)
for rec in recommendations:
    print(f"{rec['video_id']}: {rec['score']:.2%} - {rec['reason']}")
```

---

### RealtimeRecommendationEngine

实时推荐引擎。

```python
from src.services.realtime_recommendation import RealtimeRecommendationEngine

engine = RealtimeRecommendationEngine()
```

**方法**:

#### add_video_metadata(video_id: str, metadata: Dict) -> None

添加视频元数据。

```python
engine.add_video_metadata('video_001', {
    'title': '深度学习入门',
    'topics': ['AI', '深度学习', '神经网络'],
    'category': '教育',
    'duration': 1200
})
```

#### track_behavior(user_id: str, action: str, video_id: str, **kwargs) -> None

追踪用户行为。

```python
engine.track_behavior('user_001', 'view', 'video_001', duration=600)
engine.track_behavior('user_001', 'like', 'video_001')
```

#### get_recommendations(user_id: str, num: int = 10) -> List[Dict]

获取推荐。

```python
recommendations = engine.get_recommendations('user_001', num=5)
```

#### get_user_insights(user_id: str) -> Dict

获取用户洞察。

**返回**: Dict
```python
{
    'user_id': str,
    'top_interests': List[Tuple[str, float]],  # (主题, 分数)
    'behavior_count': int,
    'avg_watch_duration': float,
    'favorite_categories': List[str]
}
```

---

## 工具模块 (src/utils/)

### YouTubeDownloader

YouTube 视频下载器。

```python
from src.utils.youtube_downloader import YouTubeDownloader

downloader = YouTubeDownloader(
    output_dir: str = "data/youtube",  # 输出目录
    quality: str = "best"              # 视频质量
)
```

**方法**:

#### download_video(url: str, **kwargs) -> Dict

下载视频。

**返回**: Dict
```python
{
    'success': bool,                   # 是否成功
    'video_path': str,                 # 视频路径
    'title': str,                      # 视频标题
    'duration': float,                 # 时长(秒)
    'description': str,                # 描述
    'tags': List[str],                 # 标签
    'subtitles': Dict                  # 字幕
}
```

```python
result = downloader.download_video("https://www.youtube.com/watch?v=...")
print(f"下载完成: {result['title']} ({result['duration']}秒)")
```

#### get_video_info(url: str) -> Dict

获取视频信息（不下载）。

```python
info = downloader.get_video_info(url)
print(f"标题: {info['title']}")
print(f"时长: {info['duration']}秒")
```

---

### NLPProcessor

NLP 处理器，免费的文本处理工具。

```python
from src.utils.nlp_processor import NLPProcessor

processor = NLPProcessor(
    language: str = "zh"               # zh, en
)
```

**方法**:

#### extract_keywords(text: str, top_k: int = 10) -> List[Tuple[str, float]]

提取关键词。

**返回**: List[Tuple[str, float]] - (关键词, 权重)

```python
keywords = processor.extract_keywords(
    "人工智能和机器学习是现代科技的核心",
    top_k=5
)
# [('人工智能', 0.85), ('机器学习', 0.80), ...]
```

#### calculate_similarity(text1: str, text2: str) -> float

计算文本相似度。

**返回**: float (0-1)

```python
similarity = processor.calculate_similarity(
    "深度学习教程",
    "机器学习入门"
)
# 0.73
```

#### summarize(text: str, ratio: float = 0.3) -> str

文本摘要。

```python
summary = processor.summarize(long_text, ratio=0.3)
# 返回原文本30%长度的摘要
```

---

## 数据模型 (src/models/)

### UserProfile

用户画像模型。

```python
from src.models.user_profile import UserProfile

profile = UserProfile(
    user_id: str,                      # 用户ID
    interests: List[str],              # 兴趣标签
    save_dir: str = "data/profiles"    # 保存目录
)
```

**属性**:
- `user_id` (str): 用户ID
- `interests` (List[str]): 兴趣标签
- `watched_videos` (List[str]): 观看历史
- `liked_videos` (List[str]): 点赞视频
- `disliked_videos` (List[str]): 不喜欢的视频
- `preferences` (Dict): 个人偏好设置

**方法**:

#### update_interests(new_interests: List[str]) -> None

更新兴趣。

```python
profile.update_interests(["深度学习", "神经网络"])
```

#### add_watch_history(video_id: str, duration: float) -> None

添加观看历史。

```python
profile.add_watch_history("video_001", duration=600)
```

#### save() -> None

保存用户画像。

```python
profile.save()
```

#### load(user_id: str, save_dir: str) -> UserProfile

加载用户画像（静态方法）。

```python
profile = UserProfile.load("user_001", save_dir="data/profiles")
```

---

## 错误处理

所有 API 可能抛出的异常:

```python
from src.core.exceptions import (
    VideoAIException,              # 基础异常
    TranscriptionError,            # 转录错误
    AnalysisError,                 # 分析错误
    EditingError,                  # 编辑错误
    LLMAPIError,                   # LLM API错误
    FileNotFoundError,             # 文件不存在
    InvalidParameterError          # 无效参数
)

try:
    result = editor.edit_video("input.mp4", "output.mp4")
except TranscriptionError as e:
    print(f"转录失败: {e}")
except EditingError as e:
    print(f"编辑失败: {e}")
except Exception as e:
    print(f"未知错误: {e}")
```

---

## 完整示例

### 端到端处理流程

```python
import asyncio
from src.core.transcriber import VideoTranscriber
from src.core.analyzer import ContentAnalyzer
from src.core.editor import VideoEditor
from src.services.personalization import PersonalizationService

async def process_video_pipeline(
    video_path: str,
    user_id: str,
    user_interests: List[str]
):
    """完整的视频处理流程"""

    # 1. 创建服务
    service = PersonalizationService(enable_realtime=True)

    # 2. 创建或加载用户画像
    try:
        service.create_user_profile(user_id, user_interests)
    except:
        pass  # 用户已存在

    # 3. 转录视频
    transcriber = VideoTranscriber(model_size="base", device="cuda")
    transcript_result = transcriber.transcribe(video_path)
    print(f"转录完成: {len(transcript_result['text'])} 字符")

    # 4. 分析内容
    analyzer = ContentAnalyzer(use_llm=False)
    analysis_result = analyzer.analyze(
        transcript_result['text'],
        user_interests
    )
    print(f"识别主题: {', '.join(analysis_result['topics'])}")
    print(f"相关片段: {len(analysis_result['segments'])} 个")

    # 5. 编辑视频
    editor = VideoEditor(
        user_interests=user_interests,
        output_length="medium",
        transition_style="fade"
    )
    edit_result = editor.edit_video(video_path, "output.mp4")

    # 6. 追踪用户行为
    service.track_user_action(
        user_id=user_id,
        action="view",
        video_id="video_001",
        duration=edit_result['edited_duration']
    )

    # 7. 获取推荐
    recommendations = service.get_realtime_recommendations(user_id, num=5)

    return {
        'edit_result': edit_result,
        'analysis': analysis_result,
        'recommendations': recommendations
    }

# 运行
if __name__ == "__main__":
    result = asyncio.run(process_video_pipeline(
        video_path="input.mp4",
        user_id="user_001",
        user_interests=["AI", "机器学习"]
    ))

    print(f"\n处理完成!")
    print(f"压缩率: {result['edit_result']['compression_ratio']:.1%}")
    print(f"推荐视频: {len(result['recommendations'])} 个")
```

---

## 配置参考

### config.yaml 格式

```yaml
# LLM 配置
openai:
  api_key: "sk-your-key"
  model: "gpt-4"
  max_tokens: 2000
  temperature: 0.7

google:
  api_key: "your-key"
  model: "gemini-pro"

anthropic:
  api_key: "your-key"
  model: "claude-3-sonnet-20240229"

# Whisper 配置
whisper:
  model_size: "base"           # tiny, base, small, medium, large
  device: "cuda"               # cuda, cpu
  compute_type: "float16"      # float16, int8

# 视频处理配置
video:
  default_output_length: "medium"
  default_quality: 7.0
  max_resolution: [1920, 1080]
  fps: 30

# 推荐系统配置
recommendation:
  enable_realtime: true
  cache_ttl: 300               # 秒
  similarity_threshold: 0.6
  
# 路径配置
paths:
  input_dir: "data/input"
  output_dir: "data/output"
  temp_dir: "data/temp"
  profile_dir: "data/profiles"
```

---

## API 版本兼容性

| API版本 | Python版本 | 状态 | 说明 |
|---------|-----------|------|------|
| v1.0.x  | 3.8+      | ✅ 当前 | 稳定版本 |
| v0.9.x  | 3.8+      | ⚠️ 废弃 | 仅bug修复 |

---

## 获取帮助

- 📖 [用户手册](USER_MANUAL.md)
- 👨‍💻 [开发者指南](DEVELOPER_GUIDE.md)
- 🐛 [提交Issue](https://github.com/yourusername/video-ai/issues)
- 💬 [Discord社区](https://discord.gg/video-ai)

---

**Last Updated**: 2024-11
