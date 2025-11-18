# 🚀 Ollama 快速启动指南

使用本地 Ollama 模型，**零成本**运行 Video-AI 智能视频编辑系统！

---

## ⚡ 3 步快速部署

### 1️⃣ 一键启动

```bash
cd video-ai
./start-with-ollama.sh
```

脚本会自动：
- ✅ 创建配置文件
- ✅ 启动所有 Docker 服务
- ✅ 下载 qwen2.5-vl:8b 模型
- ✅ 测试模型可用性

**预计时间：5-10 分钟**（取决于网络速度）

---

### 2️⃣ 验证部署

```bash
python3 test_ollama.py
```

应该看到：
```
[1/5] 测试 Ollama 服务可达性...
  ✅ 服务正常运行

[2/5] 检查模型 'qwen2.5-vl:8b' 是否已下载...
  ✅ 模型已下载

[3/5] 测试 LLM 工厂创建...
  ✅ LLM Provider 创建成功

[4/5] 测试文本生成...
  ✅ 生成成功

[5/5] 测试 JSON 生成...
  ✅ JSON 生成成功

🎉 所有测试通过！
```

---

### 3️⃣ 开始使用

#### 方式 A: 通过 Python API

```python
from src.core.llm_factory import LLMFactory

# 创建 Ollama LLM（会自动读取环境变量配置）
llm = LLMFactory.create(
    provider="ollama",
    api_key="http://localhost:11434",  # Ollama 地址
    model="qwen2.5-vl:8b"
)

# 生成文本
response = await llm.generate("分析这段视频的主要内容...")
print(response)

# 生成 JSON
json_result = await llm.generate_json(
    "提取视频中的关键信息",
    schema={"topics": [], "summary": ""}
)
print(json_result)
```

#### 方式 B: 通过 VideoEditor

```python
from src.core.editor import VideoEditor

# 创建编辑器（自动使用 .env 中的 Ollama 配置）
editor = VideoEditor(
    user_interests=["technology", "AI"],
    output_length="medium"
)

# 处理视频
result = editor.process_video(
    video_path="input.mp4",
    output_path="output.mp4"
)

print(f"✅ 视频处理完成: {result}")
```

#### 方式 C: 通过 REST API

```bash
# 启动 API 服务（如果使用 docker-compose，已经自动启动）
# uvicorn api.main:app --host 0.0.0.0 --port 8000

# 处理视频
curl -X POST http://localhost:8000/api/v1/videos/process \
  -H "Content-Type: application/json" \
  -d '{
    "video_url": "https://youtube.com/watch?v=xxxxx",
    "user_interests": ["technology"],
    "output_length": "medium"
  }'
```

---

## 🎨 切换模型

Ollama 支持多种模型，可以根据需求切换：

### 查看已安装模型

```bash
docker exec -it video-ai-ollama ollama list
```

### 下载其他模型

```bash
# 轻量级模型（更快，但质量稍低）
docker exec -it video-ai-ollama ollama pull qwen2.5:3b
docker exec -it video-ai-ollama ollama pull llama3.2:3b

# 更强大的模型（更慢，但质量更高）
docker exec -it video-ai-ollama ollama pull qwen2.5:14b
docker exec -it video-ai-ollama ollama pull llama3.1:70b

# 多模态模型（支持图像+文本）
docker exec -it video-ai-ollama ollama pull llava:13b
docker exec -it video-ai-ollama ollama pull bakllava:latest
```

### 修改使用的模型

编辑 `.env` 文件：

```bash
# 修改这一行
LLM_MODEL=llama3.2:3b  # 改成你想用的模型

# 重启 API 服务
docker-compose restart api
```

---

## 📊 性能对比

### 不同硬件配置的推理速度

| 硬件 | Token/秒 | 处理 10 分钟视频 | 成本 |
|------|----------|----------------|------|
| **CPU** (Intel i7) | 8-12 | ~15 分钟 | 电费 ~$0.001 |
| **GPU** (RTX 3060) | 35-50 | ~5 分钟 | 电费 ~$0.002 |
| **GPU** (RTX 4090) | 80-120 | ~2 分钟 | 电费 ~$0.003 |
| OpenAI GPT-4 | N/A | ~3 分钟 | API 费用 ~$5-10 |

### 启用 GPU 加速

如果有 NVIDIA GPU，可以大幅提升速度：

1. 安装 NVIDIA Container Toolkit（见 `OLLAMA_SETUP_GUIDE.md`）
2. 修改 `docker-compose.yml`，取消注释 GPU 配置
3. 重启服务：`docker-compose down && docker-compose up -d`

---

