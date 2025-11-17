# Video-AI 扩展性设计文档

## 1. 架构可扩展性

### 1.1 水平扩展策略

**问题:** 单点应用无法处理大量并发请求

**解决方案:** 无状态设计 + 负载均衡

```
用户流量
   ↓
  LB1 (Nginx)
   ├─ API服务器 1
   ├─ API服务器 2
   ├─ API服务器 3
   └─ API服务器 N
```

**实现方式：**

```python
# 1. 无状态API设计
from fastapi import FastAPI
from sqlalchemy.orm import Session

app = FastAPI()

@app.post("/api/v1/videos/process")
async def process_video(
    video_id: str,
    db: Session = Depends(get_db),
    cache: Redis = Depends(get_redis)
) -> JobResponse:
    """
    无状态设计：
    - 所有状态存储在DB/Cache中
    - 请求可以被任意实例处理
    - 可以随意添加/移除实例
    """
    job = await save_job_to_db(db, video_id)
    await cache.setex(f"job:{job.id}", 3600, json.dumps(job.dict()))
    return job
```

**扩展步骤：**

```bash
# 1. 当CPU/内存使用率 > 70% 时触发扩展
kubectl scale deployment video-ai-api --replicas=5

# 2. Kubernetes自动扩展
kubectl autoscale deployment video-ai-api --min=3 --max=10

# 3. 验证
kubectl get pods -n video-ai
```

### 1.2 垂直扩展 (提升单个实例性能)

```yaml
# resources/limits 配置
resources:
  requests:
    cpu: 1000m      # 初始
    memory: 2Gi
  limits:
    cpu: 2000m      # 最多
    memory: 4Gi

# 优化措施
1. 增加CPU核心
2. 增加内存容量
3. 使用更快的存储
4. 使用GPU加速
```

**GPU加速示例：**

```yaml
# k8s中启用GPU
spec:
  containers:
  - name: api
    image: video-ai:latest
    resources:
      limits:
        nvidia.com/gpu: 1  # 请求1个GPU

# FFmpeg使用GPU编码
ffmpeg -hwaccel cuda -c:v h264_cuvid \
  -i input.mp4 \
  -c:v h264_nvenc \
  -b:v 5000k \
  output.mp4
```

---

## 2. 负载均衡

### 2.1 负载均衡算法

```
算法            特点                  适用场景
─────────────────────────────────────────────────
轮询            简单公平              同质服务器
加权轮询        按能力分配            异质服务器
最少连接        优先选择空闲          长连接
IP Hash         会话保持              需要会话的请求
一致哈希        最小化缓存失效        分布式缓存
```

**Nginx配置示例：**

```nginx
# 1. 轮询（默认）
upstream api {
    server api1:8000;
    server api2:8000;
    server api3:8000;
}

# 2. 加权轮询
upstream api {
    server api1:8000 weight=5;  # 高性能服务器
    server api2:8000 weight=3;  # 中等性能
    server api3:8000 weight=1;  # 低性能
}

# 3. 最少连接
upstream api {
    least_conn;
    server api1:8000;
    server api2:8000;
}

# 4. IP Hash（会话保持）
upstream api {
    ip_hash;
    server api1:8000;
    server api2:8000;
}

# 5. 一致哈希
upstream api {
    hash $request_uri consistent;
    server api1:8000;
    server api2:8000;
}
```

### 2.2 分布式会话管理

```python
# 使用Redis存储会话
from fastapi_sessions.backends.sessionbackend import SessionBackend
from redis import Redis

class RedisSessionBackend(SessionBackend):
    def __init__(self, redis_client: Redis):
        self.redis = redis_client
        self.prefix = "session:"

    async def read(self, session_id: str) -> dict:
        data = await self.redis.get(f"{self.prefix}{session_id}")
        return json.loads(data) if data else {}

    async def write(self, session_id: str, data: dict) -> None:
        await self.redis.setex(
            f"{self.prefix}{session_id}",
            3600,  # 1小时过期
            json.dumps(data)
        )

# 使用
@app.post("/api/v1/login")
async def login(username: str, password: str) -> Response:
    session_id = str(uuid.uuid4())
    await session_backend.write(session_id, {
        "user_id": user.id,
        "username": username,
        "login_time": datetime.now().isoformat()
    })
    return {"session_id": session_id}
```

