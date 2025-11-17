# AI Video Summarizer 项目深度研究报告

## 执行摘要

**项目地址**: https://github.com/sidedwards/ai-video-summarizer  
**项目简述**: 一个完整的 AI 驱动视频处理系统，集成转录、总结和智能片段创建功能  
**核心技术栈**:
- 后端: Python (61.1%) + FastAPI
- 前端: Svelte (18.4%) + SvelteKit + TypeScript
- 转录: WhisperX (via Replicate API)
- LLM: Anthropic Claude
- 存储: AWS S3
- 视频处理: FFmpeg

---

## 1. 项目架构详解

### 1.1 整体架构图

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (Svelte/SvelteKit)              │
│                     http://localhost:5173                    │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ - File Upload / Goal Selection UI                    │  │
│  │ - Progress Status Display                            │  │
│  │ - Download Generated Content                         │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTP/CORS (localhost:5173)
                     │
┌────────────────────▼────────────────────────────────────────┐
│                Backend (Python/FastAPI)                      │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ endpoints:                                           │  │
│  │ POST   /upload       - 文件上传和处理初始化         │  │
│  │ GET    /status       - 获取处理进度                 │  │
│  │ GET    /download     - 下载处理结果 (ZIP)          │  │
│  │ GET    /download/{f} - 单个文件下载                │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  Processing Pipeline:                                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ 1. S3 Upload Module (s3.py)                          │  │
│  │    - 上传原始文件到 AWS S3                          │  │
│  │    - 生成临时预签名 URL                            │  │
│  │                                                      │  │
│  │ 2. Transcription Module (ai_jobs.py)                │  │
│  │    - 调用 Replicate API (WhisperX)                 │  │
│  │    - 轮询获取转录结果                              │  │
│  │    - 返回结构化的转录数据                          │  │
│  │                                                      │  │
│  │ 3. Content Generation Module (ai_jobs.py)          │  │
│  │    - Anthropic Claude API 调用                      │  │
│  │    - 基于目标类型生成内容                          │  │
│  │    - 支持 5 种总结类型                             │  │
│  │                                                      │  │
│  │ 4. Clip Creation Module (ai_jobs.py)               │  │
│  │    - AI 主题提取                                   │  │
│  │    - 智能时间段识别                                │  │
│  │    - FFmpeg 命令生成                               │  │
│  │                                                      │  │
│  │ 5. Execution Module (cli.py)                        │  │
│  │    - 执行 FFmpeg 命令                              │  │
│  │    - 输出文件组织                                  │  │
│  │    - ZIP 打包下载                                  │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────┘
          │                    │                    │
          ▼                    ▼                    ▼
    ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
    │ AWS S3       │  │ Replicate    │  │ Anthropic    │
    │ (Storage)    │  │ (WhisperX)   │  │ (Claude)     │
    └──────────────┘  └──────────────┘  └──────────────┘
```

### 1.2 核心模块组织结构

```
ai-video-summarizer/
├── backend/
│   ├── __init__.py
│   ├── main.py              # 启动入口 (server 和 CLI 选择)
│   ├── server.py            # FastAPI 服务器定义
│   ├── cli.py               # CLI 入口点 & 工作流编排
│   ├── ai_jobs.py           # 核心处理逻辑 (转录、总结、裁剪)
│   ├── transcription_goal.py # 总结目标枚举
│   ├── s3.py                # AWS S3 交互
│   ├── utils.py             # 工具函数
│   ├── log.py               # 日志和调试
│   └── requirements.txt      # Python 依赖
│
├── frontend/
│   ├── src/
│   │   ├── App.svelte       # 主应用组件
│   │   ├── lib/             # 可复用组件库
│   │   └── routes/          # 页面路由
│   ├── static/              # 静态资源
│   ├── package.json         # Node 依赖
│   ├── svelte.config.js     # Svelte 配置
│   └── vite.config.ts       # Vite 构建配置
│
├── config/
│   └── config.yaml          # API 密钥和配置
│
└── setup.sh                 # 初始化脚本
```

### 1.3 依赖库分析

**Python 依赖** (极简主义):
```
requests==2.32.3    # HTTP 请求库 (调用 Replicate/Anthropic API)
PyYAML==6.0.2       # YAML 配置解析
```

**设计理念**: 最小化依赖，使用原生库处理大多数操作（subprocess, os, json, asyncio）

**Node 依赖** (前端工具链):
```
- SvelteKit 2.0.0          # 全栈框架
- Svelte 4.2.7             # UI 框架
- TypeScript 5.0.0         # 类型安全
- Vite 5.0.3               # 构建工具
- axios 1.7.7              # HTTP 客户端
```

---

## 2. 视频转录实现

### 2.1 Whisper API 集成

**关键要点**:
- 使用 **WhisperX** (OpenAI Whisper 的增强版本) via **Replicate API**
- 优势: WhisperX 支持 **speaker diarization** (说话人识别)

**实现代码流程** (来自 ai_jobs.py):

```python
# 第1步: 启动转录任务
def start_transcription(s3_url, replicate_token, config):
    # 构建 Replicate API 调用
    # 使用 WhisperX 模型处理音频
    # 返回 task_id 用于后续轮询
    pass

