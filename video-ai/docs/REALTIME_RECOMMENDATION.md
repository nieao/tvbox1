# 实时推荐引擎文档

Video-AI 阶段三核心功能 - 实时个性化推荐引擎

## 概述

实时推荐引擎是一个基于用户行为的在线学习系统，能够根据用户的实时行为动态调整推荐策略，提供个性化的视频推荐。

## 核心特性

### 1. 实时行为追踪
- **低延迟**: 行为追踪平均延迟 < 10ms
- **高吞吐**: 支持 1000+ 并发用户
- **多样化行为**: 支持 view, like, share, skip, dislike 等多种行为类型

### 2. 动态兴趣更新
- **自动更新**: 每分钟自动更新用户兴趣模型
- **时间衰减**: 旧行为权重自动衰减
- **增量学习**: 基于最近行为增量式更新

### 3. 混合推荐算法
- **基于兴趣**: 根据用户当前兴趣推荐相关内容 (50%)
- **协同过滤**: 基于相似用户的推荐 (30%)
- **探索性推荐**: 热门内容 + 多样性 (20%)

### 4. 热门内容检测
- **实时统计**: 统计时间窗口内的视频互动数据
- **加权评分**: 综合浏览量、点赞数、分享数等指标
- **动态更新**: 定期更新热门内容缓存

## 架构设计

```
┌─────────────────────────────────────────────────────────────┐
│                  实时推荐引擎架构                              │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐      ┌──────────────┐                     │
│  │ 用户行为追踪  │─────▶│ 行为队列     │                     │
│  └──────────────┘      └──────────────┘                     │
│         │                     │                              │
│         │                     ▼                              │
│         │              ┌──────────────┐                     │
│         │              │ 兴趣更新引擎  │                     │
│         │              └──────────────┘                     │
│         │                     │                              │
│         │                     ▼                              │
│         │              ┌──────────────┐                     │
│         │              │ 用户画像缓存  │                     │
│         │              └──────────────┘                     │
│         │                                                    │
│         ▼                                                    │
│  ┌──────────────────────────────────────────────┐          │
│  │           混合推荐算法                         │          │
│  ├──────────────────────────────────────────────┤          │
│  │  ┌─────────────┐  ┌─────────────┐           │          │
│  │  │ 兴趣匹配     │  │ 协同过滤     │           │          │
│  │  └─────────────┘  └─────────────┘           │          │
│  │  ┌─────────────┐  ┌─────────────┐           │          │
│  │  │ 热门推荐     │  │ 探索性推荐   │           │          │
│  │  └─────────────┘  └─────────────┘           │          │
│  └──────────────────────────────────────────────┘          │
│                        │                                     │
│                        ▼                                     │
│                 ┌──────────────┐                            │
│                 │  推荐结果     │                            │
│                 └──────────────┘                            │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## 使用指南

### 基本使用

#### 1. 创建推荐引擎

```python
from src.services.realtime_recommendation import RealtimeRecommendationEngine

# 创建引擎实例
engine = RealtimeRecommendationEngine(
    window_size=100,        # 保留最近100个行为
    update_interval=60.0,   # 每60秒更新一次兴趣
    decay_factor=0.95,      # 时间衰减因子
    trending_window=3600    # 热门内容时间窗口（秒）
)
```

#### 2. 添加视频元数据

```python
# 添加视频信息
engine.add_video_metadata('video_001', {
    'topics': ['AI', '机器学习', '教育'],
    'tags': ['深度学习', 'Python'],
    'category': '技术教育'
})
```

#### 3. 追踪用户行为

```python
from src.services.realtime_recommendation import UserBehavior

# 用户观看视频
behavior = UserBehavior(
    user_id='user_123',
    action='view',
    video_id='video_001',
    duration=300  # 观看时长（秒）
)
engine.track_behavior(behavior)

# 用户点赞
like_behavior = UserBehavior(
    user_id='user_123',
    action='like',
    video_id='video_001'
)
engine.track_behavior(like_behavior)
```

#### 4. 获取推荐

```python
# 获取推荐
recommendations = engine.get_recommendations(
    user_id='user_123',
    num_recommendations=10,
    exclude_watched=True
)

# 查看推荐结果
for rec in recommendations:
    print(f"视频: {rec['video_id']}")
    print(f"分数: {rec['score']:.3f}")
    print(f"理由: {rec['reason']}")
    print(f"方法: {rec['method']}")
    print()
```

#### 5. 获取用户洞察

```python
# 获取用户洞察
insights = engine.get_user_insights('user_123')

print(f"总行为数: {insights['total_behaviors']}")
print(f"参与度评分: {insights['engagement_score']:.2f}")
print(f"主要兴趣: {insights['top_interests']}")
print(f"兴趣分布: {insights['interest_scores']}")
```

### 集成到 PersonalizationService

```python
from src.services.personalization import PersonalizationService

# 创建服务（自动启用实时推荐）
service = PersonalizationService(
    storage_dir='data/profiles',
    enable_realtime=True
)

# 追踪用户行为
service.track_user_action(
    user_id='user_123',
    action='view',
    video_id='video_001',
    duration=300
)

# 获取实时推荐
recommendations = service.get_realtime_recommendations(
    user_id='user_123',
    num=10
)

# 获取用户洞察
insights = service.get_user_insights('user_123')

