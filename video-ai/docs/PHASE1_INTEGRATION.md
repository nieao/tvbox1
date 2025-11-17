# Video-AI 阶段一整合方案

## 研究成果总结

基于对三个优秀开源项目的深入研究，我们已经获得了以下核心技术和代码：

### 📦 研究成果统计

- **研究文档**: 14份，约 220KB
- **可执行代码**: 2000+ 行
- **示例代码**: 450+ 行
- **研究总投入**: 3个并行 subagent

---

## 一、ai-video-summarizer 核心发现

### ✅ 可直接借鉴的优点

#### 1. **三层处理架构**
```
视频 → 转录层(WhisperX) → LLM层(Claude) → 片段层(Smart Clips)
```

**优势**：
- 清晰的职责分离
- 易于扩展和维护
- 支持多种 LLM 后端

**应用到 video-ai**：
- 采用类似的分层架构
- 实现 LLM 工厂模式
- 支持 OpenAI、Gemini、Anthropic

#### 2. **Prompt 工程技巧**

**6种专业 Prompt 模板**：
1. 详细总结（章节结构）
2. 简短总结（执行摘要）
3. 主题提取（结构化输出）
4. 关键片段识别（时间戳）
5. 问答对生成（学习材料）
6. 自定义目标

**核心技巧**：
- JSON 输出强制格式
- 容错解析（fallback机制）
- 上下文窗口管理（100K token）

**应用策略**：
```python
# 片段识别 Prompt 模板
SEGMENT_PROMPT = """
基于以下转录内容和用户兴趣，识别最相关的视频片段。

用户兴趣: {interests}
转录内容: {transcript}

请返回 JSON 格式：
{
  "segments": [
    {
      "start_time": "MM:SS",
      "end_time": "MM:SS",
      "topic": "主题",
      "relevance_score": 0.0-1.0,
      "reason": "选择理由"
    }
  ]
}
"""
```

#### 3. **智能片段创建算法**

**关键参数**：
- 时长约束: 2-5 分钟
- 缓冲时间: 0.5 秒（防止音频断裂）
- 段落边界: AI 自动识别

**两阶段处理**：
1. **主题提取**: 识别视频的主要话题
2. **时间段映射**: 将主题映射到具体时间范围

**代码参考**：
```python
async def create_smart_clips(transcript, topics, min_duration=120, max_duration=300):
    """
    创建智能片段

    Args:
        transcript: 带时间戳的转录
        topics: 主题列表
        min_duration: 最小时长（秒）
        max_duration: 最大时长（秒）
    """
    clips = []
    for topic in topics:
        # 使用 LLM 识别该主题的时间范围
        time_ranges = await identify_topic_ranges(transcript, topic)

        for start, end in time_ranges:
            duration = end - start

            # 添加缓冲
            start = max(0, start - 0.5)
            end = end + 0.5

            # 时长控制
            if min_duration <= duration <= max_duration:
                clips.append({
                    'start': start,
                    'end': end,
                    'topic': topic,
                    'duration': duration
                })

    return clips
```

#### 4. **模块化代码组织**

**目录结构**：
```
src/
├── core/
│   ├── transcription_engine.py    # 转录引擎抽象
│   ├── llm_factory.py             # LLM 工厂模式
│   └── clip_generator.py          # 片段生成器
├── services/
│   └── summarization_service.py   # 总结服务
└── utils/
    ├── audio_processor.py         # 音频处理
    └── json_parser.py             # JSON 容错解析
```

**应用到 video-ai**：
- ✅ 已实现基础结构
- 🔄 需要添加 LLM 工厂和转录引擎抽象

---

## 二、latentblending 核心发现

### ✅ 可应用的技术

#### 1. **核心技术原理**

**潜在空间混合**：
- 在 Stable Diffusion 的潜在空间中进行插值
- 使用球面线性插值（SLERP）保证平滑
- LPIPS 自适应分支插入优化过渡质量

**简化理解**：
```
图像A → Encoder → 潜在向量A ──┐
                              SLERP混合 → 潜在向量C → Decoder → 过渡帧
图像B → Encoder → 潜在向量B ──┘
```

#### 2. **性能指标（RTX 4090）**

| 配置 | 帧数 | 时间 | 内存 | 适用场景 |
|------|------|------|------|----------|
| MVP  | 5帧  | 15秒 | 10GB | 快速原型 |
| 平衡 | 10帧 | 45秒 | 11GB | **推荐** ⭐ |
| 高质 | 20帧 | 120秒 | 12GB | 高质量输出 |

#### 3. **MVP 实现方案**

**阶段一：简单过渡**（当前实现）
- 使用文字卡片过渡
- 黑屏淡入淡出
- 成本：几乎为 0