# 第2步: 轮询获取结果
def get_transcription_result(task_id, replicate_token, config):
    # 定期检查转录状态
    # 转录完成时返回结构化转录数据
    pass
```

**数据流**:
1. 用户上传视频 → FastAPI /upload 端点
2. 视频上传到 AWS S3
3. 生成 S3 presigned URL
4. 发送到 Replicate API (WhisperX 模型)
5. 轮询等待完成
6. 返回转录数据

### 2.2 音频提取方法

**工具**: FFmpeg (通过 subprocess 调用)

```python
def extract_audio(video_path, output_audio_path):
    """从视频提取音频用于转录"""
    command = f"ffmpeg -i {video_path} -q:a 0 -map a {output_audio_path}"
    subprocess.run(command, shell=True)
```

**支持格式**:
- 视频: `.mp4`, `.avi`, `.mov`
- 音频: `.m4a`, `.mp3`, `.wav`

### 2.3 转录结果数据结构

**关键特性**:
- **分段结构**: 转录分为多个段落 (segments)
- **时间戳信息**: 每个段落都有 `start` 和 `end` 时间戳
- **说话人识别**: WhisperX 提供说话人标签 (speaker diarization)
- **置信度**: 转录置信度评分

**典型结构**:
```json
{
  "segments": [
    {
      "id": 0,
      "seek": 0,
      "start": 0.0,
      "end": 5.5,
      "text": "Transcribed text here...",
      "tokens": [...],
      "temperature": 0.0,
      "avg_logprob": -0.35,
      "compression_ratio": 1.2,
      "no_speech_prob": 0.001,
      "speaker": "SPEAKER_01"  # WhisperX 说话人标签
    },
    // ... 更多段落
  ],
  "language": "en"
}
```

---

## 3. 智能片段创建 (Smart Clips)

### 3.1 关键时刻识别流程

**两阶段 AI 驱动方法**:

#### 阶段1: 主题提取

```python
# 向 Anthropic Claude 发送生成内容
prompt = """
从以下生成的内容中提取每个主要主题或段落。

[生成的内容]

以 JSON 格式返回：
{
  "topics": [
    {
      "title": "主题标题",
      "description": "详细描述",
      "keywords": ["关键词1", "关键词2"]
    }
  ]
}
"""

