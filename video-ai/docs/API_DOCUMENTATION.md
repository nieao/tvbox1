# Video-AI RESTful API 文档

## 目录

- [简介](#简介)
- [快速开始](#快速开始)
- [认证](#认证)
- [API 端点](#api-端点)
  - [视频处理](#视频处理)
  - [用户管理](#用户管理)
  - [推荐系统](#推荐系统)
  - [统计分析](#统计分析)
- [示例代码](#示例代码)
- [错误处理](#错误处理)
- [部署](#部署)

---

## 简介

Video-AI API 是一个基于 FastAPI 构建的生产级 RESTful API，提供智能视频处理、个性化推荐和用户管理功能。

### 主要功能

- 🎬 **视频处理**: 支持 YouTube 视频和本地视频的智能剪辑
- 👤 **用户管理**: 完整的用户画像和偏好管理
- 🎯 **智能推荐**: 基于混合算法的个性化推荐系统
- 📊 **统计分析**: 系统性能和用户行为分析
- 🔐 **安全认证**: JWT 令牌认证和速率限制
- 📝 **完整文档**: 自动生成的 Swagger UI 和 ReDoc

### 技术栈

- **框架**: FastAPI 0.104+
- **认证**: JWT (PyJWT)
- **速率限制**: SlowAPI
- **视频处理**: MoviePy, FFmpeg
- **AI**: OpenAI, Whisper
- **部署**: Docker, Docker Compose

---

## 快速开始

### 1. 安装依赖

```bash
# 克隆项目
git clone https://github.com/your-org/video-ai.git
cd video-ai

# 安装依赖
pip install -r requirements.txt

# 安装 API 依赖
pip install fastapi[all] uvicorn[standard] python-jose[cryptography] \
    passlib[bcrypt] python-multipart slowapi pydantic-settings
```

### 2. 配置环境变量

```bash
# 复制环境变量示例
cp .env.example .env

# 编辑 .env 文件，设置必要的配置
# 至少需要设置:
# - SECRET_KEY
# - OPENAI_API_KEY
```

### 3. 启动服务器

```bash
# 开发模式（带热重载）
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# 生产模式
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 4. 访问 API 文档

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

---

## 认证

API 使用 JWT (JSON Web Tokens) 进行认证。

### 获取访问令牌

```bash
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "demo",
  "password": "demo123"
}
```

**响应:**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user_id": "demo"
}
```

### 使用令牌

在需要认证的请求中，添加 `Authorization` 头:

```bash
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 默认账户

- 用户名: `demo` / 密码: `demo123`
- 用户名: `admin` / 密码: `admin123`

---

## API 端点

### 基础端点

#### 根端点

```bash
GET /
```

**响应:**

```json
{
  "service": "Video-AI API",
  "version": "1.0.0",
  "status": "running",
  "docs": "/docs",
  "redoc": "/redoc"
}
```

#### 健康检查

```bash
GET /health
```

**响应:**

```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00",
  "version": "1.0.0",
  "services": {
    "video_processing": true,
    "recommendation": true,
    "user_management": true
  }
}
```

---

### 视频处理

#### 处理 YouTube 视频

处理 YouTube 视频并生成个性化剪辑。

```bash
POST /api/v1/videos/process
Content-Type: application/json

{
  "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
  "user_interests": ["tech", "ai", "programming"],
  "output_length": "medium",
  "transition_style": "text",
  "transition_template": "modern",
  "quality": "720p",
  "use_transcript": true,
  "max_segments": 10
}
```

**参数说明:**

- `video_url` (必需): YouTube 视频 URL
- `user_interests` (可选): 用户兴趣列表
- `output_length` (可选): 输出长度 (`short`, `medium`, `long`)
- `transition_style` (可选): 过渡效果 (`text`, `fade`, `blur`, `zoom`, `gradient`, `none`)
- `transition_template` (可选): 文字模板 (`minimal`, `modern`, `classic`, `colorful`, `info_card`)
- `quality` (可选): 视频质量 (`480p`, `720p`, `1080p`, `best`)
- `use_transcript` (可选): 是否使用 YouTube 字幕
- `max_segments` (可选): 最大片段数 (1-50)

**响应:**

```json
{
  "job_id": "job_20240101120000_abc12345",
  "status": "pending",
  "message": "视频处理已开始",
  "estimated_time": 300
}
```

#### 上传视频文件

上传本地视频文件以供处理。

```bash
POST /api/v1/videos/upload
Content-Type: multipart/form-data

file: <video_file>
```

**支持的格式:** mp4, avi, mov, mkv, webm
**最大文件大小:** 500MB

**响应:**

```json
{
  "filename": "my_video.mp4",
  "filepath": "/tmp/video-ai/uploads/video_20240101120000_xyz.mp4",
  "size": 10485760,
  "content_type": "video/mp4",
  "uploaded_at": "2024-01-01T12:00:00"
}
```

#### 处理已上传的视频

处理之前上传的视频文件。

```bash
POST /api/v1/videos/process-uploaded
Content-Type: application/json

{
  "filepath": "/tmp/video-ai/uploads/video_20240101120000_xyz.mp4",
  "user_interests": ["tech", "ai"],
  "output_length": "short"
}
```

#### 查询任务状态

```bash
GET /api/v1/jobs/{job_id}
```

**响应:**

```json
{
  "job_id": "job_20240101120000_abc12345",
  "status": "completed",
  "progress": 1.0,
  "message": "处理完成",
  "result": {
    "video_id": "video_20240101120000_abc12345",
    "output_path": "/tmp/video-ai/outputs/edited_video_20240101120000_abc12345.mp4",
    "original_duration": 600.0,
    "edited_duration": 180.0,
    "compression_ratio": 0.7,
    "density_improvement": 2.33,
    "segments_count": 8,
    "used_strategy": "hybrid",
    "download_url": "/api/v1/videos/video_20240101120000_abc12345/download"
  },
  "error": null,
  "created_at": "2024-01-01T12:00:00",
  "updated_at": "2024-01-01T12:05:00"
}
```

**状态值:**

- `pending`: 等待处理
- `processing`: 处理中
- `completed`: 已完成
- `failed`: 失败

#### 下载处理后的视频

```bash
GET /api/v1/videos/{video_id}/download
```

**响应:** 视频文件 (video/mp4)

#### 列出所有任务

```bash
GET /api/v1/jobs?status=completed
Authorization: Bearer <token>
```

**参数:**

- `status` (可选): 按状态过滤 (`pending`, `processing`, `completed`, `failed`)

---

### 用户管理

#### 创建用户

创建新的用户画像。

```bash
POST /api/v1/users
Content-Type: application/json

{
  "user_id": "user123",
  "interests": ["tech", "ai", "music"],
  "skip_topics": ["ads", "promotion"],
  "preferred_duration": "medium",
  "language": "zh-CN",
  "age_range": "25-34",
  "location": "China"
}
```

**响应:**

```json
{
  "user_id": "user123",
  "interests": {
    "tech": {
      "weight": 0.5,
      "confidence": 0.5,
      "last_updated": "2024-01-01T12:00:00"
    },
    "ai": {
      "weight": 0.5,
      "confidence": 0.5,
      "last_updated": "2024-01-01T12:00:00"
    }
  },
  "category_interests": {},
  "preferences": {
    "preferred_duration": "medium",
    "skip_topics": ["ads", "promotion"]
  },
  "engagement_score": 0.0,
  "loyalty_score": 0.0,
  "activity_level": "inactive",
  "last_active": null
}
```

#### 获取用户信息

```bash
GET /api/v1/users/{user_id}
```

#### 更新用户信息

```bash
PUT /api/v1/users/{user_id}
Content-Type: application/json

{
  "user_id": "user123",
  "interests": ["tech", "ai", "music", "gaming"],
  "preferred_duration": "long"
}
```

---

### 推荐系统

#### 获取个性化推荐

```bash
GET /api/v1/recommendations/{user_id}?num=10&seed_video_id=video_123
```

**参数:**

- `num` (可选): 推荐数量 (1-50, 默认 10)
- `seed_video_id` (可选): 种子视频ID（用于内容推荐）

**响应:**

```json
{
  "user_id": "user123",
  "recommendations": [
    {
      "video_id": "video_1",
      "score": 0.85,
      "reason": "基于相似用户的推荐，内容相似，热门内容",
      "cf_score": 0.8,
      "cb_score": 0.75,
      "popularity_score": 0.9,
      "thumbnail_url": null,
      "title": null,
      "duration": null
    }
  ],
  "total": 10,
  "generated_at": "2024-01-01T12:00:00"
}
```

#### 提交用户反馈

记录用户对视频的行为。

```bash
POST /api/v1/feedback
Content-Type: application/json

{
  "user_id": "user123",
  "video_id": "video_456",
  "action": "like",
  "rating": 0.9,
  "watch_time": 300,
  "watch_percentage": 0.8,
  "comment": "很棒的视频！"
}
```

**动作类型:**

- `like`: 点赞
- `dislike`: 不喜欢
- `skip`: 跳过
- `save`: 保存
- `share`: 分享

---

### 统计分析

#### 获取热门内容

```bash
GET /api/v1/stats/trending?period=today
```

**参数:**

- `period`: 时间段 (`today`, `week`, `month`)

**响应:**

```json
{
  "videos": [
    {
      "video_id": "video_1",
      "title": "热门视频 1",
      "views": 10000,
      "likes": 500
    }
  ],
  "period": "today",
  "generated_at": "2024-01-01T12:00:00"
}
```

#### 获取系统分析数据

需要认证。

```bash
GET /api/v1/stats/analytics
Authorization: Bearer <token>
```

**响应:**

```json
{
  "total_users": 100,
  "total_videos": 500,
  "total_jobs": 1000,
  "active_jobs": 5,
  "avg_processing_time": 250.5,
  "avg_compression_ratio": 0.65,
  "popular_interests": [],
  "system_health": "healthy"
}
```

---

## 示例代码

### Python 客户端

```python
import requests

# API 配置
BASE_URL = "http://localhost:8000"
API_V1 = f"{BASE_URL}/api/v1"

# 1. 登录获取令牌
response = requests.post(
    f"{API_V1}/auth/login",
    json={"username": "demo", "password": "demo123"}
)
token = response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# 2. 创建用户
requests.post(
    f"{API_V1}/users",
    json={
        "user_id": "test_user",
        "interests": ["tech", "ai"],
        "preferred_duration": "medium"
    }
)

# 3. 处理 YouTube 视频
response = requests.post(
    f"{API_V1}/videos/process",
    json={
        "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "user_interests": ["tech", "ai"],
        "output_length": "short"
    }
)
job_id = response.json()["job_id"]

# 4. 查询任务状态
import time
while True:
    response = requests.get(f"{API_V1}/jobs/{job_id}")
    status = response.json()["status"]

    if status == "completed":
        result = response.json()["result"]
        download_url = result["download_url"]
        print(f"视频处理完成！下载链接: {BASE_URL}{download_url}")
        break
    elif status == "failed":
        print("处理失败")
        break

    time.sleep(5)

# 5. 下载视频
response = requests.get(f"{BASE_URL}{download_url}")
with open("edited_video.mp4", "wb") as f:
    f.write(response.content)

# 6. 提交反馈
requests.post(
    f"{API_V1}/feedback",
    json={
        "user_id": "test_user",
        "video_id": result["video_id"],
        "action": "like",
        "rating": 0.9
    }
)

# 7. 获取推荐
response = requests.get(f"{API_V1}/recommendations/test_user?num=5")
recommendations = response.json()["recommendations"]
for rec in recommendations:
    print(f"推荐: {rec['video_id']} (分数: {rec['score']:.2f})")
```

### JavaScript/TypeScript 客户端

```javascript
// API 配置
const BASE_URL = 'http://localhost:8000';
const API_V1 = `${BASE_URL}/api/v1`;

// 1. 登录
async function login(username, password) {
  const response = await fetch(`${API_V1}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password })
  });
  const data = await response.json();
  return data.access_token;
}

// 2. 处理视频
async function processVideo(token, videoUrl, interests) {
  const response = await fetch(`${API_V1}/videos/process`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
      video_url: videoUrl,
      user_interests: interests,
      output_length: 'short'
    })
  });
  const data = await response.json();
  return data.job_id;
}

// 3. 查询任务状态
async function checkJobStatus(jobId) {
  const response = await fetch(`${API_V1}/jobs/${jobId}`);
  return await response.json();
}

// 4. 获取推荐
async function getRecommendations(userId, num = 10) {
  const response = await fetch(
    `${API_V1}/recommendations/${userId}?num=${num}`
  );
  return await response.json();
}

// 使用示例
(async () => {
  // 登录
  const token = await login('demo', 'demo123');

  // 处理视频
  const jobId = await processVideo(
    token,
    'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
    ['tech', 'ai']
  );

  // 轮询状态
  while (true) {
    const job = await checkJobStatus(jobId);

    if (job.status === 'completed') {
      console.log('处理完成！', job.result);
      break;
    } else if (job.status === 'failed') {
      console.error('处理失败', job.error);
      break;
    }

    await new Promise(resolve => setTimeout(resolve, 5000));
  }
})();
```

### cURL 示例

```bash
# 1. 登录
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "demo", "password": "demo123"}'

# 2. 处理视频
curl -X POST "http://localhost:8000/api/v1/videos/process" \
  -H "Content-Type: application/json" \
  -d '{
    "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "user_interests": ["tech", "ai"],
    "output_length": "short"
  }'

# 3. 查询任务状态
curl "http://localhost:8000/api/v1/jobs/job_20240101120000_abc12345"

# 4. 下载视频
curl -O "http://localhost:8000/api/v1/videos/video_20240101120000_abc12345/download"

# 5. 获取推荐
curl "http://localhost:8000/api/v1/recommendations/user123?num=5"
```

---

## 错误处理

### HTTP 状态码

- `200`: 成功
- `201`: 创建成功
- `400`: 请求错误
- `401`: 未授权
- `403`: 禁止访问
- `404`: 资源不存在
- `422`: 验证错误
- `429`: 请求过于频繁
- `500`: 服务器内部错误

### 错误响应格式

```json
{
  "error": "ValidationError",
  "message": "请求参数验证失败",
  "details": {
    "field": "video_url",
    "issue": "必须是有效的 YouTube URL"
  },
  "timestamp": "2024-01-01T12:00:00"
}
```

---

## 部署

### 使用 Docker

```bash
# 构建镜像
docker build -t video-ai-api .

# 运行容器
docker run -d \
  -p 8000:8000 \
  -e OPENAI_API_KEY=your-key \
  -e SECRET_KEY=your-secret \
  --name video-ai-api \
  video-ai-api
```

### 使用 Docker Compose

```bash
# 开发环境
docker-compose -f docker-compose.dev.yml up

# 生产环境
docker-compose up -d
```

### 生产部署建议

1. **使用 HTTPS**: 配置 SSL/TLS 证书
2. **设置环境变量**: 使用安全的密钥和密码
3. **配置反向代理**: 使用 Nginx 或 Traefik
4. **启用日志**: 配置日志聚合和监控
5. **设置备份**: 定期备份用户数据和视频
6. **限制资源**: 设置 CPU 和内存限制
7. **使用负载均衡**: 多实例部署
8. **监控健康**: 配置健康检查和告警

---

## 更多信息

- **GitHub**: https://github.com/your-org/video-ai
- **问题反馈**: https://github.com/your-org/video-ai/issues
- **文档**: https://docs.video-ai.com
- **示例**: https://github.com/your-org/video-ai/tree/main/examples

---

## 许可证

MIT License

Copyright (c) 2024 Video-AI Team