---

## 3. 缓存策略

### 3.1 多层缓存架构

```
┌─────────────────────────────────────────┐
│          用户请求                        │
└────────────────┬────────────────────────┘
                 │
         ┌───────▼────────┐
         │ 浏览器缓存      │ (CDN)
         └───────┬────────┘
                 │
         ┌───────▼────────┐
         │ 应用缓存        │ (Redis)
         │ - 热点数据     │
         │ - 计算结果     │
         └───────┬────────┘
                 │
         ┌───────▼────────┐
         │ 数据库缓存      │ (MySQL缓冲池)
         │ - 索引         │
         │ - 查询结果缓存 │
         └───────┬────────┘
                 │
         ┌───────▼────────┐
         │ 数据库          │
         │ (主从复制)     │
         └────────────────┘
```

### 3.2 缓存实现

```python
from functools import lru_cache
from redis import Redis
from datetime import datetime, timedelta
import json

class CacheManager:
    def __init__(self, redis_client: Redis):
        self.redis = redis_client
        self.ttl = 3600  # 1小时

    async def get_or_compute(
        self,
        key: str,
        compute_fn,
        ttl: int = None
    ):
        """
        缓存获取或计算
        """
        # 先从缓存读取
        cached = await self.redis.get(key)
        if cached:
            return json.loads(cached)

        # 计算
        result = await compute_fn()

        # 写入缓存
        await self.redis.setex(
            key,
            ttl or self.ttl,
            json.dumps(result)
        )

        return result

# 使用示例
@app.get("/api/v1/videos/{video_id}/stats")
async def get_video_stats(video_id: str) -> VideoStats:
    key = f"video:stats:{video_id}"

    def compute():
        return db.query(VideoStats).filter(
            VideoStats.video_id == video_id
        ).first()

    return await cache_manager.get_or_compute(key, compute)
```

### 3.3 缓存一致性

```python
# 缓存失效策略

class CacheInvalidator:
    def __init__(self, redis: Redis):
        self.redis = redis

    # 1. 主动失效（更推荐）
    async def invalidate_on_update(self, video_id: str):
        """更新视频时立即失效相关缓存"""
        await self.redis.delete(f"video:stats:{video_id}")
        await self.redis.delete(f"video:details:{video_id}")
        # 发布事件通知其他实例
        await self.redis.publish("cache_invalidate", video_id)

    # 2. 延迟失效
    async def set_with_expiry(self, key: str, value: dict, ttl: int = 3600):
        """设置缓存时指定过期时间"""
        await self.redis.setex(key, ttl, json.dumps(value))

    # 3. 更新时同时更新缓存
    async def update_cache(self, video_id: str, new_stats: dict):
        """先更新DB，再更新缓存"""
        # 更新数据库
        db_result = await db.update_video_stats(video_id, new_stats)

        # 更新缓存
        key = f"video:stats:{video_id}"
        await self.redis.setex(key, 3600, json.dumps(db_result))

        return db_result

    # 4. 防止缓存雪崩
    async def get_with_lock(self, key: str, compute_fn):
        """使用分布式锁防止缓存击穿"""
        cached = await self.redis.get(key)
        if cached:
            return json.loads(cached)

        # 尝试获取锁
        lock_key = f"{key}:lock"
        lock = await self.redis.set(
            lock_key,
            "1",
            nx=True,  # 只在不存在时设置
            ex=5      # 5秒过期
        )

        if lock:
            try:
                # 获得锁，执行计算
                result = await compute_fn()
                await self.redis.setex(key, 3600, json.dumps(result))
                return result
            finally:
                await self.redis.delete(lock_key)
        else:
            # 未获得锁，等待其他实例计算
            await asyncio.sleep(0.1)
            return await self.get_with_lock(key, compute_fn)
```

---

## 4. 数据库扩展

### 4.1 读写分离

```
应用
 ├─ 写操作 → 主库 (Master)
 │
 ├─ 读操作 → 从库1 (Slave1)
 │         → 从库2 (Slave2)
 │         → 从库3 (Slave3)
 │
 └─ 异步同步
```