## 🔧 常用命令

### 服务管理

```bash
# 查看所有服务状态
docker-compose ps

# 查看日志
docker-compose logs -f ollama    # Ollama 日志
docker-compose logs -f api       # API 日志

# 重启服务
docker-compose restart ollama
docker-compose restart api

# 停止所有服务
docker-compose down

# 完全清理（包括数据）
docker-compose down -v
```

### Ollama 管理

```bash
# 进入 Ollama 容器
docker exec -it video-ai-ollama sh

# 列出模型
docker exec -it video-ai-ollama ollama list

# 删除模型（释放空间）
docker exec -it video-ai-ollama ollama rm qwen2.5:3b

# 测试模型
docker exec -it video-ai-ollama ollama run qwen2.5-vl:8b "你好"

# 查看模型信息
docker exec -it video-ai-ollama ollama show qwen2.5-vl:8b
```

### 性能调优

```bash
# 设置并发数（默认 4）
docker exec -it video-ai-ollama sh -c 'export OLLAMA_NUM_PARALLEL=8'

# 设置最大上下文长度
docker exec -it video-ai-ollama sh -c 'export OLLAMA_MAX_LOADED_MODELS=2'

# 设置 GPU 层数（999 = 全部使用 GPU）
docker exec -it video-ai-ollama sh -c 'export OLLAMA_NUM_GPU=999'
```

---

## 🐛 常见问题

### Q1: 模型下载很慢

**方案 A**: 使用国内镜像（如果可用）

```bash
# 设置 Ollama 镜像地址
export OLLAMA_MODELS=/path/to/models
```

**方案 B**: 手动下载模型文件

从 Hugging Face 或其他镜像站下载后，放到 Ollama 数据目录。

---

### Q2: 内存不足

**方案 A**: 使用更小的模型

```bash
# 3B 模型只需 6GB 内存
docker exec -it video-ai-ollama ollama pull qwen2.5:3b
```

**方案 B**: 增加 Swap 空间

```bash
sudo fallocate -l 16G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

**方案 C**: 使用量化模型

```bash
# Q4 量化，牺牲少许精度换取 40% 内存减少
docker exec -it video-ai-ollama ollama pull qwen2.5:7b-q4_K_M
```

---

### Q3: GPU 不可用

```bash
# 检查 NVIDIA 驱动
nvidia-smi

# 检查 Docker GPU 支持
docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi

# 如果失败，重装 nvidia-container-toolkit
sudo apt-get install --reinstall nvidia-container-toolkit
sudo systemctl restart docker
```

---

### Q4: API 连接 Ollama 失败

```bash
# 检查网络连通性
docker exec -it video-ai-api curl http://ollama:11434/api/tags

# 检查环境变量
docker exec -it video-ai-api env | grep OLLAMA

# 如果都正常，重启服务
docker-compose restart api ollama
```

---

### Q5: 生成的内容质量不好

**调整参数**：

```python
llm = LLMFactory.create(
    provider="ollama",
    api_key="http://localhost:11434",
    model="qwen2.5-vl:8b",
    temperature=0.3,    # 降低随机性（0-1，默认 0.7）
    max_tokens=8192     # 增加输出长度
)
```

**更换更强的模型**：

```bash
docker exec -it video-ai-ollama ollama pull qwen2.5:14b
```

---

## 📈 使用场景推荐

| 场景 | 推荐模型 | 硬件要求 | 优势 |
|------|----------|----------|------|
| **视频分析** | qwen2.5-vl:8b | 16GB RAM | 多模态，理解图像 |
| **中文内容** | qwen2.5:7b | 12GB RAM | 中文优化 |
| **快速预览** | llama3.2:3b | 6GB RAM | 速度快 |
| **高质量输出** | qwen2.5:14b | 32GB RAM | 质量最佳 |
| **资源受限** | phi3:3.8b | 8GB RAM | 小巧高效 |

---

## 🎯 下一步

1. **阅读完整文档**: `OLLAMA_SETUP_GUIDE.md`
2. **查看 API 文档**: http://localhost:8000/docs
3. **运行示例代码**: `python examples/api_client_demo.py`
4. **性能测试**: `pytest tests/test_performance.py`

---

## 💡 提示

- **模型选择**：首次使用建议 qwen2.5-vl:8b（多模态，视频分析效果好）
- **性能优化**：有 GPU 一定要启用，速度提升 3-10 倍
- **成本优势**：本地运行完全免费，大规模使用可节省巨额 API 费用
- **隐私保护**：所有数据都在本地处理，不会上传云端

---

**享受零成本的智能视频编辑体验！** 🎉
