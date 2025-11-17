# Video-AI 运维手册

## 1. 安装和启动

### 1.1 环境准备

**系统要求：**
- OS: Linux (Ubuntu 20.04+) / CentOS 7+ / macOS
- CPU: 4核心+
- RAM: 8GB+
- 存储: 500GB+ (视频存储)
- Docker: 20.10+
- Docker Compose: 1.29+
- Kubernetes: 1.20+ (可选)

**安装Docker和Docker Compose：**

```bash
# Ubuntu
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 1.2 使用Docker Compose启动

**步骤1：克隆项目**

```bash
git clone https://github.com/yourusername/video-ai.git
cd video-ai
```

**步骤2：准备环境文件**

```bash
# 复制示例环境文件
cp .env.example .env

# 编辑配置
nano .env

# 必须配置的环节变量：
OPENAI_API_KEY=sk-xxx
GOOGLE_API_KEY=xxx
DB_PASSWORD=strong_password_here
REDIS_PASSWORD=strong_redis_password
MONGO_PASSWORD=strong_mongo_password
```

**步骤3：启动服务**

```bash
# 构建镜像
docker-compose build

# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f api

# 等待所有服务就绪（通常2-3分钟）
docker-compose ps
```

**步骤4：初始化数据库**

```bash
# 执行数据库迁移
docker-compose exec api python -m alembic upgrade head

# 创建默认用户
docker-compose exec api python scripts/init_users.py

# 验证连接
docker-compose exec postgres psql -U postgres -c "SELECT 1"
```

**步骤5：验证部署**

```bash
# 检查API健康状态
curl http://localhost:8000/health

# 预期响应
{
  "status": "healthy",
  "timestamp": "2024-11-17T12:00:00Z",
  "services": {
    "database": "ok",
    "cache": "ok",
    "ai_models": "ok"
  }
}

# 查看Swagger文档
open http://localhost:8000/docs
```

### 1.3 使用Kubernetes启动

```bash
# 创建命名空间
kubectl apply -f k8s/namespace.yaml

# 创建Secret
kubectl create secret generic api-secrets \
  --from-literal=openai-key=$OPENAI_API_KEY \
  --from-literal=google-key=$GOOGLE_API_KEY \
  --from-literal=database-url=$DATABASE_URL \
  -n video-ai

# 部署
kubectl apply -f k8s/
kubectl apply -f k8s/pvc.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/hpa.yaml

# 验证
kubectl get all -n video-ai
kubectl logs -f deployment/video-ai-api -n video-ai
```

---

## 2. 常见问题处理

### 2.1 API无法启动

**症状：** 容器反复重启

**诊断：**

```bash
# 查看错误日志
docker-compose logs api

# 检查依赖服务
docker-compose ps

# 测试数据库连接
docker-compose exec api python -c "from sqlalchemy import create_engine; engine = create_engine(os.getenv('DATABASE_URL')); engine.execute('SELECT 1')"
```

**常见原因和解决：**

| 错误信息 | 原因 | 解决方案 |
|--------|------|--------|
| `psycopg2.OperationalError: could not connect` | 数据库未就绪 | 等待PostgreSQL启动或检查连接字符串 |
| `ModuleNotFoundError: No module named 'xxx'` | 依赖安装失败 | 重新构建镜像: `docker-compose build --no-cache` |
| `SSL: CERTIFICATE_VERIFY_FAILED` | SSL证书问题 | 检查/更新SSL证书或禁用SSL验证 |
| `OPENAI_API_KEY not set` | 环境变量缺失 | 检查.env文件和docker-compose.yml |
| `Out of memory` | 内存不足 | 增加Docker内存或优化应用 |

### 2.2 数据库连接失败

```bash
# 检查PostgreSQL状态
docker-compose exec postgres pg_isready -h localhost

# 检查连接数
docker-compose exec postgres psql -U postgres -c "SELECT count(*) FROM pg_stat_activity;"

# 重置密码
docker-compose exec postgres psql -U postgres -c "ALTER USER postgres WITH PASSWORD 'newpassword';"

# 重建数据库
docker-compose down -v  # 删除所有数据（谨慎！）
docker-compose up -d
docker-compose exec api python -m alembic upgrade head
```

### 2.3 视频处理异常

**症状：** 视频处理超时或失败

```bash
# 检查Worker状态
docker-compose logs celery-worker-video