response = call_anthropic_api(prompt, config)
topics = json.loads(response)  # 有 fallback 正则解析
```

#### 阶段2: 片段边界识别

```python
# 基于主题和原始转录，识别对应的时间段
prompt = f"""
基于以下转录和主题，为每个主题找到对应的时间段：

转录内容：{transcript_text}
主题：{json.dumps(topics)}

要求：
- 每个片段长度 2-5 分钟
- 避免在句子中间切割
- 优先完整讨论内容

返回 JSON：
{{
  "clips": [
    {{
      "topic": "主题名称",
      "start": 123.45,
      "end": 234.56
    }}
  ]
}}
"""
```

### 3.2 片段评分算法

**评分维度**:
1. **内容重要性**: 由 Claude 通过关键词和语义分析判断
2. **段落完整性**: 确保不切割段落中间
3. **时间合理性**: 验证片段长度在目标范围内

**示例流程**:
- Claude 识别转录中与主题相关的句子
- 通过 sentence 的 start/end 时间戳确定片段边界
- 添加 0.5 秒缓冲防止音频断裂
- 生成最终片段列表

### 3.3 片段边界确定

**具体实现** (来自 ai_jobs.py):

```python
def create_media_clips(
    transcript,
    generated_content, 
    source_file,
    destination_folder,
    transcription_goal,
    config
):
    # 步骤 1: 主题提取
    topics = extract_topics_via_ai(generated_content, config)
    
    # 步骤 2: 时间段识别
    clips = identify_clip_segments(transcript, topics, config)
    
    # 步骤 3: FFmpeg 命令生成
    ffmpeg_commands = []
    for clip in clips:
        title = sanitize_filename(clip['topic'])
        start_time = format_timestamp(clip['start'] - 0.5)  # 0.5秒缓冲
        end_time = format_timestamp(clip['end'] + 0.5)
        
        command = (
            f"ffmpeg -i {source_file} "
            f"-ss {start_time} -to {end_time} "
            f"-c copy {destination_folder}/{title}.mp4"
        )
        ffmpeg_commands.append(command)
    
    # 步骤 4: 执行所有命令
    return " && ".join(ffmpeg_commands)
```

**关键特性**:
- `0.5 秒缓冲`: 防止音频或字幕不完整
- `文件名清理`: 移除特殊字符确保文件系统兼容性
- `无损拷贝`: 使用 `-c copy` 避免重新编码，提高速度

---

## 4. LLM 集成

### 4.1 使用的 LLM 及对比

**选择: Anthropic Claude (而非 OpenAI)**

| 方面 | Claude | GPT-4 | 原因 |
|------|--------|-------|------|
| 上下文窗口 | 100K (Claude 3) | 128K | Claude 处理长文本更高效 |
| 成本 | 较低 | 较高 | 成本考虑 |
| API 调用 | 简单 | 类似 | 类似的 API 设计 |
| 延迟 | 中等 | 中等 | 项目非实时场景 |
| JSON 输出 | 支持 | 支持 | 两者都支持 |

### 4.2 Prompt 设计策略

**三层 Prompt 结构**:

#### 1. 总结生成 Prompt

根据 5 种目标类型生成不同的 prompt:

```python
SUMMARIZATION_PROMPTS = {
    TranscriptionGoal.MEETING_MINUTES: """
        From the following transcript, extract:
        1. Main discussion points
        2. Decisions made
        3. Action items with owners
        4. Next steps
        
        Format as structured meeting minutes.
        """,
    
    TranscriptionGoal.PODCAST_SUMMARY: """
        Create an engaging podcast summary including:
        1. Episode overview
        2. Key guests and their expertise
        3. Main topics discussed
        4. Memorable quotes
        5. Resources mentioned
        """,
    
    TranscriptionGoal.LECTURE_NOTES: """
        Format as comprehensive lecture notes:
        1. Main topics and concepts
        2. Key definitions
        3. Examples provided
        4. Important takeaways
        5. Further reading suggestions
        """,
    
    TranscriptionGoal.INTERVIEW_HIGHLIGHTS: """
        Extract interview highlights:
        1. Subject background
        2. Key insights
        3. Notable quotes
        4. Career achievements
        5. Advice and recommendations
        """,
    
    TranscriptionGoal.GENERAL_TRANSCRIPTION: """
        Provide a comprehensive summary covering:
        1. Overview
        2. Main points
        3. Key takeaways
        """
}
```

#### 2. 主题提取 Prompt

```python
TOPIC_EXTRACTION_PROMPT = """
From the provided content, extract each main topic or segment discussed.
For each topic, provide:
- A descriptive title
- A brief description
- Related keywords

Return as JSON with this structure:
{
  "topics": [
    {
      "title": "Topic Title",
      "description": "Description",
      "keywords": ["keyword1", "keyword2"]
    }
  ]
}
"""
```

#### 3. 时间段识别 Prompt

```python
CLIP_SEGMENT_PROMPT = """
Based on the transcript and topics below, identify the time segments 
for each topic in the transcript.

Transcript: [full transcript with timestamps]
Topics: [extracted topics]

Requirements:
- Aim for 2-5 minute clip duration
- Prioritize capturing complete discussion
- Don't cut sentences mid-thought

Return JSON:
{
  "clips": [
    {
      "topic": "Topic Name",
      "start": <timestamp_seconds>,
      "end": <timestamp_seconds>
    }
  ]
}
"""
```

### 4.3 长文本处理策略

**问题**: Claude 100K 上下文虽然很大，但转录文本可能超出

**解决方案**:
1. **文本压缩**: 仅发送关键转录片段给 Claude
2. **分块处理**: 不同目标类型可能需要不同的上下文大小
3. **缓存优化**: Replicate API 可能支持缓存加速重复请求

**实现细节**:
```python
def generate_content(
    transcript,
    transcription_goal,
    config
):
    # 完整转录发送给 Claude
    # Claude 100K 上下文足以处理大多数视频转录
    
    prompt = SUMMARIZATION_PROMPTS[transcription_goal]
    full_prompt = f"{prompt}\n\nTranscript:\n{transcript}"
    
    response = call_anthropic_api(
        full_prompt,
        config,
        max_tokens=4096  # 限制输出大小
    )
    
    return response
