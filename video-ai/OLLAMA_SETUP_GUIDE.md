# Ollama 本地 LLM 部署指南

本指南介绍如何使用本地 Ollama 运行 qwen2.5-vl:8b 模型，完全替代云端 API，实现零成本 LLM 推理。

---

## 🎯 优势

✅ **零成本** - 无需 API Key，完全本地运行
✅ **隐私保护** - 数据不上传云端
✅ **低延迟** - 本地推理速度快
✅ **离线可用** - 无需互联网连接
✅ **多模型支持** - 可切换不同模型

---

## 📋 前置要求

### 硬件要求

**最低配置（qwen2.5-vl:8b）：**
- CPU: 8核+
- RAM: 16GB+
- 磁盘: 10GB+ 可用空间

**推荐配置（GPU 加速）：**
- GPU: NVIDIA RTX 3060+ (8GB+ VRAM)
- RAM: 32GB+
- 磁盘: 50GB+ SSD

### 软件要求

- Docker 20.10+
- Docker Compose 1.29+
- （可选）NVIDIA Docker Runtime（GPU 加速）

---

## 🚀 快速部署

### 方法一：使用 Docker Compose（推荐）

#### 1. 配置环境变量

```bash
cd video-ai
cp .env.example .env

# 编辑 .env，确保以下配置
nano .env
```

**.env 配置：**
```bash
# LLM 配置 - 使用本地 Ollama
LLM_PROVIDER=ollama
LLM_MODEL=qwen2.5-vl:8b
OLLAMA_BASE_URL=http://ollama:11434

# 数据库密码
DB_PASSWORD=your_strong_password
MONGO_PASSWORD=your_strong_password
REDIS_PASSWORD=your_strong_password

# 其他 API Keys 可以留空或删除
# OPENAI_API_KEY=
# GOOGLE_API_KEY=
# ANTHROPIC_API_KEY=
```

#### 2. 启动所有服务

```bash
# 启动服务（包含 Ollama）
docker-compose up -d

# 查看 Ollama 日志
docker-compose logs -f ollama
```

#### 3. 下载模型

```bash
# 等待 Ollama 容器启动完成（约10秒）
sleep 10

# 拉取 qwen2.5-vl:8b 模型（约5GB，需要几分钟）
docker exec -it video-ai-ollama ollama pull qwen2.5-vl:8b

# 或使用你想要的模型
# docker exec -it video-ai-ollama ollama pull qwen2.5:7b
# docker exec -it video-ai-ollama ollama pull llama3.2:latest
```

#### 4. 验证部署

```bash
# 测试 Ollama 服务
curl http://localhost:11434/api/tags

# 测试模型推理
curl http://localhost:11434/api/generate -d '{
  "model": "qwen2.5-vl:8b",
  "prompt": "为什么天空是蓝色的？",
  "stream": false
}'

# 测试 API 服务
curl http://localhost:8000/health
```

---

### 方法二：本地安装 Ollama

如果不使用 Docker，可以直接在主机上安装：

#### Linux

```bash
# 下载并安装 Ollama
curl -fsSL https://ollama.com/install.sh | sh

# 启动 Ollama 服务
ollama serve &

# 拉取模型
ollama pull qwen2.5-vl:8b

# 测试模型
ollama run qwen2.5-vl:8b "你好，介绍一下你自己"
```

#### macOS

```bash
# 使用 Homebrew
brew install ollama

# 或下载安装包
# https://ollama.com/download/mac

# 启动服务
ollama serve &

# 拉取模型
ollama pull qwen2.5-vl:8b
```

#### Windows

1. 下载安装程序: https://ollama.com/download/windows
2. 运行安装程序
3. 打开命令提示符或 PowerShell
4. 拉取模型：`ollama pull qwen2.5-vl:8b`

---

### 方法三：启用 GPU 加速（NVIDIA）

如果有 NVIDIA GPU，可以大幅提升推理速度：

