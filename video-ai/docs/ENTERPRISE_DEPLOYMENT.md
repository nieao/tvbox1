# Video-AI 企业级部署方案

## 1. 部署架构概览

### 1.1 整体架构

```
                     ┌──────────────────────────────────────┐
                     │      客户端层 (Client Layer)          │
                     │  Web | Mobile App | API Client        │
                     └──────────────┬───────────────────────┘
                                    │
                     ┌──────────────▼───────────────────────┐
                     │  CDN & 负载均衡 (Load Balancer)       │
                     │  Nginx / AWS ELB / Cloudflare        │
                     └──────────────┬───────────────────────┘
                                    │
        ┌───────────────────────────┼───────────────────────────────┐
        │                           │                               │
   ┌────▼──────┐            ┌──────▼──────┐            ┌───────────▼─────┐
   │  API容器  │            │ 任务队列    │            │  静态资源服务   │
   │ (3-10个)  │            │ (Redis)     │            │  (S3/OSS)       │
   └────┬──────┘            └──────┬──────┘            └──────────────────┘
        │                          │
        │         ┌────────────────┴────────────────┐
        │         │                                 │
   ┌────▼──────────┴──────┐        ┌──────────────▼─────────┐
   │  数据库层 (Database) │        │  缓存层 (Cache)         │
   │ ├─ MongoDB          │        │ ├─ Redis               │
   │ └─ PostgreSQL       │        │ └─ Memcached           │
   └─────────────────────┘        └────────────────────────┘
```

---

## 2. Docker 容器化部署

### 2.1 Dockerfile

```dockerfile
# Multi-stage build for optimized image size
FROM python:3.10-slim as builder

WORKDIR /build

# 安装构建工具
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 构建依赖
RUN pip install --user --no-cache-dir -r requirements.txt


# Final stage
FROM python:3.10-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 从builder阶段复制Python依赖
COPY --from=builder /root/.local /root/.local

# 复制应用代码
COPY . .

# 设置环境变量
ENV PATH=/root/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# 创建非root用户
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["python", "-m", "uvicorn", "src.api.main:app", \
     "--host", "0.0.0.0", \
     "--port", "8000", \
     "--workers", "4"]
```

### 2.2 docker-compose.yml

```yaml
version: '3.8'

services:
  # FastAPI应用
  api:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: video-ai-api
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - DATABASE_URL=postgresql://postgres:${DB_PASSWORD}@postgres:5432/video_ai
      - MONGODB_URI=mongodb://mongo:27017/video_ai
      - REDIS_URL=redis://redis:6379/0
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
      - AWS_S3_BUCKET=${AWS_S3_BUCKET}
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - /tmp:/app/temp
    depends_on:
      - postgres
      - mongo
      - redis
    networks:
      - video-ai-network
    restart: unless-stopped
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  # PostgreSQL数据库
  postgres:
    image: postgres:15-alpine
    container_name: video-ai-postgres
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=${DB_PASSWORD}
      - POSTGRES_DB=video_ai
      - PGDATA=/var/lib/postgresql/data/pgdata
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./scripts/init-db.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"
    networks:
      - video-ai-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

  # MongoDB数据库
  mongo:
    image: mongo:6
    container_name: video-ai-mongo
    environment:
      - MONGO_INITDB_ROOT_USERNAME=admin
      - MONGO_INITDB_ROOT_PASSWORD=${MONGO_PASSWORD}
      - MONGO_INITDB_DATABASE=video_ai
    volumes:
      - mongo_data:/data/db
      - mongo_config:/data/configdb
      - ./scripts/init-mongo.js:/docker-entrypoint-initdb.d/init-mongo.js
    ports:
      - "27017:27017"
    networks:
      - video-ai-network
    healthcheck:
      test: echo 'db.runCommand("ping").ok' | mongosh localhost:27017/test
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

  # Redis缓存和任务队列
  redis:
    image: redis:7-alpine
    container_name: video-ai-redis
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    networks:
      - video-ai-network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

  # Celery Worker - 视频处理
  celery-worker-video:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: video-ai-celery-video
    command: celery -A src.tasks.celery_app worker --loglevel=info --queues=video --concurrency=2
    environment:
      - ENVIRONMENT=production
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - DATABASE_URL=postgresql://postgres:${DB_PASSWORD}@postgres:5432/video_ai
      - REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/0
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    depends_on:
      - redis
      - postgres
    networks:
      - video-ai-network
    restart: unless-stopped
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  # Celery Worker - AI处理
  celery-worker-ai:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: video-ai-celery-ai
    command: celery -A src.tasks.celery_app worker --loglevel=info --queues=ai --concurrency=1
    environment:
      - ENVIRONMENT=production
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - DATABASE_URL=postgresql://postgres:${DB_PASSWORD}@postgres:5432/video_ai
      - REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/0
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./models:/app/models
    depends_on:
      - redis
      - postgres
    networks:
      - video-ai-network
    restart: unless-stopped
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  # Celery Beat - 定时任务
  celery-beat:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: video-ai-celery-beat
    command: celery -A src.tasks.celery_app beat --loglevel=info
    environment:
      - ENVIRONMENT=production
      - DATABASE_URL=postgresql://postgres:${DB_PASSWORD}@postgres:5432/video_ai
      - REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/0
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    depends_on:
      - redis
      - postgres
    networks:
      - video-ai-network
    restart: unless-stopped

  # Nginx 反向代理
  nginx:
    image: nginx:alpine
    container_name: video-ai-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
      - nginx_cache:/var/cache/nginx
    depends_on:
      - api
    networks:
      - video-ai-network
    restart: unless-stopped
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  # 可选: Minio (S3兼容存储)
  minio:
    image: minio/minio
    container_name: video-ai-minio
    environment:
      - MINIO_ROOT_USER=minioadmin
      - MINIO_ROOT_PASSWORD=${MINIO_PASSWORD}
    command: minio server /data
    volumes:
      - minio_data:/data
    ports:
      - "9000:9000"
      - "9001:9001"
    networks:
      - video-ai-network
    restart: unless-stopped

volumes:
  postgres_data:
    driver: local
  mongo_data:
    driver: local
  mongo_config:
    driver: local
  redis_data:
    driver: local
  nginx_cache:
    driver: local
  minio_data:
    driver: local

networks:
  video-ai-network:
    driver: bridge
```

