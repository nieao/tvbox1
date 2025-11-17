# Video-AI 核心模块快速指南

本文档介绍如何使用新实现的三个核心模块。

---

## 快速开始

### 1. 安装依赖

```bash
pip install openai google-generativeai anthropic
```

### 2. 设置 API 密钥

```bash
export OPENAI_API_KEY="sk-..."
export GOOGLE_API_KEY="..."
export ANTHROPIC_API_KEY="..."
```

### 3. 基本使用

```python
import asyncio
from src.core.llm_factory import LLMFactory
from src.core.analyzer import ContentAnalyzer

async def main():
    # 创建 LLM
    llm = LLMFactory.create("openai", "your-api-key")

    # 生成文本
    response = await llm.generate("解释机器学习")
    print(response)

asyncio.run(main())
```

---

## 三大核心模块

### 1. LLM 工厂 (`llm_factory.py`)

**支持的后端**: OpenAI, Gemini, Claude

```python
# 创建不同的 LLM
llm_openai = LLMFactory.create("openai", api_key)
llm_gemini = LLMFactory.create("gemini", api_key)
llm_claude = LLMFactory.create("claude", api_key)

# 生成文本
text = await llm.generate("你的提示词")

# 生成 JSON
data = await llm.generate_json("提示词", schema={...})
```

### 2. 内容分析器 (`analyzer.py`)

**功能**: 智能片段识别、主题提取、个性化过滤

```python
from src.core.analyzer import ContentAnalyzer

# 使用 LLM 深度分析
analyzer = ContentAnalyzer(
    api_provider="openai",
    api_key="your-key",
    use_llm=True
)

# 分析视频
result = analyzer.analyze(
    transcript=transcript,
    user_interests=["AI", "编程"],
    max_segments=10
)

# 查看结果
for segment in result.key_segments:
    print(f"{segment.topic}: {segment.start}s - {segment.end}s")
    print(f"评分: {segment.relevance_score:.2f}")
```

### 3. NLP 处理器 (`nlp_processor.py`)

**功能**: 关键词提取、主题识别、情感分析

```python
from src.utils.nlp_processor import KeywordExtractor, SentimentAnalyzer

# 提取关键词(无需 API)
keywords = KeywordExtractor.tfidf([text], top_n=20)

# 情感分析
sentiment, confidence = SentimentAnalyzer.analyze(text)
```

---

## 完整示例

查看 `examples/llm_usage_example.py` 获取完整示例。

---

## 测试

```bash
# 测试 NLP(不需要 API)
python tests/test_nlp_processor.py

# 测试 LLM(需要 API 密钥)
python tests/test_llm_factory.py
```

---

## 文档

- **使用指南**: `docs/CORE_MODULES_USAGE.md`
- **实现报告**: `docs/IMPLEMENTATION_REPORT.md`
- **参考文档**: `docs/IMPLEMENTATION_GUIDE.md`

---

## 关键特性

### LLM 工厂

- ✅ 支持 3 个 LLM 后端
- ✅ 自动重试(指数退避)
- ✅ JSON 容错解析
- ✅ 异步 API

### 内容分析器

- ✅ LLM 深度分析
- ✅ 基础 NLP 分析(免费)
- ✅ 个性化片段识别
- ✅ 双重评分系统

### NLP 处理器

- ✅ TF-IDF 和 TextRank
- ✅ 主题识别
- ✅ 情感分析
- ✅ 中英文支持

---

## 注意事项

### API 成本

LLM API 调用会产生费用:
- GPT-4: ~$0.10-0.20 / 10分钟视频
- Gemini: 免费(有限额)
- Claude: ~$0.05-0.10 / 10分钟视频

**节省成本**:
1. 使用 `use_llm=False` (免费 NLP 模式)
2. 使用 Gemini 免费额度
3. 实现缓存机制

### 性能优化

```python
# 使用异步并行处理
import asyncio

async def process_videos(video_paths):
    tasks = [analyze_video(path) for path in video_paths]
    results = await asyncio.gather(*tasks)
    return results
```

---

## 故障排除

### 导入错误

```python
# 确保在项目根目录
import sys
sys.path.insert(0, '/home/user/tvbox1/video-ai')

from src.core.llm_factory import LLMFactory
```

### API 错误

```python
# 检查 API 密钥
import os
print(os.getenv('OPENAI_API_KEY'))

# 使用降级模式
analyzer = ContentAnalyzer(use_llm=False)
```

---

## 下一步

1. 阅读完整使用指南: `docs/CORE_MODULES_USAGE.md`
2. 运行示例代码: `examples/llm_usage_example.py`
3. 查看实现报告: `docs/IMPLEMENTATION_REPORT.md`

---

**更新**: 2025-11-17
**版本**: 1.0.0
**状态**: ✅ 生产就绪
