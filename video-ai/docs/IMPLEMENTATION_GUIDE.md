# AI Video Summarizer 项目实现指南

## 快速导航

本指南包含可直接应用到 video-ai 项目的实现建议和代码模板。

---

## 1. 架构参考对比

### ai-video-summarizer 架构（参考）

```
User Interface Layer
    ↓ (HTTP/REST)
API Server Layer (FastAPI)
    ↓ (Python modules)
Processing Pipeline
    ├─ Transcription Module (Replicate API)
    ├─ LLM Integration Module (Anthropic API)
    ├─ Clip Creation Module (FFmpeg)
    └─ Storage Module (AWS S3)
    ↓
External Services
    ├─ Replicate (WhisperX)
    ├─ Anthropic (Claude)
    ├─ AWS (S3)
    └─ FFmpeg (local)
```

### 推荐的 video-ai 架构

```
User Interface Layer (Svelte/Vue/React)
    ↓ (HTTP REST / WebSocket)
API Gateway & Load Balancer
    ↓
Microservices / Processing Pipeline
    ├─ Video Intake Service
    │   ├─ File Validation
    │   └─ Storage Management
    ├─ Transcription Service
    │   ├─ Multi-Engine Support (Whisper, Google, Azure)
    │   └─ Result Caching
    ├─ Intelligence Service
    │   ├─ Multi-LLM Support (Claude, GPT, Gemini, Llama)
    │   └─ Prompt Management
    ├─ Clip Generation Service
    │   ├─ Smart Segmentation
    │   └─ FFmpeg Orchestration
    └─ Output Service
        ├─ Format Conversion
        └─ Delivery Management
```

---

## 2. 核心实现模板

### 2.1 LLM 抽象层（支持多个提供商）

```python
# src/llm/base.py
from abc import ABC, abstractmethod
from typing import Dict, List, Optional

class LLMProvider(ABC):
    """LLM 提供商抽象基类"""
    
    @abstractmethod
    def generate_text(
        self,
        prompt: str,
        max_tokens: int = 2048,
        temperature: float = 0.7
    ) -> str:
        """生成文本"""
        pass
    
    @abstractmethod
    def extract_json(
        self,
        prompt: str,
        schema: Dict
    ) -> Dict:
        """生成 JSON 格式输出"""
        pass

# src/llm/anthropic_provider.py
import anthropic
from .base import LLMProvider

class AnthropicProvider(LLMProvider):
    def __init__(self, api_key: str, model: str = "claude-3-opus-20240229"):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
    
    def generate_text(self, prompt: str, max_tokens: int = 2048, temperature: float = 0.7) -> str:
        message = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return message.content[0].text
    
    def extract_json(self, prompt: str, schema: Dict) -> Dict:
        json_prompt = f"""{prompt}

Return the response as valid JSON matching this schema:
{json.dumps(schema, indent=2)}
"""
        response = self.generate_text(json_prompt)
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            # Fallback 解析
            return self._parse_json_fallback(response, schema)

# src/llm/openai_provider.py
from openai import OpenAI
from .base import LLMProvider

class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str, model: str = "gpt-4"):
        self.client = OpenAI(api_key=api_key)
        self.model = model
    
    def generate_text(self, prompt: str, max_tokens: int = 2048, temperature: float = 0.7) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content

# src/llm/factory.py
from typing import Union
from .base import LLMProvider
from .anthropic_provider import AnthropicProvider
from .openai_provider import OpenAIProvider

class LLMFactory:
    _providers = {
        "anthropic": AnthropicProvider,
        "openai": OpenAIProvider,
    }
    
    @classmethod
    def create(cls, provider: str, **kwargs) -> LLMProvider:
        if provider not in cls._providers:
            raise ValueError(f"Unknown provider: {provider}")
        return cls._providers[provider](**kwargs)
    
    @classmethod
    def register(cls, name: str, provider_class: type):
        cls._providers[name] = provider_class

# 使用示例
llm = LLMFactory.create(
    "anthropic",
    api_key="your-key",
    model="claude-3-opus-20240229"
)

summary = llm.generate_text("Summarize: ...")
topics = llm.extract_json(
    "Extract topics from: ...",
    schema={"topics": [{"title": "", "keywords": []}]}
)
```

### 2.2 转录引擎抽象

