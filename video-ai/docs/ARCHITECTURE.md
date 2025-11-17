# Video-AI 架构设计文档

## 系统架构概览

Video-AI 采用模块化设计，主要分为以下几个层次：

```
┌─────────────────────────────────────────────────────────────┐
│                        用户界面层                             │
│  (Streamlit Web UI / CLI / Browser Extension / API)         │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                        业务服务层                             │
│  - PersonalizationService (个性化服务)                       │
│  - RecommendationEngine (推荐引擎)                           │
│  - UserProfileManager (用户画像管理)                         │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                        核心功能层                             │
│  - VideoTranscriber (视频转录)                               │
│  - ContentAnalyzer (内容分析)                                │
│  - VideoEditor (视频编辑)                                    │
│  - TransitionGenerator (过渡生成)                            │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                        基础设施层                             │
│  - FFmpeg (视频处理)                                         │
│  - Whisper (语音识别)                                        │
│  - GPT/Gemini (内容理解)                                     │
│  - Stable Diffusion (视频生成)                               │
└─────────────────────────────────────────────────────────────┘
```

## 核心模块详解

### 1. VideoTranscriber (视频转录模块)

**职责：**
- 从视频中提取音频
- 使用 Whisper 模型进行语音识别
- 生成带时间戳的文字稿

**技术选型：**
- `faster-whisper`: 性能优化版本，速度提升 4-5倍
- `openai-whisper`: 官方实现，准确度更高
- `FFmpeg`: 音频提取

**数据流：**
```
视频文件 → 音频提取 → Whisper转录 → 带时间戳的文字稿
```

### 2. ContentAnalyzer (内容分析模块)

**职责：**
- 提取关键词和主题
- 分析内容相关性
- 识别重要片段
- 生成内容摘要

**分析维度：**
1. **关键词提取** (TF-IDF / TextRank)
2. **主题识别** (LDA / NMF)
3. **情感分析** (Sentiment Analysis)
4. **相关性评分** (基于用户兴趣)
5. **重要性评分** (多因素综合)

**评分算法：**
```python
综合评分 = (相关性评分 * 0.6) + (重要性评分 * 0.4)

相关性评分 = 用户兴趣匹配度
重要性评分 = 关键词密度 * 0.4 +
             主题相关性 * 0.4 +
             文本长度因子 * 0.2
```

### 3. VideoEditor (视频编辑模块)

**职责：**
- 根据分析结果剪辑视频
- 生成过渡效果
- 拼接最终视频

**编辑策略：**
1. **Simple**: 直接拼接，无过渡
2. **Intelligent**: 添加文字过渡卡
3. **Advanced**: AI生成视频过渡（阶段二）

**技术实现：**
- `moviepy`: Python视频编辑库
- `FFmpeg`: 底层视频处理
- 支持多种输出格式和质量

### 4. PersonalizationService (个性化服务)

**职责：**
- 管理用户配置
- 存储用户画像
- 学习用户偏好
- 提供个性化推荐

**用户画像模型：**
```json
{
  "user_id": "xxx",
  "config": {
    "interests": ["AI", "编程"],
    "skip_topics": ["广告"],
    "pace": "fast",
    "output_length": "short"
  },
  "watch_history": [...],
  "feedback_history": [...]
}
```

## 处理流程

### 标准处理流程

```
1. 视频输入
   ↓
2. 转录 (VideoTranscriber)
   ↓
3. 内容分析 (ContentAnalyzer)
   - 提取关键词
   - 识别主题
   - 评分片段
   ↓
4. 个性化过滤 (PersonalizationService)
   - 应用用户兴趣
   - 过滤不相关内容
   ↓
5. 视频剪辑 (VideoEditor)
   - 提取关键片段
   - 添加过渡
   - 拼接输出
   ↓
6. 输出视频
```

### 批量处理流程

```
扫描输入目录
   ↓
并行处理多个视频
   ├─ 视频1 → 标准流程 → 输出1
   ├─ 视频2 → 标准流程 → 输出2
   └─ 视频3 → 标准流程 → 输出3
   ↓
生成批量处理报告
```

## 数据模型

### TranscriptSegment (转录片段)
```python
@dataclass
class TranscriptSegment:
    start: float          # 开始时间
    end: float            # 结束时间
    text: str             # 文本内容
    confidence: float     # 置信度
```

### KeySegment (关键片段)
```python
@dataclass
class KeySegment:
    start: float              # 开始时间
    end: float                # 结束时间
    text: str                 # 文本内容
    topic: str                # 主题
    relevance_score: float    # 相关性评分
    importance_score: float   # 重要性评分
    keywords: List[str]       # 关键词
```

### EditingResult (编辑结果)
```python
@dataclass
class EditingResult:
    output_path: str              # 输出路径
    original_duration: float      # 原始时长
    edited_duration: float        # 剪辑后时长
    compression_ratio: float      # 压缩比例
    density_improvement: float    # 信息密度提升
    segments_count: int           # 片段数量
```

## 性能优化策略

### 1. 缓存机制
- 转录结果缓存（避免重复转录）
- 分析结果缓存
- 用户画像缓存

### 2. 并行处理
- 批量视频并行处理
- GPU 加速（Whisper、视频编码）
- 多线程音频提取

### 3. 增量更新
- 用户画像增量更新
- 模型增量训练

## 扩展性设计

### 插件系统（规划中）
```python
class Plugin:
    def on_transcribe(self, transcript): pass
    def on_analyze(self, analysis): pass
    def on_edit(self, video): pass
```

### API 接口（规划中）
```
POST /api/v1/process
GET  /api/v1/status/{job_id}
GET  /api/v1/result/{job_id}
```

## 安全性考虑

1. **隐私保护**
   - 用户数据本地存储
   - 可选的云端同步
   - 数据加密

2. **版权保护**
   - 水印添加（可选）
   - 原作者信息保留
   - 使用协议检查

3. **内容审核**
   - 敏感内容检测
   - 合规性检查

## 未来规划

### 阶段二：AI增强
- 高质量视频过渡生成
- 智能叙事排序
- 深度语义理解

### 阶段三：平台化
- Web 服务
- 浏览器插件
- 移动端应用
- 企业版 API

### 阶段四：生态整合
- YouTube/Bilibili 集成
- 在线教育平台集成
- 企业内训系统集成