**实现方式：**

```python
from sqlalchemy import create_engine
from sqlalchemy_utils import create_database, database_exists

class DatabaseManager:
    def __init__(self):
        # 主库（写）
        self.master = create_engine(
            os.getenv("DATABASE_URL_MASTER"),
            pool_size=20,
            max_overflow=40,
            echo=False
        )

        # 从库（读）
        self.replicas = [
            create_engine(
                f"postgresql://user:pass@replica{i}:5432/video_ai",
                pool_size=20
            )
            for i in range(1, 4)
        ]
        self.replica_index = 0

    def get_read_session(self):
        """获取读连接（负载均衡）"""
        engine = self.replicas[self.replica_index]
        self.replica_index = (self.replica_index + 1) % len(self.replicas)
        return Session(engine)

    def get_write_session(self):
        """获取写连接"""
        return Session(self.master)

# 依赖注入
@app.get("/api/v1/videos")
async def list_videos(
    skip: int = 0,
    limit: int = 10,
    read_db: Session = Depends(lambda: db_manager.get_read_session())
):
    """使用从库查询"""
    return read_db.query(Video).offset(skip).limit(limit).all()

@app.post("/api/v1/videos")
async def create_video(
    video: VideoCreate,
    write_db: Session = Depends(lambda: db_manager.get_write_session())
):
    """使用主库写入"""
    new_video = Video(**video.dict())
    write_db.add(new_video)
    write_db.commit()
    return new_video
```

### 4.2 数据库分片

```
用户ID哈希
   ↓
┌─────────────────────────────┐
│ hash(user_id) % 4           │
└──────┬──────────────────────┘
       │
   ┌───┼───┬───┬───┐
   ↓   ↓   ↓   ↓   ↓
  DB1 DB2 DB3 DB4 (分片数据库)
```

**实现方式：**

```python
class ShardManager:
    """数据库分片管理"""

    def __init__(self, num_shards: int = 4):
        self.num_shards = num_shards
        self.shards = []

        # 初始化分片
        for i in range(num_shards):
            engine = create_engine(
                f"postgresql://user:pass@shard{i}:5432/video_ai"
            )
            self.shards.append(engine)

    def get_shard_id(self, user_id: str) -> int:
        """计算分片ID"""
        return hash(user_id) % self.num_shards

    def get_shard_engine(self, user_id: str):
        """获取分片引擎"""
        shard_id = self.get_shard_id(user_id)
        return self.shards[shard_id]

# 使用
@app.post("/api/v1/users/{user_id}/videos")
async def create_user_video(
    user_id: str,
    video: VideoCreate
):
    engine = shard_manager.get_shard_engine(user_id)
    session = Session(engine)

    new_video = Video(user_id=user_id, **video.dict())
    session.add(new_video)
    session.commit()
    return new_video
```

**分片键选择：**
- 用户ID（最常见）
- 视频ID
- 组织ID

**分片策略：**
- Range分片（按范围）
- Hash分片（按哈希）
- List分片（按列表）
- Directory分片（查询表映射）

### 4.3 数据库备份和恢复

```bash
# PostgreSQL备份
pg_dump -h localhost -U postgres -d video_ai > backup.sql
# 或（二进制）
pg_basebackup -h localhost -U replicator -D backup/ -Fp -Xs -P

# 恢复
psql -h localhost -U postgres -d video_ai < backup.sql

# MongoDB备份
mongodump --uri "mongodb://localhost:27017/video_ai" -o backup/

# MongoDB恢复
mongorestore --uri "mongodb://localhost:27017" backup/
```

---

## 5. 消息队列

### 5.1 异步任务处理

```
请求
  ↓
API (立即返回)
  ├→ 任务入队
  │   └→ Redis/RabbitMQ
  │
  └→ Celery Worker (后台处理)
       ├─ Worker 1 (视频处理)
       ├─ Worker 2 (AI分析)
       └─ Worker 3 (数据导出)
```

**实现方式：**