```python
# src/transcription/base.py
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List

@dataclass
class TranscriptionSegment:
    start: float
    end: float
    text: str
    speaker: Optional[str] = None
    confidence: float = 1.0

@dataclass
class TranscriptionResult:
    segments: List[TranscriptionSegment]
    language: str
    duration: float

class TranscriptionEngine(ABC):
    """转录引擎抽象"""
    
    @abstractmethod
    async def transcribe(self, audio_path: str) -> TranscriptionResult:
        """转录音频文件"""
        pass

# src/transcription/whisper_local.py
import whisper
from .base import TranscriptionEngine, TranscriptionResult, TranscriptionSegment

class LocalWhisperEngine(TranscriptionEngine):
    """本地 Whisper 引擎"""
    
    def __init__(self, model: str = "base"):
        self.model = whisper.load_model(model)
    
    async def transcribe(self, audio_path: str) -> TranscriptionResult:
        result = self.model.transcribe(audio_path)
        
        segments = [
            TranscriptionSegment(
                start=seg['start'],
                end=seg['end'],
                text=seg['text']
            )
            for seg in result['segments']
        ]
        
        return TranscriptionResult(
            segments=segments,
            language=result['language'],
            duration=result['duration']
        )

# src/transcription/replicate_whisperx.py
import replicate
from .base import TranscriptionEngine, TranscriptionResult, TranscriptionSegment

class ReplicateWhisperXEngine(TranscriptionEngine):
    """Replicate 上的 WhisperX 引擎"""
    
    def __init__(self, api_token: str):
        self.api_token = api_token
    
    async def transcribe(self, audio_path: str) -> TranscriptionResult:
        output = replicate.run(
            "openai/whisper:...",
            input={"audio": open(audio_path, "rb")},
            api_token=self.api_token
        )
        
        # 解析输出
        segments = [
            TranscriptionSegment(
                start=seg['start'],
                end=seg['end'],
                text=seg['text'],
                speaker=seg.get('speaker')
            )
            for seg in output['segments']
        ]
        
        return TranscriptionResult(
            segments=segments,
            language=output['language'],
            duration=output['duration']
        )

# src/transcription/factory.py
from .base import TranscriptionEngine
from .whisper_local import LocalWhisperEngine
from .replicate_whisperx import ReplicateWhisperXEngine

class TranscriptionFactory:
    _engines = {
        "whisper_local": LocalWhisperEngine,
        "whisperx_replicate": ReplicateWhisperXEngine,
    }
    
    @classmethod
    def create(cls, engine_type: str, **kwargs) -> TranscriptionEngine:
        if engine_type not in cls._engines:
            raise ValueError(f"Unknown engine: {engine_type}")
        return cls._engines[engine_type](**kwargs)

# 使用示例
transcriber = TranscriptionFactory.create(
    "whisper_local",
    model="base"
)

result = await transcriber.transcribe("video.mp4")
for segment in result.segments:
    print(f"[{segment.start:.2f}s - {segment.end:.2f}s] {segment.text}")
```

### 2.3 片段创建管道