```

---

## 5. 值得借鉴的设计模式

### 5.1 代码组织方式

**优点**:
1. **模块化设计**: 每个模块职责单一
   - `ai_jobs.py`: AI 操作
   - `s3.py`: 存储操作
   - `server.py`: API 端点
   - `cli.py`: 命令行

2. **关注点分离**: 
   - 业务逻辑与服务器框架分离
   - 可同时支持 CLI 和 Web 接口

3. **配置外部化**: 
   - `config.yaml` 集中管理所有 API 密钥
   - 支持不同环境的灵活配置

### 5.2 错误处理

**JSON 解析容错机制**:
```python
def extract_topics_via_ai(content, config):
    response = call_anthropic_api(prompt, config)
    
    try:
        # 尝试 JSON 解析
        topics = json.loads(response)
    except json.JSONDecodeError:
        # Fallback: 使用正则提取数据
        topics = extract_via_regex(response)
    
    return topics
```

**特点**:
- 不依赖 API 完美返回 JSON 格式
- 优雅降级而非直接失败
- 提高系统鲁棒性

### 5.3 配置管理

**YAML 配置文件结构**:
```yaml
# Replicate (WhisperX) 配置
replicate:
  api_token: "your-token-here"
  cli_path: "/path/to/replicate"

# AWS S3 配置
aws:
  bucket_name: "your-bucket"
  cli_path: "/path/to/aws"

# Anthropic (Claude) 配置
anthropic:
  api_key: "your-key-here"
  model: "claude-3-opus"

# 应用配置
app:
  upload_folder: "./uploads"
  output_folder: "./outputs"
  temp_folder: "./temp"
```

**优势**:
- 集中管理，易于部署
- 支持环境变量覆盖
- 避免敏感信息在代码中

### 5.4 异步处理架构

**后端处理流程**:
```python
# FastAPI + asyncio 实现非阻塞处理
@app.post("/upload")
async def upload_file(file: UploadFile, goal: str):
    # 保存文件
    # 启动后台任务 (不阻塞响应)
    asyncio.create_task(process_media(file, goal))
    return {"status": "processing", "task_id": task_id}

async def process_media(file, goal):
    # 长时间运行的任务
    # 1. S3 上传
    # 2. 转录
    # 3. 总结
    # 4. 裁剪
    # 更新全局状态对象