#### 1. 安装 NVIDIA Container Toolkit

```bash
# Ubuntu/Debian
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
  sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker
```

#### 2. 修改 docker-compose.yml

编辑 `docker-compose.yml`，在 ollama 服务中取消注释 GPU 配置：

```yaml
  ollama:
    image: ollama/ollama:latest
    container_name: video-ai-ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    networks:
      - video-ai-network
    restart: unless-stopped
    # 取消注释以下内容启用 GPU
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

#### 3. 重启服务

```bash
docker-compose down
docker-compose up -d

# 验证 GPU 可用
docker exec -it video-ai-ollama nvidia-smi
```

---

## 🎨 支持的模型列表

### 推荐模型

| 模型 | 大小 | 内存需求 | 特点 | 适用场景 |
|------|------|----------|------|----------|
| **qwen2.5-vl:8b** | 5GB | 12GB | 多模态（视觉+语言） | **视频分析** ⭐ |
| qwen2.5:7b | 4.7GB | 10GB | 中文优化 | 中文内容分析 |
| llama3.2:3b | 2GB | 6GB | 轻量快速 | 资源受限环境 |
| llama3.1:8b | 4.7GB | 10GB | 通用能力强 | 通用文本生成 |
| mistral:7b | 4.1GB | 10GB | 欧洲语言优化 | 多语言支持 |
| deepseek-coder:6.7b | 3.8GB | 10GB | 代码生成 | 技术内容分析 |

### 切换模型

```bash
# 拉取其他模型
docker exec -it video-ai-ollama ollama pull llama3.2:3b

# 修改 .env 文件
LLM_MODEL=llama3.2:3b

# 重启 API 服务
docker-compose restart api
```

---

## 🔧 配置选项

### 修改 Ollama 地址

如果 Ollama 运行在其他机器：

```bash
# .env 配置
OLLAMA_BASE_URL=http://192.168.1.100:11434
```

### 调整推理参数

修改代码中的参数：

```python
from src.core.llm_factory import LLMFactory

# 创建 Ollama provider
llm = LLMFactory.create(
    provider="ollama",
    api_key="http://localhost:11434",  # Ollama URL
    model="qwen2.5-vl:8b",
    temperature=0.7,      # 创造性：0-1，越高越随机
    max_tokens=4096,      # 最大生成长度
    timeout=120           # 超时时间（秒）
)

# 生成文本
response = await llm.generate("分析这段视频内容...")
```

---

## 📊 性能对比

### 推理速度（qwen2.5-vl:8b）

| 硬件配置 | Token/秒 | 延迟 |
|----------|----------|------|
| CPU (Intel i7-12700) | 8-12 | 高 |
| GPU (RTX 3060 12GB) | 35-50 | 低 |
| GPU (RTX 4090 24GB) | 80-120 | 极低 |

### 成本对比

| 方案 | 初始成本 | 运行成本 | 每百万 Token |
|------|----------|----------|--------------|
| **Ollama 本地（CPU）** | $0 | 电费 | ~$0.001 |
| **Ollama 本地（GPU）** | GPU 成本 | 电费 | ~$0.003 |
| OpenAI GPT-4 | $0 | API 费用 | $30 |
| Google Gemini Pro | $0 | API 费用 | $1.25 |

---

## 🧪 测试和验证

### 1. 基础功能测试

```bash
# 进入项目目录
cd video-ai

# 运行测试脚本
python3 << 'EOF'
import asyncio
from src.core.llm_factory import LLMFactory

async def test_ollama():
    print("🧪 测试 Ollama 连接...\n")

    # 创建 Ollama provider
    llm = LLMFactory.create(
        provider="ollama",
        api_key="http://localhost:11434",
        model="qwen2.5-vl:8b"
    )

    # 测试文本生成
    print("1️⃣ 测试文本生成:")
    response = await llm.generate("用一句话介绍人工智能")
    print(f"   响应: {response}\n")

    # 测试 JSON 生成
    print("2️⃣ 测试 JSON 生成:")
    json_response = await llm.generate_json(
        "列出3种编程语言及其特点",
        schema={"languages": [{"name": "", "features": []}]}
    )
    print(f"   JSON: {json_response}\n")

    print("✅ 所有测试通过!")