**阶段二：AI 过渡**（后续计划）
```python
from latentblending import LatentBlending

# 简化配置
lb = LatentBlending(
    model_name="stabilityai/sdxl-turbo",  # 快速模型
    num_inference_steps=5,                # MVP: 5步
    guidance_scale=1.0,                   # SDXL Turbo 无需引导
    height=512, width=512                 # 降低分辨率
)

# 生成过渡
transition_frames = lb.run_transition(
    prompt_start="视频片段A的最后一帧",
    prompt_end="视频片段B的第一帧",
    num_frames=5  # MVP: 5帧
)
```

#### 4. **集成建议**

**优先级 P2（阶段二）**：
- 当前不阻塞 MVP 发布
- 预计集成时间：2-3周
- GPU 要求：至少 8GB VRAM

---

## 三、YT-Recommendation 核心发现

### ✅ 已集成的模块

#### 1. **混合推荐引擎** (`src/services/recommendation.py`)

**核心算法**：
```python
综合评分 = CF评分 × 0.40 +     # 协同过滤
           CB评分 × 0.35 +     # 内容推荐
           Pop评分 × 0.15 +    # 流行度
           Div评分 × 0.10      # 多样性
```

**特性**：
- 407 行生产级代码
- 支持冷启动（新用户）
- 多样性控制
- 探索-利用平衡

#### 2. **NLP 处理器** (`src/utils/nlp_processor.py`)

**功能模块**：
- 关键词提取（TF-IDF、TextRank、YAKE）
- 主题识别（LDA）
- 实体识别（NER）
- 情感分析

**应用场景**：
```python
from video_ai.utils.nlp_processor import NLPProcessor

processor = NLPProcessor()

# 分析转录文本
keywords = processor.extract_keywords(transcript, method='textrank', top_n=20)
topics = processor.identify_topics(transcript, num_topics=5)
sentiment = processor.analyze_sentiment(transcript)
entities = processor.extract_entities(transcript)
```

#### 3. **用户画像模型** (`src/models/user_profile.py`)

**7维特征**：
1. 兴趣标签（加权）
2. 观看历史
3. 跳过主题
4. 参与度评分
5. 忠诚度评分
6. 活跃度评分
7. 偏好设置

**动态更新**：
```python
# 指数移动平均更新兴趣
new_interest_score = α × current + (1-α) × historical
```

---

## 四、整合实施计划

### 🎯 阶段一 MVP 功能清单

#### ✅ 已完成（基础框架）
- [x] 项目结构搭建
- [x] 基础转录功能
- [x] 简单内容分析
- [x] 视频剪辑引擎
- [x] 个性化配置
- [x] 推荐系统模块
- [x] NLP 处理器
- [x] 用户画像模型

#### 🔄 进行中（增强功能）
- [ ] LLM 工厂模式（支持多后端）
- [ ] 转录引擎抽象层
- [ ] 智能片段评分优化
- [ ] YouTube 视频下载
- [ ] Web UI 界面
- [ ] 完整测试流程

---

## 五、技术栈最终确定

### 核心依赖

```yaml
# AI 模型
openai: ">=1.3.0"              # GPT-4
google-generativeai: ">=0.3.0"  # Gemini
anthropic: ">=0.7.0"            # Claude (可选)

# 视频处理
moviepy: ">=1.0.3"
ffmpeg-python: ">=0.2.0"
opencv-python: ">=4.8.0"

# 转录
openai-whisper: ">=20231117"
faster-whisper: ">=0.9.0"       # 推荐

# NLP
nltk: ">=3.8.1"
spacy: ">=3.7.0"
scikit-learn: ">=1.3.0"         # TF-IDF
gensim: ">=4.3.0"               # LDA

# Web 框架
fastapi: ">=0.104.0"
streamlit: ">=1.28.0"

# YouTube 支持
yt-dlp: ">=2023.11.16"
youtube-transcript-api: ">=0.6.1"

# 推荐系统
numpy: ">=1.24.0"
pandas: ">=2.1.0"
scipy: ">=1.11.0"
```

### 可选依赖（阶段二）

```yaml
# AI 视频生成
diffusers: ">=0.24.0"           # Stable Diffusion
accelerate: ">=0.25.0"          # GPU 加速
torch: ">=2.1.0"                # PyTorch
```

---

## 六、开发路线图（4周计划）

### Week 1: 核心功能增强

**目标**: 完善转录和分析功能

- [ ] 实现 LLM 工厂模式
  - OpenAI GPT-4 集成
  - Google Gemini 集成
  - 统一接口抽象

- [ ] 优化内容分析
  - 集成 TextRank 关键词提取
  - LDA 主题识别
  - 基于 LLM 的片段评分

- [ ] YouTube 集成
  - yt-dlp 视频下载
  - 字幕/转录获取
  - 元数据提取

**验收标准**:
```bash
# 能够处理 YouTube 视频
python -m video_ai.cli process \
  --url "https://youtube.com/watch?v=xxx" \
  --interests "AI,编程" \
  --output "output.mp4"
```

---

### Week 2: 智能剪辑优化

**目标**: 实现生产级剪辑质量