### 2.3 环境变量配置 (.env)

```bash
# 应用配置
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=your-secret-key-here

# 数据库配置
DB_PASSWORD=secure_postgres_password
MONGO_PASSWORD=secure_mongo_password
REDIS_PASSWORD=secure_redis_password

# API密钥
OPENAI_API_KEY=sk-xxx
GOOGLE_API_KEY=xxx
ANTHROPIC_API_KEY=xxx

# AWS S3配置
AWS_ACCESS_KEY_ID=xxx
AWS_SECRET_ACCESS_KEY=xxx
AWS_S3_BUCKET=video-ai-bucket
AWS_REGION=us-east-1

# Minio配置（如果使用本地存储）
MINIO_PASSWORD=secure_minio_password

# 日志配置
LOG_LEVEL=INFO
LOG_FORMAT=json

# 性能配置
WORKER_PROCESSES=4
MAX_WORKERS=10
TIMEOUT=300
```

### 2.4 nginx.conf

```nginx
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 2048;
    use epoll;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;

    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    client_max_body_size 5000M;

    # 缓存配置
    proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=api_cache:10m max_size=1g inactive=60m;

    # 上游服务器
    upstream api_backend {
        least_conn;
        server api:8000 weight=5 max_fails=3 fail_timeout=30s;
        server api:8000 weight=5 max_fails=3 fail_timeout=30s;
        server api:8000 weight=5 max_fails=3 fail_timeout=30s;
        keepalive 32;
    }

    # HTTPS重定向
    server {
        listen 80;
        server_name _;
        return 301 https://$host$request_uri;
    }

    # HTTPS服务器
    server {
        listen 443 ssl http2;
        server_name api.video-ai.com;

        # SSL证书
        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;
        ssl_session_cache shared:SSL:10m;
        ssl_session_timeout 10m;

        # 安全头
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header Referrer-Policy "strict-origin-when-cross-origin" always;

        # API路由
        location / {
            proxy_pass http://api_backend;
            proxy_http_version 1.1;
            proxy_set_header Connection "";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            # 缓存GET请求
            proxy_cache api_cache;
            proxy_cache_valid 200 1h;
            proxy_cache_use_stale error timeout updating http_500 http_502 http_503 http_504;
            add_header X-Cache-Status $upstream_cache_status;

            # 超时配置
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }

        # 健康检查端点
        location /health {
            access_log off;
            proxy_pass http://api_backend;
            proxy_http_version 1.1;
            proxy_set_header Connection "";
        }

        # 静态文件
        location /static/ {
            alias /app/static/;
            expires 30d;
            add_header Cache-Control "public, immutable";
        }

        # WebSocket支持
        location /ws/ {
            proxy_pass http://api_backend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_read_timeout 86400;
        }
    }
}
```

