# AI Video Summarizer 快速参考卡片

## 项目核心信息

| 项目 | ai-video-summarizer |
|------|-------------------|
| 源地址 | https://github.com/sidedwards/ai-video-summarizer |
| 主语言 | Python (61%) + Svelte (18%) + CSS (15%) |
| 许可证 | MIT |
| Stars | 51 |
| Forks | 11 |

---

## 核心技术栈对比

### 转录层
- **工具**: WhisperX (via Replicate API)
- **优势**: 支持 speaker diarization (说话人识别)
- **输出**: 时间戳分段转录 + 说话人标签

### LLM 层
- **选择**: Anthropic Claude (100K 上下文)
- **备选**: OpenAI GPT-4、Google Gemini
- **关键能力**: JSON 结构化输出、长文本处理

### 存储层
- **方案**: AWS S3 (云存储)
- **备选**: 本地存储、Azure Blob Storage
- **特点**: presigned URL 临时访问

### 处理引擎
- **视频**: FFmpeg (无损片段提取)
- **参数**: `-c copy` (避免重新编码)
- **缓冲**: 0.5 秒 (防止音频断裂)

---

## 关键文件速查

| 文件 | 功能 | 关键代码 |
|------|------|--------|
| `ai_jobs.py` | 核心处理逻辑 | `start_transcription()`, `generate_content()`, `create_media_clips()` |
| `server.py` | FastAPI 服务器 | `@app.post("/upload")`, `@app.get("/status/{task_id}")` |
| `cli.py` | 命令行接口 | `main()`, `execute_ffmpeg_commands()` |
| `s3.py` | AWS 集成 | `upload_to_s3()`, `get_s3_presigned_url()` |
| `transcription_goal.py` | 目标枚举 | 5 种总结类型定义 |

---

## 处理流程时间线

```
用户上传视频
    ↓ (立即)
FastAPI 接收请求，返回 task_id
    ↓ (后台)
[1] S3 上传 (1-5 分钟，取决于文件大小)
[2] WhisperX 转录 (5-30 分钟)
[3] Claude 总结 (1-2 分钟)
[4] 主题提取 (1 分钟)
[5] 片段识别 (2-5 分钟)
[6] FFmpeg 编码 (5-30 分钟)
    ↓
用户下载 ZIP 结果
```

---

## 关键 API 端点

### 上传
```bash
POST /upload
Content-Type: multipart/form-data

{
  "file": <video_file>,
  "goal": "meeting_minutes|podcast_summary|lecture_notes|interview_highlights|general_transcription"
}

Response:
{
  "task_id": "task_1234567890",
  "status": "processing"
}
```

### 获取状态
```bash
GET /status/{task_id}

Response:
{
  "status": "processing|completed|error",
  "progress": 0-100,
  "error": null|"错误信息"
}
```

### 下载结果
```bash
GET /download/{task_id}

Returns: ZIP 文件 (包含所有输出)
```

---

## 5 种总结目标详解

### 1. Meeting Minutes (会议纪要)
- **适用**: 团队会议、项目评审、决策记录
- **输出**: 参与者、讨论要点、决策、行动项
- **格式**: 结构化文档

### 2. Podcast Summary (播客摘要)
- **适用**: 音频访谈、讲座录音、讨论节目
- **输出**: 嘉宾信息、主题、金句、资源链接
- **格式**: 叙事性摘要

### 3. Lecture Notes (讲座笔记)
- **适用**: 在线课程、学术讲座、培训视频
- **输出**: 概念定义、示例、公式、复习题
- **格式**: 学术笔记

### 4. Interview Highlights (采访亮点)
- **适用**: 采访视频、人物故事、专家观点
- **输出**: 背景、观点、故事、建议
- **格式**: 高亮摘要

### 5. General Transcription (通用转录)
- **适用**: 其他所有类型
- **输出**: 基础总结
- **格式**: 简化版本

---

## 智能片段创建算法

### 输入数据
```python
{
  "transcript": "转录文本（带时间戳）",
  "summary": "AI 生成的总结",
  "source_file": "原始视频路径"
}
```

### 处理步骤
```
Step 1: 主题提取
  → 向 Claude 发送总结
  → 解析 JSON 主题列表
  ↓
Step 2: 时间段识别
  → 向 Claude 发送 (转录 + 主题)
  → 获取 start/end 时间戳
  ↓
Step 3: 验证和缓冲
  → 检查时长 (120s-300s)
  → 添加 0.5 秒缓冲
  ↓
Step 4: FFmpeg 编码
  → 生成命令: ffmpeg -i input.mp4 -ss start -to end -c copy output.mp4
  → 执行所有片段编码
  ↓
Step 5: 打包下载
  → 创建 ZIP 档案
  → 添加元数据 (JSON)
```

### 约束条件
- **最小时长**: 2 分钟 (120 秒)
- **最大时长**: 5 分钟 (300 秒)
- **最大片段数**: 10 个
- **缓冲**: 0.5 秒 (段落连接处)