```python
# src/clips/clip_generator.py
from typing import List, Dict
from dataclasses import dataclass
import json

@dataclass
class Clip:
    title: str
    start: float
    end: float
    keywords: List[str]
    duration: float

class ClipGenerator:
    """智能片段生成器"""
    
    def __init__(self, llm_provider, min_duration: float = 120, max_duration: float = 300):
        self.llm = llm_provider
        self.min_duration = min_duration
        self.max_duration = max_duration
    
    async def generate_clips(
        self,
        transcript: str,
        summary: str,
        max_clips: int = 10
    ) -> List[Clip]:
        """
        生成片段列表
        
        步骤:
        1. 从总结中提取主题
        2. 在转录中找到相关时间段
        3. 验证片段长度和质量
        """
        
        # Step 1: 提取主题
        topics = await self._extract_topics(summary)
        
        # Step 2: 识别时间段
        clips = await self._identify_time_segments(transcript, topics)
        
        # Step 3: 验证和排序
        clips = self._validate_and_sort_clips(clips)
        
        # Step 4: 限制数量
        return clips[:max_clips]
    
    async def _extract_topics(self, summary: str) -> List[Dict]:
        """从总结提取主题"""
        prompt = f"""
        Extract the main topics from this summary:
        
        {summary}
        
        For each topic, provide:
        - title: Brief, descriptive title
        - description: One sentence description
        - keywords: List of relevant keywords
        
        Return as JSON array.
        """
        
        schema = {
            "topics": [
                {
                    "title": "",
                    "description": "",
                    "keywords": []
                }
            ]
        }
        
        return self.llm.extract_json(prompt, schema)["topics"]
    
    async def _identify_time_segments(
        self,
        transcript: str,
        topics: List[Dict]
    ) -> List[Clip]:
        """识别每个主题的时间段"""
        prompt = f"""
        Based on the transcript with timestamps and the topics below,
        identify the time segment for each topic.
        
        Transcript:
        {transcript}
        
        Topics to find:
        {json.dumps(topics, indent=2)}
        
        For each topic, return:
        - title: Topic title
        - start: Start time in seconds
        - end: End time in seconds
        - keywords: Relevant keywords
        
        Requirements:
        - Aim for {self.min_duration}-{self.max_duration} seconds per clip
        - Ensure complete sentences/thoughts
        - Maximize content quality
        
        Return as JSON array.
        """
        
        schema = {
            "clips": [
                {
                    "title": "",
                    "start": 0.0,
                    "end": 0.0,
                    "keywords": []
                }
            ]
        }
        
        clip_data = self.llm.extract_json(prompt, schema)["clips"]
        
        return [
            Clip(
                title=c["title"],
                start=c["start"],
                end=c["end"],
                keywords=c.get("keywords", []),
                duration=c["end"] - c["start"]
            )
            for c in clip_data
        ]
    
    def _validate_and_sort_clips(self, clips: List[Clip]) -> List[Clip]:
        """验证和排序片段"""
        validated = []
        
        for clip in clips:
            # 检查时长
            if clip.duration < self.min_duration * 0.8:
                continue  # 过短
            if clip.duration > self.max_duration * 1.2:
                continue  # 过长
            
            # 检查有效性
            if clip.start >= clip.end:
                continue  # 无效范围
            
            validated.append(clip)
        
        # 按开始时间排序
        return sorted(validated, key=lambda c: c.start)

# 使用示例
generator = ClipGenerator(llm_provider)
clips = await generator.generate_clips(transcript, summary)

for clip in clips:
    print(f"[{clip.start:.1f}s - {clip.end:.1f}s] {clip.title}")
    print(f"  Duration: {clip.duration:.1f}s")
    print(f"  Keywords: {', '.join(clip.keywords)}")
```

---

## 3. 数据处理流程

### 3.1 输入验证

```python
# src/validation/input_validator.py
from typing import Optional
from pathlib import Path
import mimetypes

class VideoValidator:
    """视频输入验证"""
    
    SUPPORTED_FORMATS = {
        '.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv',
        '.m4a', '.mp3', '.wav', '.aac', '.flac'
    }
    
    MAX_FILE_SIZE = 5 * 1024 * 1024 * 1024  # 5GB
    
    @classmethod
    def validate_file(cls, file_path: Path) -> bool:
        """验证文件"""
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # 检查扩展名
        if file_path.suffix.lower() not in cls.SUPPORTED_FORMATS:
            raise ValueError(
                f"Unsupported format: {file_path.suffix}. "
                f"Supported: {cls.SUPPORTED_FORMATS}"
            )
        
        # 检查文件大小
        size = file_path.stat().st_size
        if size > cls.MAX_FILE_SIZE:
            raise ValueError(
                f"File too large: {size / 1e9:.1f}GB. "
                f"Max: {cls.MAX_FILE_SIZE / 1e9:.1f}GB"
            )
        
        # 检查可读性
        if not os.access(file_path, os.R_OK):
            raise PermissionError(f"File not readable: {file_path}")
        
        return True
    
    @classmethod
    def validate_parameters(
        cls,
        transcription_goal: str,
        max_clips: Optional[int] = None
    ) -> bool:
        """验证处理参数"""
        valid_goals = {
            "meeting_minutes",
            "podcast_summary",
            "lecture_notes",
            "interview_highlights",
            "general_transcription"
        }
        
        if transcription_goal not in valid_goals:
            raise ValueError(
                f"Invalid goal: {transcription_goal}. "
                f"Valid: {valid_goals}"
            )
        
        if max_clips is not None:
            if max_clips < 1 or max_clips > 100:
                raise ValueError(
                    f"Invalid max_clips: {max_clips}. "
                    f"Must be 1-100"
                )
        
        return True
```

### 3.2 缓存策略