---

## 3. Kubernetes 部署

### 3.1 k8s/namespace.yaml

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: video-ai
  labels:
    app: video-ai
```

### 3.2 k8s/deployment.yaml

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: video-ai-api
  namespace: video-ai
  labels:
    app: video-ai
    component: api
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: video-ai
      component: api
  template:
    metadata:
      labels:
        app: video-ai
        component: api
    spec:
      # Pod亲和性配置
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
            - weight: 100
              podAffinityTerm:
                labelSelector:
                  matchExpressions:
                    - key: app
                      operator: In
                      values:
                        - video-ai
                topologyKey: kubernetes.io/hostname

      # 初始化容器 - 数据库迁移
      initContainers:
        - name: db-migrate
          image: video-ai:latest
          command:
            - python
            - -m
            - alembic
            - upgrade
            - head
          env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: api-secrets
                  key: database-url

      # 主容器
      containers:
        - name: api
          image: video-ai:latest
          imagePullPolicy: Always
          ports:
            - name: http
              containerPort: 8000
              protocol: TCP

          # 环境变量
          env:
            - name: ENVIRONMENT
              value: "production"
            - name: OPENAI_API_KEY
              valueFrom:
                secretKeyRef:
                  name: api-secrets
                  key: openai-key
            - name: GOOGLE_API_KEY
              valueFrom:
                secretKeyRef:
                  name: api-secrets
                  key: google-key
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: api-secrets
                  key: database-url
            - name: REDIS_URL
              value: "redis://redis:6379/0"
            - name: LOG_LEVEL
              value: "INFO"

          # 资源限制
          resources:
            requests:
              memory: "2Gi"
              cpu: "1000m"
            limits:
              memory: "4Gi"
              cpu: "2000m"

          # 存活探针
          livenessProbe:
            httpGet:
              path: /health
              port: http
            initialDelaySeconds: 30
            periodSeconds: 10
            timeoutSeconds: 5
            failureThreshold: 3

          # 就绪探针
          readinessProbe:
            httpGet:
              path: /health/ready
              port: http
            initialDelaySeconds: 10
            periodSeconds: 5
            timeoutSeconds: 3
            failureThreshold: 3

          # 启动探针（K8s 1.18+）
          startupProbe:
            httpGet:
              path: /health
              port: http
            initialDelaySeconds: 0
            periodSeconds: 10
            timeoutSeconds: 3
            failureThreshold: 30

          # 卷挂载
          volumeMounts:
            - name: data
              mountPath: /app/data
            - name: logs
              mountPath: /app/logs
            - name: temp
              mountPath: /tmp

      # 优雅关闭
      terminationGracePeriodSeconds: 30

      # 卷定义
      volumes:
        - name: data
          persistentVolumeClaim:
            claimName: video-ai-data-pvc
        - name: logs
          emptyDir: {}
        - name: temp
          emptyDir: {}
```

### 3.3 k8s/service.yaml

```yaml
apiVersion: v1
kind: Service
metadata:
  name: video-ai-api
  namespace: video-ai
  labels:
    app: video-ai
spec:
  type: LoadBalancer
  selector:
    app: video-ai
    component: api
  ports:
    - name: http
      port: 80
      targetPort: 8000
      protocol: TCP
    - name: https
      port: 443
      targetPort: 8000
      protocol: TCP
  sessionAffinity: ClientIP
  sessionAffinityConfig:
    clientIP:
      timeoutSeconds: 10800
```

### 3.4 k8s/hpa.yaml (自动扩缩容)

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: video-ai-api-hpa
  namespace: video-ai
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: video-ai-api
  minReplicas: 3
  maxReplicas: 10
  metrics:
    # CPU指标
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    # 内存指标
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
    # 自定义指标 - 等待队列长度
    - type: Pods
      pods:
        metric:
          name: queue_length
        target:
          type: AverageValue
          averageValue: "30"
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
        - type: Percent
          value: 50
          periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 0
      policies:
        - type: Percent
          value: 100
          periodSeconds: 15
        - type: Pods
          value: 2
          periodSeconds: 15
      selectPolicy: Max
```

### 3.5 k8s/pvc.yaml (持久化存储)

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: video-ai-data-pvc
  namespace: video-ai
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 500Gi
  storageClassName: standard

---

apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: video-ai-db-pvc
  namespace: video-ai
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 100Gi
  storageClassName: standard
```

---

## 4. CI/CD 流程

### 4.1 .github/workflows/deploy.yml

