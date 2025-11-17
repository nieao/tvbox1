# Video-AI RESTful API

基于 FastAPI 构建的生产级 RESTful API，提供智能视频处理和个性化推荐服务。

## 特性

- ✅ **完整的 RESTful API** - 支持所有核心功能
- 🔐 **JWT 认证** - 安全的用户认证和授权
- 🚦 **速率限制** - 防止滥用和过载
- 📊 **自动文档** - Swagger UI 和 ReDoc
- 🧪 **完整测试** - 单元测试和集成测试
- 🐳 **Docker 支持** - 容器化部署
- 📝 **详细日志** - 请求日志和错误追踪
- ⚡ **异步处理** - 后台任务处理
- 🎯 **类型安全** - Pydantic 数据验证

## 项目结构

```
api/
├── __init__.py           # API 模块初始化
├── main.py               # FastAPI 应用主文件
├── models.py             # Pydantic 数据模型
├── services.py           # 业务逻辑服务
├── auth.py               # 认证和授权
├── middleware.py         # 中间件
├── config.py             # 配置管理
├── utils.py              # 工具函数
└── README.md            # 本文件
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements-api.txt
```

### 2. 配置环境

```bash
cp .env.example .env
# 编辑 .env 文件，设置必要的配置
```

### 3. 启动服务器

```bash
# 开发模式
python -m uvicorn api.main:app --reload

# 生产模式
python -m uvicorn api.main:app --workers 4
```

### 4. 访问文档

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API 端点

### 认证

- `POST /api/v1/auth/login` - 用户登录
- `GET /api/v1/auth/me` - 获取当前用户信息

### 视频处理

- `POST /api/v1/videos/process` - 处理视频（YouTube URL）
- `POST /api/v1/videos/upload` - 上传视频文件
- `POST /api/v1/videos/process-uploaded` - 处理已上传的视频
- `GET /api/v1/jobs/{job_id}` - 查询任务状态
- `GET /api/v1/jobs` - 列出所有任务
- `GET /api/v1/videos/{video_id}/download` - 下载处理后的视频

### 用户管理

- `POST /api/v1/users` - 创建用户
- `GET /api/v1/users/{user_id}` - 获取用户信息
- `PUT /api/v1/users/{user_id}` - 更新用户信息

### 推荐系统

- `GET /api/v1/recommendations/{user_id}` - 获取个性化推荐
- `POST /api/v1/feedback` - 提交用户反馈

### 统计分析

- `GET /api/v1/stats/trending` - 获取热门内容
- `GET /api/v1/stats/analytics` - 获取系统分析数据（需要认证）

### 管理功能

- `POST /api/v1/admin/cleanup` - 清理旧文件（需要认证）

## 使用示例

### Python

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
        "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "user_interests": ["tech", "ai"],
        "output_length": "short"
    }
)
job_id = response.json()["job_id"]

# 查询状态
response = requests.get(f"http://localhost:8000/api/v1/jobs/{job_id}")
print(response.json())
```

### cURL

```bash
# 登录
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "demo", "password": "demo123"}'

# 处理视频
curl -X POST "http://localhost:8000/api/v1/videos/process" \
  -H "Content-Type: application/json" \
  -d '{
    "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "user_interests": ["tech", "ai"],
    "output_length": "short"
  }'
```

## 测试

```bash
# 运行所有测试
pytest tests/test_api.py -v

# 运行特定测试
pytest tests/test_api.py::test_login_success -v
```

## 部署

### Docker

```bash
# 构建镜像
docker build -t video-ai-api .

# 运行容器
docker run -d -p 8000:8000 video-ai-api
```

### Docker Compose

```bash
# 开发环境
docker-compose -f docker-compose.dev.yml up

# 生产环境
docker-compose up -d
```

## 配置

主要配置项（在 `config.py` 或 `.env` 中）:

- `DEBUG` - 调试模式
- `SECRET_KEY` - JWT 密钥
- `OPENAI_API_KEY` - OpenAI API 密钥
- `RATE_LIMIT_PER_MINUTE` - 每分钟请求限制
- `MAX_UPLOAD_SIZE` - 最大上传文件大小
- `MAX_CONCURRENT_JOBS` - 最大并发任务数

## 性能优化

1. **使用多 Worker**: `--workers 4`
2. **启用 Redis 缓存**: 设置 `REDIS_URL`
3. **配置任务队列**: 使用 Celery 处理长任务
4. **使用负载均衡**: Nginx 或 Traefik
5. **启用 CDN**: 缓存静态资源

## 安全建议

1. 使用强密钥 (`SECRET_KEY`)
2. 启用 HTTPS
3. 配置 CORS
4. 限制上传文件大小
5. 实施速率限制
6. 定期更新依赖
7. 使用环境变量管理敏感信息

## 监控

- 健康检查: `/health`
- Prometheus 指标: `/metrics` (可选)
- 日志: 使用 `LOG_LEVEL` 配置

## 故障排查

### 问题: 端口已被占用

```bash
# 查找占用端口的进程
lsof -i :8000

# 杀死进程
kill -9 <PID>
```

### 问题: 导入错误

确保项目根目录在 Python 路径中:

```bash
export PYTHONPATH=/path/to/video-ai:$PYTHONPATH
```

### 问题: 视频处理失败

检查:
- FFmpeg 是否安装
- OpenAI API Key 是否有效
- 磁盘空间是否充足

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License

## 联系方式

- GitHub: https://github.com/your-org/video-ai
- Email: support@video-ai.com
- Discord: https://discord.gg/video-ai