```python
# src/cache/transcript_cache.py
import hashlib
import json
from pathlib import Path
from typing import Optional

class TranscriptCache:
    """转录结果缓存"""
    
    def __init__(self, cache_dir: Path = Path(".cache/transcripts")):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_cache_key(self, file_path: str) -> str:
        """生成缓存键（基于文件内容哈希）"""
        with open(file_path, 'rb') as f:
            file_hash = hashlib.sha256(f.read()).hexdigest()
        return file_hash
    
    def get(self, file_path: str) -> Optional[Dict]:
        """获取缓存的转录"""
        cache_key = self._get_cache_key(file_path)
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        if cache_file.exists():
            with open(cache_file, 'r') as f:
                return json.load(f)
        return None
    
    def set(self, file_path: str, transcript: Dict) -> None:
        """保存转录到缓存"""
        cache_key = self._get_cache_key(file_path)
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        with open(cache_file, 'w') as f:
            json.dump(transcript, f, indent=2)
    
    def clear(self) -> None:
        """清空缓存"""
        import shutil
        shutil.rmtree(self.cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
```

---

## 4. 错误处理和重试

```python
# src/error_handling/retry_policy.py
import asyncio
from typing import Callable, TypeVar, Optional
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T')

class RetryPolicy:
    """重试策略"""
    
    def __init__(
        self,
        max_retries: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0
    ):
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
    
    async def execute(
        self,
        func: Callable[..., T],
        *args,
        **kwargs
    ) -> T:
        """执行函数，包含重试逻辑"""
        
        delay = self.initial_delay
        last_error = None
        
        for attempt in range(self.max_retries + 1):
            try:
                return await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
            except Exception as e:
                last_error = e
                
                if attempt < self.max_retries:
                    logger.warning(
                        f"Attempt {attempt + 1} failed: {e}. "
                        f"Retrying in {delay:.1f}s..."
                    )
                    await asyncio.sleep(delay)
                    delay = min(delay * self.exponential_base, self.max_delay)
                else:
                    logger.error(f"All {self.max_retries + 1} attempts failed")
        
        raise last_error

# 使用示例
retry_policy = RetryPolicy(max_retries=3)

async def call_api():
    return await retry_policy.execute(
        make_api_request,
        url="https://api.example.com"
    )
```

---

## 5. 配置管理

### 5.1 配置文件结构

```yaml
# config.yaml
app:
  name: "Video AI Summarizer"
  version: "1.0.0"
  environment: "development"  # development, staging, production
  
  # 日志配置
  logging:
    level: "INFO"
    file: "logs/app.log"
    max_size_mb: 100
    backup_count: 10

# 转录服务配置
transcription:
  engine: "whisper_local"  # whisper_local, whisperx_replicate, google_speech
  
  whisper_local:
    model: "base"  # tiny, base, small, medium, large
  
  whisperx_replicate:
    api_token: "${REPLICATE_API_TOKEN}"
    
  google_speech:
    api_key: "${GOOGLE_API_KEY}"
    language: "en-US"

# LLM 配置
llm:
  provider: "anthropic"  # anthropic, openai, gemini
  
  anthropic:
    api_key: "${ANTHROPIC_API_KEY}"
    model: "claude-3-opus-20240229"
    max_tokens: 4096
    temperature: 0.7
  
  openai:
    api_key: "${OPENAI_API_KEY}"
    model: "gpt-4"
    max_tokens: 4096
    temperature: 0.7
  
  gemini:
    api_key: "${GOOGLE_API_KEY}"
    model: "gemini-pro"

# 存储配置
storage:
  backend: "local"  # local, s3, azure_blob
  
  local:
    base_path: "./data"
    max_size_gb: 100
  
  s3:
    bucket: "${AWS_BUCKET}"
    region: "us-east-1"
    access_key: "${AWS_ACCESS_KEY}"
    secret_key: "${AWS_SECRET_KEY}"

# 处理参数
processing:
  clip_min_duration: 120  # seconds
  clip_max_duration: 300  # seconds
  max_clips_per_video: 10
  
  # FFmpeg 配置
  ffmpeg:
    codec: "libx264"
    quality: "medium"  # low, medium, high
    buffer: 0.5  # seconds

# API 配置
api:
  host: "0.0.0.0"
  port: 8000
  debug: false
  cors:
    allowed_origins:
      - "http://localhost:3000"
      - "http://localhost:5173"
```

### 5.2 配置加载器