```yaml
name: Deploy to Production

on:
  push:
    branches: [main, master]
    tags:
      - 'v*'
  workflow_dispatch:

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  # 测试阶段
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
          cache: 'pip'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Run tests
        run: pytest tests/ --cov=src --cov-report=xml

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3

      - name: Run linting
        run: |
          flake8 src tests
          mypy src

  # 构建镜像
  build:
    needs: test
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

    steps:
      - uses: actions/checkout@v3

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2

      - name: Log in to Container Registry
        uses: docker/login-action@v2
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v4
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=ref,event=branch
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}
            type=sha

      - name: Build and push
        uses: docker/build-push-action@v4
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=registry,ref=${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:buildcache
          cache-to: type=registry,ref=${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:buildcache,mode=max

  # 部署到Kubernetes
  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment: production

    steps:
      - uses: actions/checkout@v3

      - name: Set up kubectl
        uses: azure/setup-kubectl@v3
        with:
          version: 'latest'

      - name: Configure kubectl
        run: |
          mkdir -p $HOME/.kube
          echo "${{ secrets.KUBE_CONFIG }}" | base64 --decode > $HOME/.kube/config
          chmod 600 $HOME/.kube/config

      - name: Deploy to Kubernetes
        run: |
          kubectl apply -f k8s/namespace.yaml
          kubectl apply -f k8s/deployment.yaml -n video-ai
          kubectl apply -f k8s/service.yaml -n video-ai
          kubectl set image deployment/video-ai-api \
            api=${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:latest \
            -n video-ai
          kubectl rollout status deployment/video-ai-api -n video-ai

      - name: Verify deployment
        run: |
          kubectl get pods -n video-ai
          kubectl get services -n video-ai

  # 通知
  notify:
    needs: [test, build, deploy]
    runs-on: ubuntu-latest
    if: always()

    steps:
      - name: Send Slack notification
        uses: 8398a7/action-slack@v3
        with:
          status: ${{ job.status }}
          text: 'Deploy ${{ needs.build.outputs.image_tag }} - ${{ job.status }}'
          webhook_url: ${{ secrets.SLACK_WEBHOOK }}
        if: always()
```

### 4.2 .github/workflows/test.yml

```yaml
name: Tests

on:
  pull_request:
    branches: [main, develop]
  push:
    branches: [develop]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15-alpine
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

      redis:
        image: redis:7-alpine
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
          cache: 'pip'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Run tests
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost/test_db
          REDIS_URL: redis://localhost:6379
        run: |
          pytest tests/ \
            --cov=src \
            --cov-report=xml \
            --cov-report=html \
            -v

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml
```

---

## 5. 监控和日志

### 5.1 Prometheus 配置 (prometheus.yml)

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    monitor: 'video-ai'

alerting:
  alertmanagers:
    - static_configs:
        - targets:
            - alertmanager:9093

rule_files:
  - 'rules/*.yml'

scrape_configs:
  # API应用监控
  - job_name: 'video-ai-api'
    static_configs:
      - targets: ['api:8000']
    metrics_path: '/metrics'

  # 数据库监控
  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']

  - job_name: 'mongodb'
    static_configs:
      - targets: ['mongo-exporter:9216']

  # Redis监控
  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']

  # Nginx监控
  - job_name: 'nginx'
    static_configs:
      - targets: ['nginx-exporter:9113']

  # 节点监控
  - job_name: 'node'
    static_configs:
      - targets: ['node-exporter:9100']
```

### 5.2 告警规则 (rules/alerts.yml)

```yaml
groups:
  - name: video-ai
    interval: 30s
    rules:
      # API异常检测
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
        for: 5m
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value }} errors per second"

      - alert: HighLatency
        expr: histogram_quantile(0.95, http_request_duration_seconds) > 1
        for: 5m
        annotations:
          summary: "High API latency"
          description: "p95 latency is {{ $value }}s"

      # 资源监控
      - alert: HighCPUUsage
        expr: node_cpu_usage > 0.8
        for: 5m
        annotations:
          summary: "High CPU usage"

      - alert: HighMemoryUsage
        expr: node_memory_usage > 0.8
        for: 5m
        annotations:
          summary: "High memory usage"

      - alert: DiskFull
        expr: node_disk_usage > 0.9
        for: 5m
        annotations:
          summary: "Disk space almost full"

      # 队列监控
      - alert: QueueDepthHigh
        expr: celery_queue_length{queue="video"} > 1000
        for: 10m
        annotations:
          summary: "Video processing queue is overloaded"

      # 数据库监控
      - alert: DatabaseConnectionHigh
        expr: pg_stat_activity_count > 80
        for: 5m
        annotations:
          summary: "High database connection count"

      - alert: DatabaseSlowQueries
        expr: rate(pg_slow_queries_total[5m]) > 10
        for: 5m
        annotations:
          summary: "High number of slow queries"