# 检查任务队列
docker-compose exec redis redis-cli LLEN celery

# 查看失败任务
docker-compose exec redis redis-cli LLEN celery::failed

# 重新处理失败的任务
docker-compose exec api python scripts/retry_failed_jobs.py
```

**常见原因：**

| 问题 | 解决方案 |
|------|--------|
| 内存溢出 | 减少并发worker数: `celery -c 1` |
| FFmpeg崩溃 | 检查FFmpeg版本: `ffmpeg -version` |
| GPU显存不足 | 减少批处理大小或使用CPU |
| 网络超时 | 增加超时配置: `task_soft_time_limit=3600` |

### 2.4 Redis连接问题

```bash
# 检查Redis状态
docker-compose exec redis redis-cli ping

# 查看内存使用
docker-compose exec redis redis-cli INFO memory

# 清理过期数据
docker-compose exec redis redis-cli FLUSHDB

# 监控Redis命令
docker-compose exec redis redis-cli MONITOR
```

---

## 3. 性能调优

### 3.1 数据库优化

**索引优化：**

```sql
-- 创建常用查询的索引
CREATE INDEX idx_video_user_id ON videos(user_id);
CREATE INDEX idx_video_created_at ON videos(created_at);
CREATE INDEX idx_job_status ON jobs(status, created_at);

-- 检查慢查询
SELECT query, calls, mean_time FROM pg_stat_statements
ORDER BY mean_time DESC LIMIT 10;

-- 分析查询计划
EXPLAIN ANALYZE SELECT * FROM videos
WHERE user_id = 'user123' AND created_at > NOW() - INTERVAL '7 days';
```

**连接池优化：**

```python
# sqlalchemy.create_engine配置
engine = create_engine(
    DATABASE_URL,
    pool_size=20,           # 连接池大小
    max_overflow=40,        # 最大溢出连接数
    pool_recycle=3600,      # 连接回收时间
    pool_pre_ping=True      # 测试连接有效性
)
```

**查询优化：**

```python
# 使用eager loading避免N+1问题
from sqlalchemy.orm import joinedload

# 不推荐（N+1查询）
videos = db.query(Video).all()
for video in videos:
    print(video.user.name)  # 每个都会触发一次查询

# 推荐（单一查询）
videos = db.query(Video).options(joinedload(Video.user)).all()
```

### 3.2 缓存优化

```python
# Redis内存优化
# 1. 使用更紧凑的数据结构
# 2. 设置合理的过期时间
# 3. 启用LRU淘汰策略

# redis.conf
maxmemory 4gb
maxmemory-policy allkeys-lru
```

**缓存预热：**

```python
from datetime import datetime, timedelta

async def warm_up_cache():
    """启动时预加载热点数据"""
    # 加载热门视频
    hot_videos = db.query(Video) \
        .filter(Video.view_count > 1000) \
        .all()

    for video in hot_videos:
        key = f"video:details:{video.id}"
        await redis.setex(key, 3600, json.dumps(video.dict()))

    # 在启动脚本中调用
    # asyncio.run(warm_up_cache())
```

### 3.3 API性能优化

```python
# 启用Gzip压缩
from fastapi.middleware.gzip import GZIPMiddleware
app.add_middleware(GZIPMiddleware, minimum_size=1000)

# 启用CORS缓存
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    max_age=3600  # 1小时
)

# 连接池优化
from httpx import AsyncClient
client = AsyncClient(
    limits=httpx.Limits(max_keepalive_connections=100)
)

# 异步处理
@app.get("/api/v1/videos")
async def list_videos():
    # 并发查询
    videos, total = await asyncio.gather(
        db.query(Video).offset(0).limit(10).all(),
        db.query(Video).count()
    )
    return {"videos": videos, "total": total}
```

### 3.4 容器资源优化

```yaml
# docker-compose.yml
services:
  api:
    resources:
      limits:
        cpus: '2'          # 限制CPU
        memory: 4G         # 限制内存
      reservations:
        cpus: '1'          # 预留CPU
        memory: 2G         # 预留内存

# Kubernetes HPA
kubectl autoscale deployment video-ai-api \
  --min=3 \
  --max=10 \
  --cpu-percent=70