- [ ] 智能片段边界检测
  - 场景检测（OpenCV）
  - 静音检测（FFmpeg）
  - 句子边界对齐

- [ ] 评分系统升级
  - 5因素综合评分
  - 基于 LLM 的相关性判断
  - 用户反馈学习

- [ ] 过渡效果增强
  - 5种文字模板
  - 淡入淡出效果
  - 音频平滑处理

**验收标准**:
- 片段切换自然流畅
- 音频无断裂
- 叙事逻辑连贯

---

### Week 3: Web UI 开发

**目标**: 提供友好的用户界面

- [ ] Streamlit 主界面
  - 视频上传/URL 输入
  - 兴趣标签配置
  - 实时处理进度

- [ ] 预览功能
  - 片段列表展示
  - 时间线可视化
  - 片段拖拽排序

- [ ] 结果展示
  - 视频播放器
  - 统计数据可视化
  - 导出选项

**界面原型**:
```
┌─────────────────────────────────────────┐
│  Video-AI - 个性化视频编辑              │
├─────────────────────────────────────────┤
│  [输入]                                 │
│  📹 上传视频 或 🔗 YouTube URL          │
│  ┌───────────────────────────────────┐ │
│  │ https://youtube.com/watch?v=...   │ │
│  └───────────────────────────────────┘ │
│                                         │
│  [配置]                                 │
│  🏷️ 兴趣标签: [AI] [编程] [+添加]     │
│  ⏱️ 输出长度: ○短 ●中 ○长             │
│  🎨 过渡风格: ●文字 ○简单 ○AI生成     │
│                                         │
│  [开始处理] ▶️                          │
├─────────────────────────────────────────┤
│  处理进度: ████████░░ 80%               │
│  📝 转录中... ✅                         │
│  🧠 分析中... ✅                         │
│  ✂️ 剪辑中... 🔄                        │
└─────────────────────────────────────────┘
```

---

### Week 4: 测试与优化

**目标**: 确保生产就绪

- [ ] 单元测试
  - 转录模块测试
  - 分析模块测试
  - 剪辑模块测试

- [ ] 集成测试
  - 完整流程测试
  - 边界情况测试
  - 错误恢复测试

- [ ] 性能优化
  - 缓存机制
  - 并行处理
  - 内存优化

- [ ] 文档完善
  - API 文档
  - 使用教程
  - 故障排除指南

**验收标准**:
- 测试覆盖率 > 80%
- 端到端处理成功率 > 95%
- 10分钟视频处理时间 < 3分钟

---

## 七、快速开始指南

### 安装依赖

```bash
cd video-ai
pip install -r requirements.txt

# 下载 spaCy 模型
python -m spacy download zh_core_web_sm
python -m spacy download en_core_web_sm

# 下载 NLTK 数据
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

### 配置 API 密钥

```bash
# 创建 .env 文件
cat > .env <<EOF
OPENAI_API_KEY=sk-your-openai-key
GOOGLE_API_KEY=your-google-key
EOF
```

### 运行示例

```bash
# 基础示例
python examples/basic_demo.py

# 推荐系统演示
python examples/recommendation_demo.py

# Web UI
streamlit run examples/web_ui.py
```

---

## 八、成功指标

### MVP 阶段（阶段一结束）

**功能完整性**:
- ✅ 支持 YouTube 视频处理
- ✅ 智能片段识别准确率 > 80%
- ✅ 用户满意度 > 4.0/5.0

**性能指标**:
- ✅ 10分钟视频处理 < 5分钟
- ✅ 压缩率 30-70%
- ✅ 信息密度提升 > 50%

**技术债务**:
- ✅ 测试覆盖率 > 70%
- ✅ 代码文档完整
- ✅ 关键路径无已知 bug

---

## 九、风险与应对

| 风险 | 概率 | 影响 | 应对策略 |
|------|------|------|----------|
| LLM API 成本过高 | 中 | 高 | 缓存转录结果，批量处理 |
| 视频处理速度慢 | 高 | 中 | GPU 加速，异步处理队列 |
| 片段识别不准确 | 中 | 高 | 用户反馈循环，持续优化 |
| YouTube API 限流 | 低 | 中 | 配额监控，降级方案 |
| 开源库兼容性 | 低 | 低 | 依赖版本锁定，CI/CD |

---

## 十、下一步行动

### 立即执行（今天）

1. **安装完整依赖**
   ```bash
   pip install -r requirements.txt
   ```

2. **配置 API 密钥**
   - 获取 OpenAI API key
   - 获取 Google API key

3. **运行测试**
   ```bash
   python examples/recommendation_demo.py
   ```

### 本周目标

- [ ] 实现 LLM 工厂模式
- [ ] 集成 YouTube 下载
- [ ] 优化关键词提取

### 本月目标

- [ ] 完成 Web UI
- [ ] 完整测试流程
- [ ] MVP 正式发布

---

**所有研究文档位置**: `/home/user/tvbox1/video-ai/docs/`

**核心代码已就绪，现在开始实施！** 🚀