```

### 5.3 Docker-Compose 监控栈

```yaml
  prometheus:
    image: prom/prometheus:latest
    container_name: video-ai-prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - ./rules:/etc/prometheus/rules
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
    ports:
      - "9090:9090"
    networks:
      - video-ai-network

  grafana:
    image: grafana/grafana:latest
    container_name: video-ai-grafana
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
    volumes:
      - grafana_data:/var/lib/grafana
    ports:
      - "3000:3000"
    networks:
      - video-ai-network

  alertmanager:
    image: prom/alertmanager:latest
    container_name: video-ai-alertmanager
    volumes:
      - ./alertmanager.yml:/etc/alertmanager/alertmanager.yml
    command:
      - '--config.file=/etc/alertmanager/alertmanager.yml'
    ports:
      - "9093:9093"
    networks:
      - video-ai-network

  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.0.0
    container_name: video-ai-elasticsearch
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data
    ports:
      - "9200:9200"
    networks:
      - video-ai-network

  kibana:
    image: docker.elastic.co/kibana/kibana:8.0.0
    container_name: video-ai-kibana
    ports:
      - "5601:5601"
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
    networks:
      - video-ai-network

  logstash:
    image: docker.elastic.co/logstash/logstash:8.0.0
    container_name: video-ai-logstash
    volumes:
      - ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf
    ports:
      - "5000:5000/udp"
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
    networks:
      - video-ai-network
    depends_on:
      - elasticsearch
```

---

## 6. 安全配置

### 6.1 SSL/TLS 证书配置

**使用 Let's Encrypt (免费)**

```bash
# 安装 certbot
apt-get install certbot python3-certbot-nginx

# 获取证书
certbot certonly --nginx -d api.video-ai.com

# 自动续约 (Cron任务)
0 12 * * * /usr/bin/certbot renew --quiet
```

**Docker中使用 mkcert (本地开发)**

```dockerfile
RUN apt-get install -y mkcert && \
    mkcert -install && \
    mkcert -cert-file=/etc/nginx/ssl/cert.pem \
           -key-file=/etc/nginx/ssl/key.pem \
           localhost api.local
```

### 6.2 API密钥管理

**使用 HashiCorp Vault**

```bash
# 启动Vault
vault server -dev

# 存储密钥
vault kv put secret/video-ai \
  openai_api_key="sk-xxx" \
  database_url="postgresql://..." \
  redis_password="xxx"

# 在应用中读取
from hvac import Client

client = Client(url='http://vault:8200')
secrets = client.secrets.kv.read_secret_version(path='secret/video-ai')
```

### 6.3 RBAC 和访问控制

```yaml
# Kubernetes RBAC
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: video-ai-api
  namespace: video-ai
rules:
  - apiGroups: [""]
    resources: ["configmaps", "secrets"]
    verbs: ["get", "list"]
  - apiGroups: [""]
    resources: ["pods"]
    verbs: ["get", "list"]

---

apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: video-ai-api
  namespace: video-ai
subjects:
  - kind: ServiceAccount
    name: video-ai-api
    namespace: video-ai
roleRef:
  kind: Role
  name: video-ai-api
  apiGroup: rbac.authorization.k8s.io
```

### 6.4 网络策略

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: video-ai-network-policy
  namespace: video-ai
spec:
  podSelector:
    matchLabels:
      app: video-ai
  policyTypes:
    - Ingress
    - Egress
  ingress:
    - from:
        - podSelector:
            matchLabels:
              role: frontend
      ports:
        - protocol: TCP
          port: 8000
  egress:
    - to:
        - podSelector:
            matchLabels:
              app: postgres
      ports:
        - protocol: TCP
          port: 5432
    - to:
        - podSelector:
            matchLabels:
              app: redis
      ports:
        - protocol: TCP
          port: 6379
```

---

## 总结

本文档提供了Video-AI的完整企业级部署方案，包括：

1. **Docker容器化** - 完整的dockerfile和docker-compose配置
2. **Kubernetes编排** - 生产级K8s部署配置
3. **CI/CD流程** - 自动化测试和部署
4. **监控告警** - Prometheus + Grafana + ELK日志系统
5. **安全配置** - SSL/TLS、密钥管理、RBAC、网络策略

通过本方案，可以实现高可用、高性能、安全的企业级部署。
