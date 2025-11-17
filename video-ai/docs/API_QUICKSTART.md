# Video-AI API 快速开始指南

## 5 分钟快速开始

这个指南将帮助你在 5 分钟内运行 Video-AI API。

### 前提条件

- Python 3.10+
- FFmpeg
- OpenAI API Key（可选，用于 AI 功能）

### 步骤 1: 安装

```bash
# 克隆项目
git clone https://github.com/your-org/video-ai.git
cd video-ai

# 安装依赖
pip install -r requirements.txt

# 安装 API 额外依赖
pip install fastapi[all] uvicorn[standard] python-jose[cryptography] \
    passlib[bcrypt] python-multipart slowapi pydantic-settings
```

### 步骤 2: 配置

```bash
# 创建 .env 文件
cat > .env << EOF
DEBUG=True
SECRET_KEY=dev-secret-key-change-me
OPENAI_API_KEY=your-openai-api-key-here
EOF
```

### 步骤 3: 启动服务器

```bash
# 启动开发服务器
python -m uvicorn api.main:app --reload
```

### 步骤 4: 测试 API

打开浏览器访问:

- **Swagger UI**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health

### 步骤 5: 发送第一个请求

```python
import requests

# 登录
response = requests.post(
    "http://localhost:8000/api/v1/auth/login",
    json={"username": "demo", "password": "demo123"}
)
token = response.json()["access_token"]

# 处理视频
response = requests.post(
    "http://localhost:8000/api/v1/videos/process",
    json={
        "video_url": "https://www.youtube.com/watch?v=your-video-id",
        "user_interests": ["tech", "ai"],
        "output_length": "short"
    }
)
print(response.json())
```

恭喜！你已经成功运行了 Video-AI API！

---

## 使用 Docker 快速开始

更简单的方式是使用 Docker：

```bash
# 启动所有服务
docker-compose -f docker-compose.dev.yml up

# API 会在 http://localhost:8000 上运行
```

---

## 下一步

- 查看 [完整 API 文档](API_DOCUMENTATION.md)
- 尝试 [示例代码](../examples/)
- 了解 [部署指南](DEPLOYMENT.md)

---

## 常见问题

### Q: 如何获取 OpenAI API Key?

访问 https://platform.openai.com/api-keys 注册并创建 API Key。

### Q: 支持哪些视频格式?

支持 mp4, avi, mov, mkv, webm 等常见格式。

### Q: 如何提高处理速度?

- 使用 GPU 加速 (设置 WHISPER_DEVICE=cuda)
- 使用较小的 Whisper 模型 (设置 WHISPER_MODEL=tiny)
- 减少 max_segments 参数

### Q: 如何部署到生产环境?

查看 [部署文档](DEPLOYMENT.md) 了解详细信息。

---

## 获取帮助

- **文档**: https://docs.video-ai.com
- **GitHub Issues**: https://github.com/your-org/video-ai/issues
- **Discord**: https://discord.gg/video-ai