```

---

## 4. 备份和恢复

### 4.1 数据库备份

**自动每日备份：**

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/backups/database"
DB_NAME="video_ai"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# PostgreSQL备份
pg_dump -h postgres -U postgres -d $DB_NAME | gzip > $BACKUP_DIR/pg_$TIMESTAMP.sql.gz

# MongoDB备份
mongodump --uri "mongodb://admin:password@mongo:27017/video_ai" -o $BACKUP_DIR/mongo_$TIMESTAMP

# 保留最近7天的备份
find $BACKUP_DIR -type f -mtime +7 -delete

# 上传到S3
aws s3 sync $BACKUP_DIR s3://backup-bucket/video-ai-db/
```

**Cron定时任务：**

```bash
# 编辑crontab
crontab -e

# 每天凌晨2点执行备份
0 2 * * * /home/user/scripts/backup.sh >> /var/log/backup.log 2>&1
```

### 4.2 数据库恢复

```bash
# PostgreSQL恢复
docker-compose exec postgres bash -c \
  'psql -U postgres < /backup/pg_backup.sql'

# 或从压缩文件
docker-compose exec postgres bash -c \
  'gunzip < /backup/pg_backup.sql.gz | psql -U postgres'

# MongoDB恢复
docker-compose exec mongo bash -c \
  'mongorestore --uri "mongodb://admin:password@localhost:27017" /backup/mongo'
```

### 4.3 持久卷备份

```bash
# 备份数据卷
docker run --rm \
  -v video-ai_data:/data \
  -v /backups:/backup \
  alpine tar czf /backup/data_$(date +%s).tar.gz -C /data .

# 恢复数据卷
docker run --rm \
  -v video-ai_data:/data \
  -v /backups:/backup \
  alpine tar xzf /backup/data_latest.tar.gz -C /data
```

---

## 5. 升级流程

### 5.1 蓝绿部署（推荐）

```yaml
# 部署v2.0.0同时运行v1.9.0
services:
  api-v1:  # 旧版本
    image: video-ai:1.9.0
    port: 8000

  api-v2:  # 新版本
    image: video-ai:2.0.0
    port: 8001

  nginx:
    # 初始流量100% → v1
    # 测试后切换到v2
    # 验证无误后删除v1
```

**Kubernetes蓝绿部署：**

```bash
# 步骤1：部署新版本
kubectl set image deployment/video-ai-api \
  api=video-ai:2.0.0 \
  --record

# 步骤2：验证新版本
kubectl rollout status deployment/video-ai-api

# 步骤3：如需回滚
kubectl rollout undo deployment/video-ai-api
kubectl rollout history deployment/video-ai-api
```

### 5.2 灰度部署

```yaml
# Istio VirtualService（流量逐步切换）
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: video-ai-api
spec:
  hosts:
  - api.video-ai.com
  http:
  # 第一阶段：5% → v2
  - match:
    - uri:
        prefix: /
    route:
    - destination:
        host: video-ai-api-v1
      weight: 95
    - destination:
        host: video-ai-api-v2
      weight: 5

  # 监控后切换
  # - match:
  #   - uri:
  #       prefix: /
  #   route:
  #   - destination:
  #       host: video-ai-api-v2
  #     weight: 100
```

### 5.3 数据库迁移

```bash
# 步骤1：创建迁移脚本
alembic revision -m "add_new_column"

# 步骤2：编辑迁移文件
# alembic/versions/xxx_add_new_column.py

# 步骤3：运行迁移
docker-compose exec api python -m alembic upgrade head

# 步骤4：验证
docker-compose exec postgres psql -U postgres -d video_ai -c "\d videos"

# 步骤5：回滚（如需要）
docker-compose exec api python -m alembic downgrade -1
```

---

## 6. 日志管理

### 6.1 日志聚合

```python
# 使用ELK收集日志
from loguru import logger
import json

logger.add(
    "logs/app.log",
    rotation="500 MB",      # 大小轮转
    retention="7 days",     # 保留时间
    level="INFO",
    format="{time} | {level: <8} | {name}:{function}:{line} - {message}",
    serialize=True          # JSON格式
)

# 发送到Elasticsearch
logger.add(
    "http://elasticsearch:9200/video-ai-{time:YYYY-MM-DD}",
    format=lambda msg: json.dumps({
        "timestamp": msg["record"]["time"],
        "level": msg["record"]["level"].name,
        "message": msg["message"],
        "service": "video-ai",
    })
)
```

### 6.2 日志分析

