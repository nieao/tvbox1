# Video-AI 本地部署快速指南

## 🚀 5分钟快速部署

### 前置要求

- Docker 20.10+
- Docker Compose 1.29+
- 至少 8GB RAM
- 10GB 可用磁盘空间

### 一键部署

```bash
# 1. 克隆并进入项目
git clone <你的仓库URL>
cd tvbox1
git checkout claude/personalized-video-editor-01FFtSQe2Kq6oj1Wfr9dBo9k
cd video-ai

# 2. 配置环境变量
cp .env.example .env

# 编辑 .env，至少填写以下内容：
# OPENAI_API_KEY=sk-xxx  # 你的 OpenAI API Key
# DB_PASSWORD=your_strong_password
# MONGO_PASSWORD=your_strong_password
# REDIS_PASSWORD=your_strong_password
# SECRET_KEY=$(openssl rand -hex 32)

# 3. 启动所有服务
docker-compose up -d

# 4. 等待服务就绪（约30秒）
docker-compose logs -f api

# 5. 访问服务
# API: http://localhost:8000
# 文档: http://localhost:8000/docs
```

### ✅ 验证部署

```bash
# 健康检查
curl http://localhost:8000/health

# 预期响应
# {"status":"healthy","timestamp":"2025-11-17T..."}
```

## 📱 使用示例

### 1. 通过 API 处理视频

```bash
# 获取认证 Token
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"demo","password":"demo123"}'

# 处理 YouTube 视频
curl -X POST http://localhost:8000/api/v1/videos/process \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "user_interests": ["technology", "AI"],
    "output_length": "medium"
  }'

# 查看处理进度
curl http://localhost:8000/api/v1/videos/jobs/YOUR_JOB_ID \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 2. 通过 Python SDK

```python
from examples.api_client_demo import VideoAIClient

# 初始化客户端
client = VideoAIClient(
    base_url="http://localhost:8000",
    username="demo",
    password="demo123"
)

# 登录
client.login()

# 处理视频
job = client.process_video(
    video_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    user_interests=["technology", "AI"],
    output_length="medium"
)

# 轮询结果
result = client.wait_for_job(job["job_id"])
print(f"处理完成！视频路径: {result['output_path']}")
```

### 3. 通过浏览器插件

1. 构建插件：
   ```bash
   cd browser-extension
   ./build.sh
   ```

2. 安装插件（Chrome）：
   - 访问 `chrome://extensions/`
   - 开启"开发者模式"
   - 点击"加载已解压的扩展程序"
   - 选择 `dist/chrome` 目录

3. 使用插件：
   - 访问 YouTube 视频页面
   - 点击工具栏中的 Video-AI 图标
   - 点击"处理当前视频"
   - 等待处理完成并下载

## 🛠️ 常见问题

### Q1: Docker 启动失败
```bash
# 检查端口占用
netstat -tulpn | grep -E '8000|5432|27017|6379'

# 清理旧容器
docker-compose down -v
docker-compose up -d
```

### Q2: API 返回 500 错误
```bash
# 查看日志
docker-compose logs api

# 检查环境变量
docker-compose exec api env | grep API_KEY
```

### Q3: 视频处理很慢
```bash
# 检查 GPU 可用性
docker-compose exec api python -c "import torch; print(torch.cuda.is_available())"

# 如果没有 GPU，在 .env 中设置
# FORCE_CPU=true
```

### Q4: 无法连接数据库
```bash
# 重启数据库服务
docker-compose restart postgres mongo redis

# 检查连接
docker-compose exec postgres psql -U postgres -d video_ai
docker-compose exec mongo mongo -u admin -p $MONGO_PASSWORD
```

## 📊 服务端口说明

| 服务 | 端口 | 说明 |
|------|------|------|
| API | 8000 | FastAPI 主服务 |
| PostgreSQL | 5432 | 关系型数据库 |
| MongoDB | 27017 | 文档数据库 |
| Redis | 6379 | 缓存服务 |
| MinIO | 9000 | 对象存储 |
| Prometheus | 9090 | 监控指标 |
| Grafana | 3000 | 可视化监控 |

## 🔧 进阶配置

### 启用 GPU 加速

编辑 `docker-compose.yml`，添加 GPU 支持：

```yaml
services:
  api:
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

### 配置外部存储（AWS S3）

编辑 `.env`：

```bash
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_S3_BUCKET=your-bucket-name
AWS_REGION=us-east-1
```

### 配置 HTTPS（使用 Nginx）

```bash
# 生成证书（Let's Encrypt）
certbot certonly --standalone -d your-domain.com

# 修改 nginx.conf，启用 SSL
# 重启 Nginx
docker-compose restart nginx
```

## 📚 更多文档

- **用户手册**: `docs/USER_MANUAL.md`
- **开发者指南**: `docs/DEVELOPER_GUIDE.md`
- **API 文档**: `docs/API_REFERENCE.md`
- **部署指南**: `docs/DEPLOYMENT_GUIDE.md`

## 🆘 获取帮助

如遇到问题：
1. 查看日志: `docker-compose logs -f`
2. 阅读文档: `docs/`
3. 运行测试: `pytest tests/ -v`
4. 提交 Issue（如果是开源项目）

---

**祝你使用愉快！** 🎉
