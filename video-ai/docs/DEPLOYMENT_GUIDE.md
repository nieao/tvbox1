# Video-AI 部署指南

本指南涵盖 Video-AI 在各种环境下的部署方案。

---

## 目录

1. [本地部署](#本地部署)
2. [Docker 部署](#docker-部署)
3. [Kubernetes 部署](#kubernetes-部署)
4. [云平台部署](#云平台部署)
5. [性能调优](#性能调优)
6. [监控和日志](#监控和日志)
7. [安全配置](#安全配置)

---

## 本地部署

### 开发环境部署

```bash
# 1. 克隆项目
git clone <repository-url>
cd video-ai

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，添加API密钥

# 5. 启动服务
streamlit run examples/web_ui.py
```

### 生产环境部署

**使用 Gunicorn + Nginx**

1. **安装依赖**:
```bash
pip install gunicorn
sudo apt-get install nginx
```

2. **创建 Gunicorn 配置** (`gunicorn_config.py`):
```python
bind = "127.0.0.1:8000"
workers = 4
worker_class = "sync"
timeout = 120
keepalive = 5
```

3. **配置 Nginx** (`/etc/nginx/sites-available/video-ai`):
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api {
        proxy_pass http://127.0.0.1:8000;
    }
}
```

4. **启动服务**:
```bash
# Streamlit (Web UI)
streamlit run examples/web_ui.py --server.port 8501

# API服务 (如果有)
gunicorn -c gunicorn_config.py app:app
```

---

## Docker 部署

### Dockerfile

创建 `Dockerfile`:

```dockerfile
FROM python:3.10-slim

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 下载NLP模型
RUN python -m spacy download zh_core_web_sm && \
    python -m spacy download en_core_web_sm && \
    python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"

# 复制项目文件
COPY . .

# 创建数据目录
RUN mkdir -p data/input data/output data/temp

# 暴露端口
EXPOSE 8501

# 启动命令
CMD ["streamlit", "run", "examples/web_ui.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Docker Compose

创建 `docker-compose.yml`:

```yaml
version: '3.8'

services:
  video-ai:
    build: .
    ports:
      - "8501:8501"
    volumes:
      - ./data:/app/data
      - ./config.yaml:/app/config.yaml
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
    restart: unless-stopped

  # 可选：Redis缓存
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

volumes:
  redis_data:
```

### 构建和运行

```bash
# 构建镜像
docker build -t video-ai:latest .

# 运行容器
docker run -d \
  -p 8501:8501 \
  -v $(pwd)/data:/app/data \
  -e OPENAI_API_KEY=your-key \
  video-ai:latest

# 或使用 docker-compose
docker-compose up -d

# 查看日志
docker-compose logs -f video-ai

# 停止服务
docker-compose down
```

---

## Kubernetes 部署

### Deployment

创建 `k8s/deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: video-ai
  labels:
    app: video-ai
spec:
  replicas: 3
  selector:
    matchLabels:
      app: video-ai
  template:
    metadata:
      labels:
        app: video-ai
    spec:
      containers:
      - name: video-ai
        image: your-registry/video-ai:latest
        ports:
        - containerPort: 8501
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: video-ai-secrets
              key: openai-api-key
        volumeMounts:
        - name: data
          mountPath: /app/data
        resources:
          requests:
            memory: "4Gi"
            cpu: "2"
          limits:
            memory: "8Gi"
            cpu: "4"
      volumes:
      - name: data
        persistentVolumeClaim:
          claimName: video-ai-pvc
```

### Service

创建 `k8s/service.yaml`:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: video-ai-service
spec:
  type: LoadBalancer
  selector:
    app: video-ai
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8501
```

### Secrets

```bash
# 创建secrets
kubectl create secret generic video-ai-secrets \
  --from-literal=openai-api-key=your-openai-key \
  --from-literal=google-api-key=your-google-key
```

### 部署

```bash
# 应用配置
kubectl apply -f k8s/

# 查看状态
kubectl get pods -l app=video-ai
kubectl get svc video-ai-service

# 查看日志
kubectl logs -f deployment/video-ai

# 扩容
kubectl scale deployment video-ai --replicas=5
```

---

## 云平台部署

### AWS 部署

#### 使用 EC2

1. **启动 EC2 实例**:
   - AMI: Ubuntu 22.04
   - 实例类型: t3.xlarge (或更高，GPU推荐 g4dn.xlarge)
   - 存储: 50GB+

2. **配置安全组**:
   - 允许入站: 80, 443, 8501

3. **部署应用**:
```bash
ssh ubuntu@your-ec2-ip
sudo apt-get update
sudo apt-get install python3 python3-pip ffmpeg

git clone <repository-url>
cd video-ai
pip3 install -r requirements.txt

# 使用 systemd 管理服务
sudo nano /etc/systemd/system/video-ai.service
```

`video-ai.service`:
```ini
[Unit]
Description=Video-AI Service
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/video-ai
ExecStart=/home/ubuntu/video-ai/venv/bin/streamlit run examples/web_ui.py
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable video-ai
sudo systemctl start video-ai
```

#### 使用 ECS/Fargate

1. **创建 ECR 仓库**:
```bash
aws ecr create-repository --repository-name video-ai
```

2. **推送镜像**:
```bash
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_ECR_URI
docker build -t video-ai .
docker tag video-ai:latest YOUR_ECR_URI/video-ai:latest
docker push YOUR_ECR_URI/video-ai:latest
```

3. **创建 ECS 任务定义和服务** (使用 AWS Console 或 CLI)

### Azure 部署

#### 使用 Azure Container Instances

```bash
# 登录Azure
az login

# 创建资源组
az group create --name video-ai-rg --location eastus

# 部署容器
az container create \
  --resource-group video-ai-rg \
  --name video-ai \
  --image your-registry/video-ai:latest \
  --dns-name-label video-ai \
  --ports 8501 \
  --environment-variables \
    OPENAI_API_KEY=your-key
```

### Google Cloud Platform 部署

#### 使用 Cloud Run

```bash
# 设置项目
gcloud config set project YOUR_PROJECT_ID

# 构建镜像
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/video-ai

# 部署服务
gcloud run deploy video-ai \
  --image gcr.io/YOUR_PROJECT_ID/video-ai \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 4Gi \
  --set-env-vars OPENAI_API_KEY=your-key
```

---

## 性能调优

### 1. GPU 加速

**安装 CUDA**:
```bash
# Ubuntu
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.0-1_all.deb
sudo dpkg -i cuda-keyring_1.0-1_all.deb
sudo apt-get update
sudo apt-get install cuda

# 安装PyTorch (CUDA版本)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### 2. 缓存优化

**Redis 缓存**:
```python
import redis

# 配置Redis
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# 缓存转录结果
def transcribe_with_cache(video_path: str):
    cache_key = f"transcribe:{hash(video_path)}"
    cached = redis_client.get(cache_key)

    if cached:
        return json.loads(cached)

    result = transcribe(video_path)
    redis_client.setex(cache_key, 3600, json.dumps(result))
    return result
```

### 3. 并发处理

**使用异步和多进程**:
```python
import asyncio
from concurrent.futures import ProcessPoolExecutor

# 异步处理
async def process_multiple_videos(video_paths):
    tasks = [process_video_async(path) for path in video_paths]
    results = await asyncio.gather(*tasks)
    return results

# 多进程处理
with ProcessPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(process_video, video_paths))
```

### 4. 负载均衡

**Nginx 配置**:
```nginx
upstream video_ai_backend {
    least_conn;
    server 127.0.0.1:8501;
    server 127.0.0.1:8502;
    server 127.0.0.1:8503;
}

server {
    listen 80;
    location / {
        proxy_pass http://video_ai_backend;
    }
}
```

---

## 监控和日志

### 1. 应用监控

**使用 Prometheus + Grafana**:

```python
# 添加metrics
from prometheus_client import Counter, Histogram

video_processed = Counter('video_processed_total', 'Total videos processed')
processing_time = Histogram('processing_duration_seconds', 'Video processing duration')

@processing_time.time()
def process_video(video_path):
    # 处理逻辑
    video_processed.inc()
```

### 2. 日志管理

**配置日志**:
```python
import logging
from logging.handlers import RotatingFileHandler

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler('logs/app.log', maxBytes=10485760, backupCount=5),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
```

**ELK Stack 集成**:
- Elasticsearch: 存储日志
- Logstash: 日志处理
- Kibana: 日志可视化

---

## 安全配置

### 1. API 密钥管理

**使用环境变量或 Secrets Manager**:
```python
import os
from aws_secretsmanager_caching import SecretCache

# 环境变量
api_key = os.getenv('OPENAI_API_KEY')

# AWS Secrets Manager
cache = SecretCache()
api_key = cache.get_secret_string('openai-api-key')
```

### 2. HTTPS 配置

**Let's Encrypt + Nginx**:
```bash
# 安装 certbot
sudo apt-get install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo certbot renew --dry-run
```

### 3. 防火墙配置

```bash
# UFW (Ubuntu)
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 4. 限流和防护

**Nginx 限流**:
```nginx
limit_req_zone $binary_remote_addr zone=video_ai_limit:10m rate=10r/s;

location / {
    limit_req zone=video_ai_limit burst=20;
    proxy_pass http://backend;
}
```

---

## 备份和恢复

### 1. 数据备份

```bash
#!/bin/bash
# backup.sh

# 备份数据目录
tar -czf backup_$(date +%Y%m%d).tar.gz data/

# 上传到S3
aws s3 cp backup_$(date +%Y%m%d).tar.gz s3://your-bucket/backups/

# 清理旧备份 (保留30天)
find . -name "backup_*.tar.gz" -mtime +30 -delete
```

### 2. 自动备份

**Cron job**:
```bash
# 编辑 crontab
crontab -e

# 每天凌晨2点备份
0 2 * * * /path/to/backup.sh
```

---

## 故障排除

### 常见问题

1. **内存不足**:
   - 增加swap空间
   - 限制并发数
   - 使用分片处理

2. **GPU OOM**:
   - 降低batch size
   - 使用FP16精度
   - 清理GPU缓存

3. **API超时**:
   - 增加timeout设置
   - 使用重试机制
   - 启用缓存

---

## 最佳实践

1. ✅ 使用Docker容器化部署
2. ✅ 配置自动扩缩容
3. ✅ 启用监控和告警
4. ✅ 定期备份数据
5. ✅ 使用 HTTPS
6. ✅ 限流和防护
7. ✅ 日志集中管理
8. ✅ CI/CD 自动化

---

## 生产检查清单

- [ ] 配置 HTTPS
- [ ] 设置防火墙
- [ ] 配置备份
- [ ] 启用监控
- [ ] 配置日志
- [ ] 限流设置
- [ ] 安全审计
- [ ] 性能测试
- [ ] 灾难恢复计划
- [ ] 文档更新

---

**需要帮助？** 查看 [用户手册](USER_MANUAL.md) 或提交 [Issue](https://github.com/yourusername/video-ai/issues)