```bash
# 查看实时日志
docker-compose logs -f api

# 查看特定时间范围的日志
docker-compose logs --since 1h api

# 搜索错误日志
docker-compose logs api | grep ERROR

# Kibana查询
# 访问 http://localhost:5601
# Index pattern: video-ai-*
# 查询: level: ERROR AND timestamp: [now-1h TO now]
```

---

## 7. 监控告警

### 7.1 关键指标监控

```
需要监控的指标：
├─ 系统指标
│  ├─ CPU使用率 (> 80%)
│  ├─ 内存使用率 (> 85%)
│  ├─ 磁盘使用率 (> 90%)
│  └─ 网络I/O
│
├─ 应用指标
│  ├─ API响应时间 (p95 > 1s)
│  ├─ 错误率 (> 1%)
│  ├─ 并发连接数
│  └─ 请求队列长度
│
├─ 数据库指标
│  ├─ 连接数 (> 80)
│  ├─ 查询耗时 (> 1s)
│  ├─ 事务数
│  └─ 表空间使用
│
└─ 业务指标
   ├─ 视频处理成功率 (< 99%)
   ├─ 平均处理时间
   ├─ 用户活跃度
   └─ API调用量
```

### 7.2 告警配置

```yaml
# prometheus/rules/alerts.yml
groups:
  - name: critical
    rules:
      - alert: ServiceDown
        expr: up{job="video-ai"} == 0
        for: 5m
        annotations:
          severity: critical
          summary: "Video AI service is down"

      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.01
        for: 5m
        annotations:
          severity: warning
          summary: "High error rate: {{ $value }}"

      - alert: DiskAlmostFull
        expr: node_filesystem_avail_bytes / node_filesystem_size_bytes < 0.1
        for: 5m
        annotations:
          severity: critical
```

### 7.3 告警通知

```yaml
# alertmanager.yml
global:
  resolve_timeout: 5m
  slack_api_url: 'https://hooks.slack.com/services/YOUR/WEBHOOK'

route:
  receiver: 'slack'
  group_by: ['alertname']
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 4h

receivers:
  - name: 'slack'
    slack_configs:
      - channel: '#alerts'
        title: 'Alert: {{ .GroupLabels.alertname }}'
        text: '{{ range .Alerts }}{{ .Annotations.summary }}{{ end }}'
```

---

## 8. 安全检查清单

### 8.1 部署前检查

- [ ] SSL/TLS证书已配置
- [ ] API密钥已从代码中移除
- [ ] 数据库密码已修改
- [ ] Redis认证已启用
- [ ] 防火墙规则已配置
- [ ] 备份系统已测试
- [ ] 日志聚合已启用
- [ ] 监控告警已配置
- [ ] 访问控制已限制
- [ ] 代码审查已完成

### 8.2 定期安全审计

```bash
# 检查容器漏洞
docker scan video-ai:latest

# 检查依赖漏洞
pip-audit

# 检查代码静态分析
bandit -r src/

# 检查容器配置
docker run --rm -it \
  -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy:latest image video-ai:latest
```

---

## 9. 故障恢复

### 9.1 故障分类和处理

| 故障类型 | 症状 | 恢复步骤 |
|---------|------|--------|
| API崩溃 | 无响应 | 1. 检查日志 2. 重启容器 3. 回滚版本 |
| 数据库故障 | 连接超时 | 1. 检查数据库状态 2. 重启服务 3. 恢复备份 |
| 磁盘满 | 写入失败 | 1. 清理临时文件 2. 扩展存储 3. 归档日志 |
| 内存溢出 | OOM | 1. 重启应用 2. 优化代码 3. 增加资源 |
| 网络故障 | 超时 | 1. 检查网络 2. 检查DNS 3. 检查防火墙 |

### 9.2 故障转移

```bash
# 主节点故障时自动转移到从节点
# PostgreSQL级联复制

# 在从节点上提升为主节点
docker-compose exec postgres-replica bash -c \
  'pg_ctl promote -D $PGDATA'

# MongoDB副本集自动故障转移
mongo_replica_set_example:
  # 自动选举新的主节点
  # 无需人工干预
```

---

## 总结

本运维手册涵盖了Video-AI系统的完整生命周期管理，从安装启动到故障恢复。通过遵循本手册的建议，可以确保系统的高可用性和稳定性。

关键要点：
- 定期备份数据
- 持续监控关键指标
- 快速响应告警
- 定期安全审计
- 保持文档更新