asyncio.run(test_ollama())
EOF
```

### 2. 视频分析测试

```python
from src.core.editor import VideoEditor

# 使用 Ollama 处理视频
editor = VideoEditor(
    user_interests=["technology", "AI"],
    output_length="medium"
)

# 系统会自动使用环境变量中配置的 Ollama
result = editor.process_video(
    video_path="test_video.mp4",
    output_path="output.mp4"
)

print(f"处理完成: {result}")
```

---

## 🐛 故障排除

### 问题1: Ollama 容器启动失败

```bash
# 检查日志
docker-compose logs ollama

# 常见原因：端口占用
sudo netstat -tulpn | grep 11434

# 解决：修改端口映射
# 在 docker-compose.yml 中改为 "11435:11434"
```

### 问题2: 模型下载慢

```bash
# 使用国内镜像（如果可用）
export OLLAMA_MODELS=/path/to/models

# 或手动下载模型文件
# 从 Hugging Face 镜像站下载
```

### 问题3: GPU 不可用

```bash
# 检查 NVIDIA 驱动
nvidia-smi

# 检查 Docker GPU 支持
docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi

# 重装 nvidia-container-toolkit
sudo apt-get install --reinstall nvidia-container-toolkit
sudo systemctl restart docker
```

### 问题4: 内存不足

```bash
# 使用更小的模型
docker exec -it video-ai-ollama ollama pull qwen2.5:3b

# 或增加 swap
sudo fallocate -l 16G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### 问题5: API 无法连接 Ollama

```bash
# 检查网络连通性
docker exec -it video-ai-api curl http://ollama:11434/api/tags

# 检查环境变量
docker exec -it video-ai-api env | grep OLLAMA

# 重启服务
docker-compose restart api ollama
```

---

## 📚 更多资源

- **Ollama 官方文档**: https://github.com/ollama/ollama
- **模型库**: https://ollama.com/library
- **Qwen 模型文档**: https://github.com/QwenLM/Qwen2.5
- **性能优化**: https://github.com/ollama/ollama/blob/main/docs/gpu.md

---

## 🔄 从云端 API 迁移到 Ollama

如果你之前使用的是 OpenAI/Gemini/Claude：

### 1. 备份原配置

```bash
cp .env .env.backup
```

### 2. 修改配置

```bash
# 原配置
# LLM_PROVIDER=openai
# OPENAI_API_KEY=sk-xxx

# 新配置
LLM_PROVIDER=ollama
LLM_MODEL=qwen2.5-vl:8b
OLLAMA_BASE_URL=http://ollama:11434
```

### 3. 重启服务

```bash
docker-compose restart api
```

### 4. 验证切换

```bash
# 检查日志，应该看到 "初始化 Ollama 提供商"
docker-compose logs api | grep Ollama
```

---

## ⚡ 性能优化建议

### CPU 优化

```bash
# 增加 Ollama 线程数
docker exec -it video-ai-ollama sh -c 'export OLLAMA_NUM_PARALLEL=4'
```

### GPU 优化

```bash
# 配置 GPU 层数（全部放 GPU）
docker exec -it video-ai-ollama sh -c 'export OLLAMA_NUM_GPU=999'
```

### 内存优化

```bash
# 启用量化（牺牲精度换速度）
# 使用 Q4_K_M 量化版本
docker exec -it video-ai-ollama ollama pull qwen2.5-vl:8b-q4_K_M
```

---

**恭喜！** 🎉 你已经完成 Ollama 本地 LLM 的部署，现在可以零成本、高隐私地运行 Video-AI 系统了！