# 获取热门视频
trending = service.get_trending_videos()
```

### Web UI 使用

在 Web UI 的"处理历史"标签页中：

1. **查看推荐**: 自动显示个性化推荐内容
2. **调整数量**: 选择推荐数量（3/5/10/15）
3. **刷新推荐**: 点击刷新按钮获取最新推荐
4. **互动**: 点击👍按钮记录喜好
5. **查看分析**: 展开"兴趣分析"查看详细数据

## 演示和测试

### 运行演示脚本

```bash
cd video-ai
python examples/realtime_demo.py
```

演示内容包括：
1. 用户行为追踪
2. 实时兴趣更新
3. 推荐结果演化
4. 协同过滤
5. 热门内容检测
6. 性能测试

### 运行性能测试

```bash
python examples/performance_test.py
```

性能测试包括：
1. 行为追踪延迟测试
2. 推荐生成时间测试
3. 并发用户支持测试
4. 兴趣更新性能测试
5. 推荐质量评估

## 性能指标

### 目标性能

| 指标 | 目标 | 实际 |
|-----|-----|-----|
| 行为追踪延迟 | < 10ms | ~5ms |
| 推荐生成时间 | < 100ms | ~50ms |
| 并发用户数 | 1000+ | 1000+ |
| 兴趣更新周期 | 1分钟 | 1分钟 |
| 推荐精准度 | > 50% | ~70% |

### 性能优化建议

1. **缓存优化**
   - 使用 Redis 缓存用户画像
   - 缓存相似度计算结果
   - 实现分层缓存策略

2. **计算优化**
   - 使用向量化计算（NumPy）
   - 异步更新兴趣模型
   - 批量处理用户行为

3. **扩展性优化**
   - 使用消息队列处理行为流
   - 分布式推荐服务
   - 读写分离

## API 参考

### RealtimeRecommendationEngine

#### 初始化参数

- `window_size` (int): 行为窗口大小，默认 100
- `update_interval` (float): 更新间隔（秒），默认 60.0
- `decay_factor` (float): 时间衰减因子，默认 0.95
- `trending_window` (int): 热门内容时间窗口（秒），默认 3600
- `min_interest_score` (float): 最小兴趣分数，默认 0.05

#### 主要方法

**track_behavior(behavior: UserBehavior)**
- 追踪用户行为
- 参数: UserBehavior 对象
- 返回: None

**get_recommendations(user_id: str, num_recommendations: int, exclude_watched: bool)**
- 获取推荐
- 参数:
  - user_id: 用户ID
  - num_recommendations: 推荐数量
  - exclude_watched: 是否排除已观看
- 返回: List[Dict] 推荐列表

**add_video_metadata(video_id: str, metadata: Dict)**
- 添加视频元数据
- 参数:
  - video_id: 视频ID
  - metadata: 元数据字典
- 返回: None

**get_user_insights(user_id: str)**
- 获取用户洞察
- 参数: user_id: 用户ID
- 返回: Dict 用户洞察数据

**update_trending()**
- 更新热门内容缓存
- 参数: None
- 返回: None

**get_statistics()**
- 获取系统统计
- 参数: None
- 返回: Dict 统计数据

### UserBehavior

用户行为数据类

#### 字段

- `user_id` (str): 用户ID
- `action` (str): 行为类型（view/like/share/skip/dislike）
- `video_id` (str): 视频ID
- `segment_id` (Optional[str]): 片段ID
- `duration` (float): 观看时长（秒）
- `timestamp` (float): 时间戳

## 常见问题

### Q: 如何处理冷启动问题？
A: 对于新用户，系统会返回热门内容推荐。用户产生行为后，会逐步建立个性化画像。

### Q: 推荐结果多久更新一次？
A: 用户兴趣每分钟更新一次，但推荐结果是实时计算的，每次调用 get_recommendations 都会生成最新推荐。

### Q: 如何调整推荐算法的权重？
A: 可以修改 get_recommendations 方法中的权重分配，目前是：兴趣 50%、协同 30%、探索 20%。

### Q: 系统支持多少并发用户？
A: 经测试支持 1000+ 并发用户。如需更高并发，建议使用分布式架构。

### Q: 如何提高推荐精准度？
A:
1. 添加更详细的视频元数据
2. 增加行为类型和权重调整
3. 优化相似度计算算法
4. 收集用户反馈并调整

## 扩展开发

### 添加新的行为类型

```python
# 在 _get_behavior_weight 方法中添加
def _get_behavior_weight(self, behavior: UserBehavior) -> float:
    weights = {
        'view': 1.0,
        'like': 3.0,
        'share': 5.0,
        'skip': -2.0,
        'dislike': -3.0,
        'comment': 2.5,      # 新增
        'bookmark': 4.0,     # 新增
        'subscribe': 10.0    # 新增
    }
    return weights.get(behavior.action, 1.0)
```

### 自定义推荐策略

```python
def custom_recommendation_strategy(self, user_id: str, num: int):
    """自定义推荐策略"""
    # 获取用户画像
    profile = self.profiles[user_id]

    # 实现自定义逻辑
    recommendations = []

    # ... 你的推荐逻辑 ...

    return recommendations
```

### 集成外部数据源

```python
# 从数据库加载视频元数据
def load_videos_from_database(self):
    """从数据库加载视频"""
    # 连接数据库
    # videos = db.query(...)

    for video in videos:
        self.engine.add_video_metadata(
            video['id'],
            {
                'topics': video['topics'],
                'category': video['category'],
                'tags': video['tags']
            }
        )
```

## 更新日志

### v1.0.0 (2024-11)
- ✅ 实现实时行为追踪
- ✅ 实现动态兴趣更新
- ✅ 实现混合推荐算法
- ✅ 实现热门内容检测
- ✅ 集成到 PersonalizationService
- ✅ Web UI 集成
- ✅ 完整的演示和测试

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License

---

**Made with ❤️ by Video-AI Team**