```python
# src/config/loader.py
from pathlib import Path
from typing import Any, Dict
import yaml
import os

class ConfigLoader:
    """配置加载器"""
    
    def __init__(self, config_path: Path = Path("config.yaml")):
        self.config_path = config_path
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        
        with open(self.config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # 替换环境变量
        config = self._replace_env_vars(config)
        
        return config
    
    @staticmethod
    def _replace_env_vars(obj: Any) -> Any:
        """递归替换环境变量"""
        if isinstance(obj, dict):
            return {k: ConfigLoader._replace_env_vars(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [ConfigLoader._replace_env_vars(v) for v in obj]
        elif isinstance(obj, str) and obj.startswith("${") and obj.endswith("}"):
            env_var = obj[2:-1]
            return os.getenv(env_var, obj)
        return obj
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值（支持点号路径）"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        
        return value

# 使用示例
config = ConfigLoader()
transcription_engine = config.get("transcription.engine")
llm_model = config.get("llm.anthropic.model")
```

---

## 6. 监控和日志

```python
# src/monitoring/logger.py
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

class LoggerConfig:
    """日志配置"""
    
    @staticmethod
    def setup_logging(log_file: Path = Path("logs/app.log"), level=logging.INFO):
        """设置日志系统"""
        
        # 创建日志目录
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 创建日志格式
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # 文件处理器（带轮换）
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=100 * 1024 * 1024,  # 100MB
            backupCount=10
        )
        file_handler.setFormatter(formatter)
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        
        # 配置根日志记录器
        root_logger = logging.getLogger()
        root_logger.setLevel(level)
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)
        
        return root_logger

# 使用示例
logger = logging.getLogger(__name__)
logger.info("Processing started")
logger.warning("API rate limit approaching")
logger.error("Failed to transcribe audio")
```

---

## 7. 实现检查清单

### 核心功能（必须实现）

- [ ] 视频/音频文件上传
- [ ] 转录引擎集成（至少支持2种）
- [ ] LLM 集成（至少支持2个提供商）
- [ ] 智能片段识别
- [ ] 片段导出（MP4 格式）
- [ ] 结果下载（ZIP 格式）
- [ ] 处理进度跟踪
- [ ] 错误处理和日志

### 非功能需求（应该实现）

- [ ] 配置管理系统
- [ ] 缓存机制（转录/LLM 结果）
- [ ] 重试逻辑（指数退避）
- [ ] 输入验证
- [ ] 安全性（避免 shell 注入）
- [ ] 性能监控
- [ ] 单元测试（>80% 覆盖率）
- [ ] 集成测试
- [ ] API 文档（OpenAPI/Swagger）

### 可选增强功能

- [ ] 支持实时处理状态 WebSocket
- [ ] 批量处理队列
- [ ] 自定义 prompt 编辑界面
- [ ] 多语言支持
- [ ] 导出为多种格式（SRT、VTT、PDF）
- [ ] 字幕生成
- [ ] 元数据提取
- [ ] 相似性去重

---

## 8. 性能优化建议

### 8.1 并行处理

```python
# 多个片段的并行 FFmpeg 编码
import concurrent.futures

def create_clips_parallel(clips: List[Clip], video_path: str, max_workers: int = 4):
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(create_single_clip, clip, video_path)
            for clip in clips
        ]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]
    return results
```

### 8.2 异步 I/O

```python
# 使用 aiofiles 进行异步文件操作
import aiofiles

async def save_results_async(results: Dict, output_dir: Path):
    tasks = [
        aiofiles.open(output_dir / "transcript.txt", mode="w"),
        aiofiles.open(output_dir / "summary.txt", mode="w"),
        aiofiles.open(output_dir / "clips.json", mode="w"),
    ]
    
    async with await asyncio.gather(*tasks) as files:
        await files[0].write(results["transcript"])
        await files[1].write(results["summary"])
        await files[2].write(json.dumps(results["clips"]))
```

### 8.3 缓存优化

```python
# 使用 functools.lru_cache
from functools import lru_cache

@lru_cache(maxsize=128)
def get_prompt_template(goal: str) -> str:
    # 缓存 prompt 模板
    return PROMPT_TEMPLATES[goal]
```

---

## 总结

该指南提供了一整套参考实现，可以帮助快速开发 video-ai 项目。关键是：

1. **抽象关键组件**（LLM、转录、存储）以支持多个提供商
2. **实现完善的错误处理和重试机制**
3. **使用配置文件管理所有参数**
4. **添加详细的日志和监控**
5. **编写全面的测试**

这样可以确保项目具有良好的可维护性、可扩展性和可靠性。

