# Video-AI 核心模块使用指南

本文档介绍 video-ai 项目新增的三个核心模块的使用方法。

---

## 目录

1. [LLM 工厂模式](#llm-工厂模式)
2. [增强内容分析器](#增强内容分析器)
3. [NLP 处理器](#nlp-处理器)
4. [快速开始](#快速开始)
5. [注意事项](#注意事项)

---

## LLM 工厂模式

### 概述

LLM 工厂模式提供统一的接口来使用多个 LLM 后端:
- **OpenAI** GPT-4
- **Google** Gemini
- **Anthropic** Claude

### 特性

- ✅ 统一的接口抽象
- ✅ 自动重试机制(指数退避)
- ✅ JSON 容错解析
- ✅ 配置管理
- ✅ 异步支持
- ✅ 错误处理和日志

### 基本使用

#### 1. 创建 LLM 实例

```python
from src.core.llm_factory import LLMFactory

# 方法1: 直接创建
llm = LLMFactory.create(
    provider="openai",  # "openai", "gemini", "claude"
    api_key="your-api-key",
    model="gpt-4-turbo-preview",  # 可选,使用默认模型
    temperature=0.7,
    max_tokens=4096
)

# 方法2: 从配置字典创建
config = {
    "provider": "openai",
    "api_key": "your-api-key",
    "model": "gpt-4-turbo-preview",
    "temperature": 0.7
}
llm = LLMFactory.create_from_config(config)
```

#### 2. 生成文本

```python
import asyncio

async def generate_text():
    # 简单文本生成
    response = await llm.generate(
        prompt="解释什么是机器学习",
        max_tokens=200
    )
    print(response)

asyncio.run(generate_text())
```

#### 3. 生成 JSON

```python
async def generate_json():
    schema = {
        "topics": [
            {
                "title": "",
                "keywords": []
            }
        ]
    }

    result = await llm.generate_json(
        prompt="从这段文字中提取主题...",
        schema=schema
    )

    print(result)  # 自动解析为 Python 字典

asyncio.run(generate_json())
```

### 高级配置

```python
llm = LLMFactory.create(
    provider="openai",
    api_key="your-key",
    model="gpt-4-turbo-preview",
    max_tokens=4096,
    temperature=0.7,
    timeout=60,           # API 超时时间(秒)
    max_retries=3,        # 最大重试次数
    retry_delay=1.0       # 初始重试延迟(秒)
)
```

### 支持的模型

| 提供商 | 默认模型 | 其他可选模型 |
|--------|----------|--------------|
| OpenAI | gpt-4-turbo-preview | gpt-4, gpt-3.5-turbo |
| Gemini | gemini-pro | gemini-pro-vision |
| Claude | claude-3-sonnet-20240229 | claude-3-opus-20240229 |

---

## 增强内容分析器

### 概述

内容分析器集成 LLM 进行深度分析,实现:
- 智能主题提取
- 关键片段识别
- 个性化内容过滤
- 两阶段处理流程

### 特性

- ✅ LLM 深度分析
- ✅ 基础 NLP 分析(无需 API)
- ✅ 两阶段处理:主题提取 → 片段识别
- ✅ 个性化过滤(兴趣/跳过主题)
- ✅ 智能评分系统
- ✅ 自动降级(LLM → NLP)

### 基本使用

#### 1. 创建分析器

```python
from src.core.analyzer import ContentAnalyzer

# 方法1: 使用 LLM(推荐)
analyzer = ContentAnalyzer(
    api_provider="openai",
    api_key="your-api-key",
    model="gpt-4-turbo-preview",
    use_llm=True
)

# 方法2: 仅使用基础 NLP(无需 API)
analyzer = ContentAnalyzer(use_llm=False)

# 方法3: 传入自定义 LLM 实例
from src.core.llm_factory import LLMFactory

llm = LLMFactory.create("openai", "your-key")
analyzer = ContentAnalyzer(llm_provider=llm)
```

#### 2. 分析视频内容

```python
from src.core.transcriber import VideoTranscriber

# 转录视频
transcriber = VideoTranscriber()
transcript = transcriber.transcribe("video.mp4")

# 分析内容
result = analyzer.analyze(
    transcript=transcript,
    user_interests=["人工智能", "机器学习"],  # 用户兴趣
    skip_topics=["广告", "推广"],            # 跳过的主题
    max_segments=10                          # 最多返回片段数
)

# 查看结果
print("主要主题:", result.main_topics)
print("关键词:", result.keywords)
print("摘要:", result.summary)
print("情感:", result.sentiment)

for segment in result.key_segments:
    print(f"\n片段: {segment.topic}")
    print(f"  时间: {segment.start:.1f}s - {segment.end:.1f}s")
    print(f"  相关性: {segment.relevance_score:.2f}")
    print(f"  重要性: {segment.importance_score:.2f}")
    print(f"  理由: {segment.reason}")
```

### 分析结果结构

```python
@dataclass
class AnalysisResult:
    key_segments: List[KeySegment]  # 关键片段列表
    main_topics: List[str]          # 主要主题
    summary: str                    # 内容摘要
    keywords: List[str]             # 关键词
    sentiment: str                  # 情感(positive/negative/neutral)

@dataclass
class KeySegment:
    start: float                    # 开始时间(秒)
    end: float                      # 结束时间(秒)
    text: str                       # 片段文本
    topic: str                      # 主题
    relevance_score: float          # 相关性评分(0-1)
    importance_score: float         # 重要性评分(0-1)
    keywords: List[str]             # 关键词
    reason: Optional[str]           # 选择理由(LLM提供)
```

### Prompt 模板

分析器使用三个核心 Prompt:

1. **主题提取 Prompt**: 从内容中提取 5-10 个主要主题
2. **片段识别 Prompt**: 基于主题和用户兴趣识别关键片段
3. **摘要生成 Prompt**: 生成 200-300 字的内容摘要

可以通过修改源代码中的 Prompt 模板来自定义分析行为。

---

## NLP 处理器

### 概述

NLP 处理器提供基础的文本处理功能,无需 API:
- 关键词提取(TF-IDF, TextRank)
- 主题识别
- 情感分析
- 实体识别
- 中英文支持

### 基本使用

#### 1. 文本预处理

```python
from src.utils.nlp_processor import TextPreprocessor

text = "这个视频讲解了人工智能和机器学习的基础知识"

# 清洁文本
cleaned = TextPreprocessor.clean_text(text)

# 分词
tokens = TextPreprocessor.tokenize(text, language='zh')

# 去停用词
filtered = TextPreprocessor.remove_stopwords(tokens, language='zh')
```

#### 2. 关键词提取

```python
from src.utils.nlp_processor import KeywordExtractor

# 方法1: TF-IDF(适合短文本)
documents = ["文档1", "文档2", "文档3"]
keywords = KeywordExtractor.tfidf(documents, top_n=20, language='zh')

for keyword, score in keywords.items():
    print(f"{keyword}: {score:.3f}")

# 方法2: TextRank(适合长文本)
text = "长文本内容..."
keywords = KeywordExtractor.textrank(text, top_n=20, language='zh')

for keyword, score in keywords.items():
    print(f"{keyword}: {score:.3f}")

# 方法3: 提取短语
tokens = TextPreprocessor.tokenize(text, language='zh')
phrases = KeywordExtractor.extract_phrases(tokens)
```

#### 3. 主题识别

```python
from src.utils.nlp_processor import TopicExtractor

text = "要分析的文本..."

# 识别主题
topics = TopicExtractor.identify_topics(
    text,
    language='zh',
    num_topics=5
)

for topic, weight in topics:
    print(f"{topic}: {weight:.3f}")

# 提取实体
entities = TopicExtractor.extract_entities(text, language='zh')
print("实体:", entities)
```

#### 4. 情感分析

```python
from src.utils.nlp_processor import SentimentAnalyzer

text = "这个视频非常好,讲解得太清楚了!"

sentiment, confidence = SentimentAnalyzer.analyze(text, language='zh')

print(f"情感: {sentiment}")        # positive/negative/neutral
print(f"置信度: {confidence:.3f}")  # 0-1
```

### 语言支持

```python
# 中文
KeywordExtractor.tfidf([text], language='zh')
SentimentAnalyzer.analyze(text, language='zh')

# 英文
KeywordExtractor.tfidf([text], language='en')
SentimentAnalyzer.analyze(text, language='en')
```

---

## 快速开始

### 1. 安装依赖

```bash
cd video-ai
pip install -r requirements.txt

# 可选: 安装中文分词(提升效果)
pip install jieba
```

### 2. 设置环境变量

```bash
# .env 文件
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=...
ANTHROPIC_API_KEY=...
```

### 3. 运行测试

```bash
# 测试 LLM 工厂
python tests/test_llm_factory.py

# 测试 NLP 处理器
python tests/test_nlp_processor.py
```

### 4. 运行示例

```bash
# LLM 使用示例
python examples/llm_usage_example.py
```

### 5. 完整工作流

```python
from src.core.transcriber import VideoTranscriber
from src.core.analyzer import ContentAnalyzer
from src.core.editor import VideoEditor

# 1. 转录视频
transcriber = VideoTranscriber()
transcript = transcriber.transcribe("video.mp4")

# 2. 分析内容
analyzer = ContentAnalyzer(
    api_provider="openai",
    api_key="your-key",
    use_llm=True
)

result = analyzer.analyze(
    transcript,
    user_interests=["AI", "编程"],
    max_segments=10
)

# 3. 生成个性化视频
editor = VideoEditor()
output = editor.create_personalized_video(
    video_path="video.mp4",
    segments=result.key_segments,
    output_path="output.mp4"
)

print(f"视频已生成: {output}")
```

---

## 注意事项

### API 密钥

- OpenAI: https://platform.openai.com/api-keys
- Google Gemini: https://makersuite.google.com/app/apikey
- Anthropic Claude: https://console.anthropic.com/

### 成本控制

LLM API 调用会产生费用:

| 提供商 | 模型 | 输入价格 | 输出价格 |
|--------|------|----------|----------|
| OpenAI | GPT-4 Turbo | $10/1M tokens | $30/1M tokens |
| Gemini | Gemini Pro | 免费(有限额) | 免费(有限额) |
| Claude | Claude 3 Sonnet | $3/1M tokens | $15/1M tokens |

**优化建议**:
1. 使用 `use_llm=False` 进行基础分析(免费)
2. 限制输入文本长度(见代码中的截断逻辑)
3. 缓存分析结果
4. 使用较小的模型(如 `gpt-3.5-turbo`)

### 性能优化

```python
# 1. 使用异步处理
import asyncio

async def process_multiple_videos():
    tasks = [
        analyze_video("video1.mp4"),
        analyze_video("video2.mp4"),
        analyze_video("video3.mp4")
    ]
    results = await asyncio.gather(*tasks)

# 2. 配置重试参数
llm = LLMFactory.create(
    "openai",
    api_key,
    max_retries=3,
    retry_delay=1.0  # 降低延迟
)

# 3. 使用基础分析(更快)
analyzer = ContentAnalyzer(use_llm=False)
```

### 错误处理

```python
try:
    result = analyzer.analyze(transcript)
except Exception as e:
    print(f"分析失败: {e}")

    # 降级到基础分析
    analyzer_basic = ContentAnalyzer(use_llm=False)
    result = analyzer_basic.analyze(transcript)
```

### 日志配置

```python
import logging

# 启用详细日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 或者只启用特定模块的日志
logging.getLogger('src.core.llm_factory').setLevel(logging.DEBUG)
logging.getLogger('src.core.analyzer').setLevel(logging.INFO)
```

---

## 更多资源

- **项目文档**: `/home/user/tvbox1/video-ai/docs/`
- **研究文档**:
  - `AI_VIDEO_SUMMARIZER_RESEARCH.md`
  - `PROMPT_ENGINEERING_GUIDE.md`
  - `RECOMMENDATION_RESEARCH.md`
- **配置文件**: `config.yaml`
- **测试**: `tests/`
- **示例**: `examples/`

---

## 技术支持

如有问题,请参考:
1. 代码注释和文档字符串
2. 测试文件中的示例
3. 研究文档中的最佳实践

---

**更新日期**: 2025-11-17
**版本**: 1.0.0