```python
from celery import Celery, Task
from redis import Redis

# 初始化Celery
app = Celery(
    'video_ai',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/1'
)

# 任务定义
@app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    time_limit=3600  # 1小时超时
)
def process_video_task(
    self,
    video_id: str,
    user_interests: list
) -> dict:
    """处理视频"""
    try:
        # 更新状态
        video = db.get_video(video_id)
        video.status = "processing"
        db.commit()

        # 执行处理
        result = video_processor.process(
            video_id,
            user_interests
        )

        # 保存结果
        video.status = "completed"
        video.result = result
        db.commit()

        return result

    except Exception as exc:
        # 重试逻辑
        self.retry(exc=exc, countdown=60)

# 在API中提交任务
@app.post("/api/v1/videos/{video_id}/process")
async def process_video(
    video_id: str,
    interests: List[str]
) -> JobResponse:
    # 提交任务
    task = process_video_task.apply_async(
        args=(video_id, interests),
        priority=8,  # 优先级0-9
        expires=3600  # 1小时后过期
    )

    return {
        "job_id": task.id,
        "status": "pending",
        "video_id": video_id
    }

# 获取任务状态
@app.get("/api/v1/jobs/{job_id}")
async def get_job_status(job_id: str) -> JobStatus:
    task = process_video_task.AsyncResult(job_id)

    return {
        "job_id": job_id,
        "status": task.status,  # PENDING, PROGRESS, SUCCESS, FAILURE
        "progress": task.info.get("progress", 0),
        "result": task.result
    }
```

### 5.2 Celery配置优化

```python
from celery import Celery
from kombu import Exchange, Queue

app = Celery('video_ai')

# 队列配置
app.conf.task_queues = (
    Queue('default', Exchange('default'), routing_key='default'),
    Queue('video', Exchange('video'), routing_key='video.*'),
    Queue('ai', Exchange('ai'), routing_key='ai.*'),
    Queue('priority', Exchange('priority'), routing_key='priority.*'),
)

# 路由规则
app.conf.task_routes = {
    'tasks.process_video_task': {'queue': 'video'},
    'tasks.analyze_content_task': {'queue': 'ai'},
    'tasks.generate_transition_task': {'queue': 'ai'},
    'tasks.cleanup_temp_files': {'queue': 'default'},
}

# 任务优先级
app.conf.task_default_priority = 5
app.conf.task_default_rate_limit = '100/h'  # 每小时限制

# Worker配置
app.conf.worker_prefetch_multiplier = 4  # 预加载任务数
app.conf.worker_max_tasks_per_child = 1000  # 进程重用
app.conf.worker_disable_rate_limits = False

# 结果存储
app.conf.result_expires = 3600  # 结果保留1小时
app.conf.result_compression = 'gzip'
```

---

## 6. 时间序列数据优化

### 6.1 InfluxDB 时间序列数据

```python
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS

# 初始化
client = InfluxDBClient(
    url="http://localhost:8086",
    token="your-token",
    org="video-ai"
)

write_api = client.write_api(write_type=SYNCHRONOUS)
query_api = client.query_api()

# 写入指标
def record_processing_metric(
    video_id: str,
    duration: float,
    quality_score: float
):
    """记录视频处理指标"""
    from influxdb_client.client.write.point import Point

    point = Point("video_processing") \
        .tag("video_id", video_id) \
        .field("duration_seconds", duration) \
        .field("quality_score", quality_score) \
        .time(datetime.utcnow())

    write_api.write(bucket="video-ai", record=point)

# 查询指标
def get_processing_stats(video_id: str) -> dict:
    """查询视频处理统计"""
    query = f'''
    from(bucket: "video-ai")
        |> range(start: -7d)
        |> filter(fn: (r) => r._measurement == "video_processing")
        |> filter(fn: (r) => r.video_id == "{video_id}")
    '''

    result = query_api.query(org="video-ai", query=query)

    stats = {}
    for table in result:
        for record in table.records:
            field = record.field
            value = record.value
            if field not in stats:
                stats[field] = []
            stats[field].append(value)

    return {
        "avg_duration": sum(stats.get("duration_seconds", [0])) / len(stats.get("duration_seconds", [1])),
        "avg_quality": sum(stats.get("quality_score", [0])) / len(stats.get("quality_score", [1]))
    }
```