---

## Prompt 工程要点

### 三层 Prompt 结构

| 层级 | 输入 | 输出 | 特点 |
|-----|------|------|------|
| 1 (总结) | 完整转录 | 结构化总结 | 根据目标定制 |
| 2 (主题) | 总结 | JSON 主题列表 | 强制结构化 |
| 3 (片段) | 转录 + 主题 | JSON 时间戳 | 复杂推理 |

### Prompt 模板

```python
# 基础结构
{
  "角色": "专业的 [某领域] 分析师",
  "任务": "从转录中 [具体任务]",
  "约束": [
    "最多/最少 [数字] 项",
    "JSON 格式",
    "避免 [某些内容]"
  ],
  "输出格式": {
    "field1": "类型和说明",
    "field2": ["数组元素类型"]
  },
  "示例": {
    "input": "...",
    "output": {...}
  },
  "输入": "{实际数据}"
}
```

### 容错策略

```python
# 在 prompt 中声明
"如果无法完全确定，返回 null 值"
"如果 JSON 格式失败，使用自然语言，我们有备用解析器"
```

---

## 代码复用清单

### 立即可复用的代码模式

- [ ] **异步 HTTP 调用** (requests 库)
- [ ] **YAML 配置加载** (PyYAML)
- [ ] **JSON 解析容错** (try/except + regex fallback)
- [ ] **FFmpeg 命令生成** (参数化 shell 命令)
- [ ] **文件验证** (路径、大小、格式检查)
- [ ] **轮询机制** (异步任务完成检查)
- [ ] **ZIP 打包** (Python zipfile 模块)

### 需要改进的部分

- [ ] **参数化 FFmpeg** (避免 `shell=True`)
- [ ] **多 LLM 支持** (工厂模式)
- [ ] **多转录引擎** (适配器模式)
- [ ] **缓存机制** (转录结果)
- [ ] **重试逻辑** (指数退避)
- [ ] **单元测试** (pytest)
- [ ] **性能监控** (日志和指标)

---

## 常见问题速解

### Q: 如何处理超大文件?
A: 
1. 使用流式上传到 S3
2. WhisperX 通过 Replicate 处理 (无大小限制)
3. FFmpeg 片段提取也支持大文件

### Q: 如何优化处理速度?
A:
1. 缓存转录结果 (基于文件哈希)
2. 并行化 FFmpeg 片段编码 (ThreadPoolExecutor)
3. 异步 API 调用

### Q: 如何处理不同语言?
A:
1. WhisperX 自动检测语言
2. Claude 可以处理任何语言
3. 在 prompt 中指定输出语言

### Q: 如何处理模型 API 失败?
A:
1. 实现重试机制 (exponential backoff)
2. 使用备选 LLM (OpenAI 作为备选)
3. 本地 Whisper 作为备选转录引擎

---

## 部署检查清单

- [ ] API 密钥配置 (Replicate, Anthropic, AWS)
- [ ] 文件系统权限 (uploads, outputs 目录)
- [ ] FFmpeg 安装验证
- [ ] CORS 配置 (frontend origin)
- [ ] 日志目录创建
- [ ] 临时文件清理策略
- [ ] 错误处理和通知
- [ ] API 速率限制配置
- [ ] 输入验证和清理
- [ ] 安全审计 (SQL 注入、路径遍历等)

---

## 关键指标和 KPI

### 性能指标
- 转录准确度: >95%
- 片段精准度: >90%
- 平均处理时间: <20 分钟
- API 可用性: >99.5%

### 用户体验
- 上传成功率: >99%
- 下载可靠性: 100%
- 错误恢复率: >90%

### 系统资源
- 存储占用: 原始文件 + 转录 + 10 个片段
- CPU 使用: FFmpeg 编码 (可优化为 GPU)
- 内存使用: 较低 (异步处理)

---

## 扩展方向建议

### 短期 (1-2 月)
1. 支持多个 LLM (OpenAI, Gemini)
2. 添加本地 Whisper 选项
3. 实现缓存和重试机制

### 中期 (2-4 月)
1. 支持字幕生成 (SRT/VTT)
2. 自定义 prompt 编辑界面
3. 批量处理队列

### 长期 (4+ 月)
1. 多语言支持和翻译
2. 视频搜索和去重
3. 音视频同步优化
4. 实时处理和流式输出

---

## 参考资源

- **WhisperX**: https://github.com/m-bain/whisperx
- **Replicate**: https://replicate.com/
- **Anthropic Claude**: https://www.anthropic.com/
- **FastAPI**: https://fastapi.tiangolo.com/
- **FFmpeg**: https://ffmpeg.org/

---

## 联系和支持

- GitHub Issue: https://github.com/sidedwards/ai-video-summarizer/issues
- 项目讨论: https://github.com/sidedwards/ai-video-summarizer/discussions