```

### 5.5 日志和调试

**分层日志系统**:
```python
# 核心日志
logging.basicConfig(
    level=logging.INFO,
    handlers=[
        RotatingFileHandler("debug.log", maxBytes=10MB, backupCount=5),
        StreamHandler(sys.stdout)
    ]
)

# 调试信息保存
def save_debug_info(output_folder, content, topics, clips):
    debug_data = {
        "generated_content": content,
        "extracted_topics": topics,
        "generated_clips": clips
    }
    with open(f"{output_folder}/debug_info.txt", "w") as f:
        json.dump(debug_data, f, indent=2)
```

---

## 6. 可直接应用到 video-ai 项目的部分

### 6.1 立即可采用

1. **架构参考**
   - 后端 (Python) + 前端 (Svelte/TypeScript) 的分离
   - FastAPI 作为 Web 服务器的选择
   - YAML 配置管理模式

2. **API 集成模式**
   ```python
   # 异步 HTTP 请求模式
   import requests
   
   def call_external_api(url, headers, payload):
       response = requests.post(url, json=payload, headers=headers)
       return response.json()
   
   # 轮询机制处理异步任务
   def poll_for_completion(task_id, check_interval=5, max_retries=1000):
       for attempt in range(max_retries):
           status = get_task_status(task_id)
           if status == "completed":
               return get_result(task_id)
           time.sleep(check_interval)
       raise TimeoutError(f"Task {task_id} did not complete")
   ```

3. **LLM Prompt 设计框架**
   - 保持 prompt 的模块化
   - 为不同使用场景准备预定义 prompts
   - 实现 JSON 解析的容错机制

4. **文件处理最佳实践**
   ```python
   # FFmpeg 命令组织
   def build_ffmpeg_command(input_file, output_file, start, end):
       return [
           "ffmpeg",
           "-i", input_file,
           "-ss", format_timestamp(start),
           "-to", format_timestamp(end),
           "-c", "copy",  # 无损复制
           output_file
       ]
   ```

### 6.2 需要调整的部分

1. **存储方案**
   - 该项目使用 AWS S3，video-ai 可能使用不同的存储
   - 创建抽象层便于切换

2. **转录引擎**
   - 该项目使用 WhisperX (via Replicate)
   - video-ai 可能需要不同的方案（本地 Whisper、Google Speech-to-Text 等）
   - 建议创建统一接口

3. **LLM 选择**
   - 该项目特化于 Anthropic Claude
   - video-ai 可能需要支持多个 LLM（OpenAI、Gemini、Llama 等）
   - 实现 LLM 工厂模式以支持多个提供商

### 6.3 改进建议

1. **错误恢复**
   - 添加重试机制（指数退避）
   - 实现部分失败恢复

2. **性能优化**
   - 缓存转录结果以避免重复处理
   - 并行化独立任务（多个片段的 FFmpeg 编码）

3. **监控和可观测性**
   - 添加更详细的进度跟踪
   - 实现健康检查端点

4. **安全性增强**
   - 避免使用 `shell=True` 在 subprocess 中，改用参数列表
   - 验证和清理用户输入
   - 实现请求速率限制

5. **测试框架**
   - 该项目未显示明显的单元测试
   - 建议添加：
     - 单元测试（pytest）
     - 集成测试（FastAPI TestClient）
     - 端到端测试

---

## 7. 具体代码示例

### 7.1 核心工作流实现 (Python)

```python
# backend/workflow.py
import asyncio
from typing import Dict, List
import json
import requests
import subprocess
from datetime import timedelta