---

## 7. 全文搜索

### 7.1 Elasticsearch 集成

```python
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

# 初始化
es = Elasticsearch(['http://localhost:9200'])

# 创建索引
def create_video_index():
    mapping = {
        "settings": {
            "number_of_shards": 3,
            "number_of_replicas": 2,
            "analysis": {
                "analyzer": {
                    "default": {
                        "type": "standard",
                        "stopwords": "_english_"
                    }
                }
            }
        },
        "mappings": {
            "properties": {
                "video_id": {"type": "keyword"},
                "title": {"type": "text", "analyzer": "default"},
                "description": {"type": "text"},
                "tags": {"type": "keyword"},
                "duration": {"type": "integer"},
                "created_at": {"type": "date"},
                "view_count": {"type": "integer"}
            }
        }
    }

    es.indices.create(index="videos", body=mapping, ignore=400)

# 索引视频
async def index_video(video: Video):
    doc = {
        "video_id": str(video.id),
        "title": video.title,
        "description": video.description,
        "tags": video.tags,
        "duration": video.duration,
        "created_at": video.created_at,
        "view_count": video.view_count
    }

    es.index(index="videos", id=str(video.id), body=doc)

# 搜索视频
async def search_videos(query: str, limit: int = 20) -> List[Video]:
    search_body = {
        "query": {
            "multi_match": {
                "query": query,
                "fields": ["title^3", "description", "tags"]
            }
        },
        "size": limit
    }

    results = es.search(index="videos", body=search_body)

    return [
        Video.from_dict(hit["_source"])
        for hit in results["hits"]["hits"]
    ]

# 聚合分析
async def get_trending_tags() -> List[dict]:
    agg_body = {
        "aggs": {
            "trending_tags": {
                "terms": {
                    "field": "tags",
                    "size": 10
                }
            }
        }
    }

    results = es.search(index="videos", body=agg_body)
    return results["aggregations"]["trending_tags"]["buckets"]
```

---

## 8. 成本优化

### 8.1 自动扩缩容成本估算

```python
# 成本计算示例
class CostEstimator:
    # 每小时费用（美元）
    COMPUTE_COST_PER_HOUR = 0.5  # 单个实例
    STORAGE_COST_PER_GB = 0.023  # 存储
    DATA_TRANSFER_COST_PER_GB = 0.12  # 数据传输

    @staticmethod
    def estimate_monthly_cost(
        avg_instances: int,
        peak_instances: int,
        storage_gb: int,
        data_transfer_gb: int
    ) -> dict:
        # 计算实例成本（考虑峰值）
        avg_hours = 730  # 每月平均小时数
        compute_cost = (
            avg_instances * COMPUTE_COST_PER_HOUR * avg_hours * 0.7 +
            (peak_instances - avg_instances) * COMPUTE_COST_PER_HOUR * avg_hours * 0.3
        )

        storage_cost = storage_gb * STORAGE_COST_PER_GB
        transfer_cost = data_transfer_gb * DATA_TRANSFER_COST_PER_GB

        total = compute_cost + storage_cost + transfer_cost

        return {
            "compute": compute_cost,
            "storage": storage_cost,
            "data_transfer": transfer_cost,
            "total": total,
            "per_video": total / 10000  # 假设每月10K个视频
        }

# 成本优化建议
strategies = [
    "使用预留实例（Reserved Instances）- 可节省 30-40%",
    "使用Spot实例处理非关键任务 - 可节省 70%",
    "启用自动扩缩容 - 减少空闲资源",
    "使用CDN缓存减少出站流量",
    "压缩视频减少存储成本",
    "定期清理过期数据"
]
```

---

## 总结

本文档提供了Video-AI系统的完整扩展性设计方案，包括：

1. **水平和垂直扩展** - 支持无限扩展
2. **负载均衡** - 多种算法支持
3. **多层缓存** - 减少DB压力
4. **数据库扩展** - 读写分离、分片
5. **消息队列** - 异步任务处理
6. **全文搜索** - Elasticsearch集成
7. **成本优化** - 自动扩缩容

通过遵循这些原则，可以构建一个能够处理百万级用户的高可扩展系统。