class VideoProcessingWorkflow:
    def __init__(self, config: Dict):
        self.config = config
        self.anthropic_url = "https://api.anthropic.com/v1/messages"
        self.replicate_url = "https://api.replicate.com/v1"
    
    async def process_video(
        self,
        video_path: str,
        transcription_goal: str,
        callback=None
    ) -> Dict:
        """完整的视频处理流程"""
        
        try:
            # Step 1: 上传到 S3
            if callback:
                callback("uploading_to_s3", 10)
            s3_url = self._upload_to_s3(video_path)
            
            # Step 2: 转录
            if callback:
                callback("transcribing", 25)
            transcript = await self._transcribe_audio(s3_url)
            
            # Step 3: 生成内容
            if callback:
                callback("generating_content", 50)
            summary = await self._generate_summary(
                transcript,
                transcription_goal
            )
            
            # Step 4: 创建片段
            if callback:
                callback("creating_clips", 75)
            clips = await self._create_clips(
                transcript,
                summary,
                video_path
            )
            
            if callback:
                callback("completed", 100)
            
            return {
                "transcript": transcript,
                "summary": summary,
                "clips": clips
            }
        
        except Exception as e:
            if callback:
                callback("error", 0, str(e))
            raise
    
    async def _transcribe_audio(self, s3_url: str) -> str:
        """使用 WhisperX 转录"""
        headers = {
            "Authorization": f"Bearer {self.config['replicate']['api_token']}"
        }
        
        payload = {
            "version": "whisperx-model-id",
            "input": {
                "audio": s3_url,
                "language": "en"
            }
        }
        
        # 启动任务
        response = requests.post(
            f"{self.replicate_url}/predictions",
            json=payload,
            headers=headers
        )
        task_id = response.json()["id"]
        
        # 轮询完成
        while True:
            result = requests.get(
                f"{self.replicate_url}/predictions/{task_id}",
                headers=headers
            ).json()
            
            if result["status"] == "succeeded":
                return result["output"]
            elif result["status"] == "failed":
                raise Exception(f"Transcription failed: {result['error']}")
            
            await asyncio.sleep(5)
    
    async def _generate_summary(
        self,
        transcript: str,
        goal: str
    ) -> str:
        """使用 Claude 生成总结"""
        
        prompts = {
            "meeting_minutes": self._get_meeting_prompt(),
            "podcast_summary": self._get_podcast_prompt(),
            # ... 其他类型
        }
        
        prompt = prompts.get(goal, self._get_default_prompt())
        full_prompt = f"{prompt}\n\nTranscript:\n{transcript}"
        
        headers = {
            "x-api-key": self.config['anthropic']['api_key'],
            "content-type": "application/json"
        }
        
        payload = {
            "model": "claude-3-opus-20240229",
            "max_tokens": 4096,
            "messages": [
                {
                    "role": "user",
                    "content": full_prompt
                }
            ]
        }
        
        response = requests.post(
            self.anthropic_url,
            json=payload,
            headers=headers
        )
        
        return response.json()["content"][0]["text"]
    
    async def _create_clips(
        self,
        transcript: str,
        summary: str,
        video_path: str
    ) -> List[Dict]:
        """智能片段创建"""
        
        # Step 1: 提取主题
        topics = await self._extract_topics(summary)
        
        # Step 2: 识别时间段
        clips = await self._identify_clip_segments(
            transcript,
            topics
        )
        
        # Step 3: 生成 FFmpeg 命令并执行
        output_clips = []
        for clip in clips:
            output_path = f"./outputs/{clip['title']}.mp4"
            
            ffmpeg_cmd = [
                "ffmpeg",
                "-i", video_path,
                "-ss", self._seconds_to_timestamp(clip['start'] - 0.5),
                "-to", self._seconds_to_timestamp(clip['end'] + 0.5),
                "-c", "copy",
                output_path
            ]
            
            subprocess.run(ffmpeg_cmd, check=True)
            
            output_clips.append({
                "title": clip['title'],
                "file": output_path,
                "duration": clip['end'] - clip['start']
            })
        
        return output_clips
    
    @staticmethod
    def _seconds_to_timestamp(seconds: float) -> str:
        """转换秒数为 HH:MM:SS.ms 格式"""
        td = timedelta(seconds=seconds)
        total_seconds = int(td.total_seconds())
        milliseconds = int((seconds % 1) * 1000)
        hours, remainder = divmod(total_seconds, 3600)
        minutes, secs = divmod(remainder, 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}.{milliseconds:03d}"
    
    def _upload_to_s3(self, file_path: str) -> str:
        """上传文件到 S3"""
        # 使用 AWS CLI
        bucket = self.config['aws']['bucket_name']
        subprocess.run([
            "aws", "s3", "cp",
            file_path,
            f"s3://{bucket}/uploads/"
        ])
        return f"s3://{bucket}/uploads/{Path(file_path).name}"
    
    def _get_meeting_prompt(self) -> str:
        return """
        From the following transcript, create professional meeting minutes including:
        1. Attendees and key participants
        2. Main discussion points
        3. Decisions made
        4. Action items with owners and deadlines
        5. Next steps and follow-up items
        
        Format using clear sections and bullet points.
        """
    
    def _get_podcast_prompt(self) -> str:
        return """
        Create an engaging podcast episode summary:
        1. Episode title and guest information
        2. Key topics discussed
        3. Main insights and takeaways
        4. Memorable quotes
        5. Resources and links mentioned
        """
    
    def _get_default_prompt(self) -> str:
        return """
        Provide a comprehensive summary covering:
        1. Main overview
        2. Key points discussed
        3. Important takeaways
        """
    
    async def _extract_topics(self, content: str) -> List[Dict]:
        """从内容提取主题"""
        prompt = f"""
        Extract main topics from this content:
        {content}
        
        Return as JSON:
        {{"topics": [{{"title": "...", "keywords": ["...", "..."]}}]}}
        """
        
        headers = {
            "x-api-key": self.config['anthropic']['api_key'],
            "content-type": "application/json"
        }
        
        payload = {
            "model": "claude-3-opus-20240229",
            "max_tokens": 2048,
            "messages": [{"role": "user", "content": prompt}]
        }
        
        response = requests.post(
            self.anthropic_url,
            json=payload,
            headers=headers
        ).json()
        
        text = response["content"][0]["text"]
        
        try:
            return json.loads(text)["topics"]
        except json.JSONDecodeError:
            # Fallback 解析
            return self._parse_topics_from_text(text)
    
    async def _identify_clip_segments(
        self,
        transcript: str,
        topics: List[Dict]
    ) -> List[Dict]:
        """识别每个主题的时间段"""
        prompt = f"""
        Identify time segments in the transcript for each topic.
        
        Transcript: {transcript}
        Topics: {json.dumps(topics)}
        
        Requirements:
        - Each clip 2-5 minutes
        - Don't cut mid-sentence
        - Ensure complete discussion
        
        Return JSON with clips: [{{
            "title": "...",
            "start": <seconds>,
            "end": <seconds>
        }}]
        """
        
        # 调用 Claude API
        # 解析响应...
        # 返回片段列表
        pass
```

### 7.2 FastAPI 服务器实现

```python
# backend/server.py
from fastapi import FastAPI, UploadFile, File, Query
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
from pathlib import Path
from datetime import datetime, timedelta
import zipfile
import io

from workflow import VideoProcessingWorkflow

app = FastAPI(title="Video Summarizer API")

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局状态管理
class ProcessingStatus:
    def __init__(self):
        self.tasks = {}
    
    def create_task(self, task_id: str):
        self.tasks[task_id] = {
            "status": "initializing",
            "progress": 0,
            "error": None,
            "files": []
        }
    
    def update(self, task_id: str, status: str, progress: int, files=None):
        if task_id in self.tasks:
            self.tasks[task_id]["status"] = status
            self.tasks[task_id]["progress"] = progress
            if files:
                self.tasks[task_id]["files"] = files
    
    def get_status(self, task_id: str):
        return self.tasks.get(task_id, {})

status_tracker = ProcessingStatus()

@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    goal: str = Query("general_transcription")
):
    """上传文件开始处理"""
    
    task_id = f"task_{datetime.now().timestamp()}"
    
    # 保存上传的文件
    upload_dir = Path("./uploads")
    upload_dir.mkdir(exist_ok=True)
    
    file_path = upload_dir / file.filename
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)
    
    # 初始化任务状态
    status_tracker.create_task(task_id)
    
    # 启动后台处理
    asyncio.create_task(
        process_video_background(task_id, str(file_path), goal)
    )
    
    return {
        "task_id": task_id,
        "status": "processing"
    }

async def process_video_background(task_id: str, file_path: str, goal: str):
    """后台处理视频"""
    
    from utils import load_config
    
    try:
        config = load_config()
        workflow = VideoProcessingWorkflow(config)
        
        def progress_callback(status: str, progress: int, message: str = ""):
            status_tracker.update(task_id, status, progress)
        
        result = await workflow.process_video(
            file_path,
            goal,
            callback=progress_callback
        )
        
        # 保存结果
        output_dir = Path(f"./outputs/{task_id}")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 保存转录、摘要、片段信息
        with open(output_dir / "transcript.txt", "w") as f:
            f.write(result["transcript"])
        
        with open(output_dir / "summary.txt", "w") as f:
            f.write(result["summary"])
        
        with open(output_dir / "clips.json", "w") as f:
            json.dump(result["clips"], f, indent=2)
        
        # 更新状态
        status_tracker.update(
            task_id,
            "completed",
            100,
            files=[
                "transcript.txt",
                "summary.txt",
                "clips.json"
            ] + [clip["file"] for clip in result["clips"]]
        )
        
        # 设置自动清理（60秒后删除）
        await asyncio.sleep(60)
        import shutil
        shutil.rmtree(output_dir)
    
    except Exception as e:
        status_tracker.update(task_id, "error", 0)
        print(f"Error processing {task_id}: {e}")

@app.get("/status/{task_id}")
async def get_status(task_id: str):
    """获取处理状态"""
    return status_tracker.get_status(task_id)

@app.get("/download/{task_id}")
async def download_results(task_id: str):
    """下载处理结果 (ZIP)"""
    
    output_dir = Path(f"./outputs/{task_id}")
    
    if not output_dir.exists():
        return {"error": "Task not found or already deleted"}
    
    # 创建 ZIP
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zf:
        for file in output_dir.glob("*"):
            zf.write(file, arcname=file.name)
    
    zip_buffer.seek(0)
    
    return StreamingResponse(
        iter([zip_buffer.getvalue()]),
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename={task_id}.zip"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

---

## 8. 总结与建议

### 关键成功因素

1. **模块化设计**: 不同关注点的清晰分离
2. **异步处理**: 避免阻塞长时间运行的操作
3. **容错机制**: JSON 解析降级、重试逻辑
4. **配置管理**: 敏感信息和部署参数的外部化
5. **清晰的 API 设计**: RESTful 端点明确职责

### video-ai 项目建议

| 优先级 | 建议 | 原因 |
|------|------|------|
| P0 | 采用相似的后端-前端分离架构 | 提高开发效率和可维护性 |
| P0 | 实现配置管理系统 | 支持多环境部署 |
| P1 | 设计 LLM 适配器模式 | 支持多个 LLM 提供商灵活切换 |
| P1 | 添加单元测试框架 | 提高代码质量 |
| P2 | 实现详细的监控和日志 | 便于生产环境调试 |
| P2 | 优化 FFmpeg 片段创建性能 | 支持大文件处理 |

---

## 附录: 快速参考

### 环境变量配置
```bash
# 设置 API 密钥
export ANTHROPIC_API_KEY="your-key"
export REPLICATE_API_TOKEN="your-token"
export AWS_BUCKET="your-bucket"

# 运行
python backend/main.py  # CLI 模式
# or
uvicorn backend.server:app --reload  # 服务器模式
```

### 常用 FFmpeg 命令
```bash
# 提取音频
ffmpeg -i video.mp4 -q:a 0 -map a audio.mp3

# 提取片段
ffmpeg -i video.mp4 -ss 00:01:23 -to 00:05:45 -c copy output.mp4

# 批量操作
for file in *.mp4; do
    ffmpeg -i "$file" -ss 0 -to 300 -c copy "clip_${file}"
done
```

### Anthropic API 调用示例
```python
import anthropic

client = anthropic.Anthropic(api_key="your-key")

message = client.messages.create(
    model="claude-3-opus-20240229",
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": "Summarize this: [transcript]"
        }
    ]
)

print(message.content[0].text)
```

