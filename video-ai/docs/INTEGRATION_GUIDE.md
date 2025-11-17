# Video-AI 推荐系统集成指南

## 概述

本指南说明如何将推荐系统集成到video-ai项目中，实现完整的个性化视频编辑和推荐功能。

## 架构集成

### 现有架构
```
VideoEditor（主入口）
├── VideoTranscriber（转录）
├── ContentAnalyzer（分析）
└── VideoEditor（剪辑）
```

### 集成后的架构
```
PersonalizationService（个性化服务）
├── UserProfile（用户画像）
├── RecommendationEngine（推荐引擎）
│   ├── CollaborativeFiltering（协同过滤）
│   ├── ContentBasedRecommender（内容推荐）
│   └── HybridRecommender（混合推荐）
├── NLPProcessor（NLP处理）
│   ├── TextPreprocessor
│   ├── KeywordExtractor
│   ├── TopicExtractor
│   └── SentimentAnalyzer
└── VideoFeatureManager（视频特征管理）
```

## 集成步骤

### 步骤1: 安装依赖

```bash
# 新增推荐系统依赖
pip install jieba  # 中文分词
pip install scikit-learn>=1.3.0  # 协同过滤
```

### 步骤2: 更新PersonalizationService

修改 `/home/user/tvbox1/video-ai/src/services/personalization.py`：

```python
from src.services.recommendation import HybridRecommender, RecommendationItem
from src.models.user_profile import UserProfile
from src.utils.nlp_processor import KeywordExtractor, TopicExtractor, SentimentAnalyzer

class PersonalizationService:
    """增强的个性化服务"""

    def __init__(self, storage_dir: str = "data/profiles"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # 新增推荐系统
        self.recommender = HybridRecommender()
        self.user_profiles = {}  # 缓存用户画像

    def create_profile(self, user_id: str, config: Optional[PersonalizationConfig] = None) -> UserProfile:
        """创建用户画像"""
        profile = UserProfile(
            user_id=user_id,
            language=config.language if config else "zh-CN"
        )
        self.user_profiles[user_id] = profile
        return profile

    def recommend_videos(self, user_id: str, k: int = 10) -> List[RecommendationItem]:
        """获取推荐视频"""
        if user_id not in self.user_profiles:
            return []
        
        return self.recommender.recommend(user_id, k=k)

    def extract_video_features(self, transcript: str) -> Dict[str, float]:
        """提取视频特征"""
        # 使用NLP处理获取关键词和主题
        keywords = KeywordExtractor.textrank(transcript, top_n=10)
        topics = TopicExtractor.identify_topics(transcript, num_topics=5)
        
        # 合并成特征字典
        features = {}
        features.update(keywords)
        for topic, weight in topics:
            features[topic] = weight
        
        return features
```

### 步骤3: 更新VideoEditor集成推荐

```python
from src.services.personalization import PersonalizationService

class VideoEditor:
    """增强的视频编辑器"""

    def __init__(self, config: Optional[PersonalizationConfig] = None):
        # ... 现有代码 ...
        
        # 初始化个性化服务
        self.personalization_service = PersonalizationService()

    def recommend_related_videos(self, user_id: str, video_id: str, k: int = 5) -> List[Dict]:
        """获取相关视频推荐"""
        recommendations = self.personalization_service.recommend_videos(user_id, k=k)
        
        return [
            {
                'video_id': rec.video_id,
                'score': rec.score,
                'reason': rec.reason
            }
            for rec in recommendations
        ]

    def process_video_with_recommendations(self, input_path: str, output_path: str, user_id: str):
        """处理视频并生成推荐"""
        # 步骤1: 转录和分析
        transcript = self.transcriber.transcribe(input_path)
        analysis = self.analyzer.analyze(transcript, user_interests=self.config.interests)
        
        # 步骤2: 提取视频特征
        video_features = self.personalization_service.extract_video_features(transcript.full_text)
        
        # 步骤3: 更新用户画像
        profile = self.personalization_service.create_profile(user_id, self.config)
        profile.add_watch_event(
            video_id="current_video",
            category=analysis.main_topics[0] if analysis.main_topics else "General",
            tags=analysis.keywords[:10],
            watch_time=analysis.key_segments[-1].end if analysis.key_segments else 0,
            watch_percentage=0.8
        )
        
        # 步骤4: 编辑视频
        result = self._edit_video(input_path, output_path, analysis, transcript)
        
        # 步骤5: 获取推荐
        recommendations = self.recommend_related_videos(user_id, "current_video", k=10)
        
        return {
            'edit_result': result,
            'recommendations': recommendations
        }
```

## 数据模型设计

### 用户画像数据模型

```json
{
  "user_id": "user_123",
  "basic_info": {
    "age_range": "25-34",
    "location": "Beijing",
    "language": "zh-CN",
    "device_type": "mobile",
    "registration_date": "2024-01-01T00:00:00Z"
  },
  "interests": {
    "Technology": {
      "weight": 0.85,
      "confidence": 0.9,
      "sub_topics": ["AI", "编程", "数据科学"]
    },
    "Education": {
      "weight": 0.75,
      "confidence": 0.8,
      "sub_topics": ["在线教育", "教学", "学习"]
    }
  },
  "behavior": {
    "total_watch_time": 36000,  # 秒
    "total_videos_watched": 150,
    "average_completion_rate": 0.82,
    "total_interactions": 45,
    "last_active": "2024-01-15T10:00:00Z"
  },
  "engagement_metrics": {
    "engagement_score": 0.78,
    "loyalty_score": 0.65,
    "activity_level": "active",
    "churn_risk": 0.1
  },
  "preferences": {
    "video_duration": "medium",
    "quality": "HD",
    "subtitle_enabled": true,
    "skip_topics": ["广告", "推广"],
    "recommendation_diversity": 0.7
  },
  "watch_history": [
    {
      "video_id": "vid_123",
      "timestamp": "2024-01-15T10:00:00Z",
      "watch_time": 600,
      "completion_rate": 0.9,
      "engagement": "like"
    }
  ],
  "feedback_history": [
    {
      "video_id": "vid_123",
      "action": "like",
      "timestamp": "2024-01-15T10:05:00Z"
    }
  ]
}
```

### 推荐项目数据模型

```json
{
  "recommendation": {
    "video_id": "vid_456",
    "title": "深度学习基础",
    "score": 0.87,
    "ranking": 1,
    "reasons": [
      "基于相似用户的推荐",
      "与你的兴趣匹配",
      "近期热门内容"
    ],
    "component_scores": {
      "collaborative_filtering": 0.85,
      "content_based": 0.80,
      "popularity": 0.92,
      "freshness": 0.78
    },
    "metadata": {
      "category": "Technology",
      "tags": ["AI", "深度学习", "教育"],
      "duration": "1200秒",
      "views": 50000,
      "likes": 2500,
      "published_at": "2024-01-10T00:00:00Z"
    }
  }
}
```

## 推荐算法参数配置

### 协同过滤参数

```python
# src/services/recommendation.py
class CollaborativeFiltering:
    PARAMS = {
        'similarity_threshold': 0.1,      # 相似度阈值
        'n_similar_users': 10,            # 相似用户数量
        'min_common_items': 3,            # 最少共同交互项目数
        'decay_factor': 0.9               # 时间衰减因子
    }
```

### 混合推荐权重

```python
class HybridRecommender:
    WEIGHTS = {
        'collaborative_filtering': 0.40,  # 协同过滤权重
        'content_based': 0.35,            # 内容推荐权重
        'popularity': 0.15,               # 热度权重
        'diversity': 0.10                 # 多样性权重
    }
```

## 性能优化策略

### 1. 缓存机制

```python
# 推荐结果缓存（1小时过期）
recommendation_cache = {
    'user_id': {
        'timestamp': datetime.now(),
        'recommendations': [...]
    }
}

# 用户画像缓存（实时更新）
profile_cache = {
    'user_id': UserProfile(...)
}

# 视频特征缓存（7天过期）
video_feature_cache = {
    'video_id': {
        'features': {...},
        'timestamp': datetime.now()
    }
}
```

### 2. 向量索引（ANN）

```python
# 使用Faiss加速最近邻搜索
from faiss import IndexFlatL2

# 构建用户向量索引
user_vectors = np.array([profile.get_interest_vector() for profile in profiles])
index = IndexFlatL2(d=128)
index.add(user_vectors)

# 快速查找K个最相似用户
D, I = index.search(np.array([query_vector]), k=10)
```

### 3. 批处理和异步处理

```python
# 异步更新用户画像
import asyncio

async def update_profile_async(user_id, event):
    profile = await get_profile_from_db(user_id)
    profile.add_event(event)
    await save_profile_to_db(profile)

# 批量计算推荐
from concurrent.futures import ThreadPoolExecutor

def batch_recommend(user_ids, k=10):
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {
            executor.submit(recommender.recommend, uid, k): uid
            for uid in user_ids
        }
        results = {}
        for future in futures:
            results[futures[future]] = future.result()
    return results
```

## 评估指标

### 推荐准确性指标

```python
# Precision@K: 推荐列表中相关项目数 / K
precision_at_10 = relevant_items_in_top_10 / 10

# Recall@K: 推荐列表中相关项目数 / 用户交互总数
recall_at_10 = relevant_items_in_top_10 / total_interactions

# NDCG@K: 加权平均排名
def ndcg_at_k(predictions, targets, k=10):
    dcg = sum((2**rel - 1) / math.log2(i + 2) for i, rel in enumerate(predictions[:k]))
    ideal_dcg = sum((2**rel - 1) / math.log2(i + 2) for i, rel in enumerate(sorted(targets, reverse=True)[:k]))
    return dcg / ideal_dcg if ideal_dcg > 0 else 0
```

### 用户体验指标

```python
# CTR: 点击率
ctr = recommendations_clicked / recommendations_shown

# 平均观看时长
avg_watch_time = sum(watch_times) / len(watch_times)

# 完成率
completion_rate = videos_completed / videos_started
```

### 多样性指标

```python
# Coverage: 推荐过的不同项目数 / 库存总数
coverage = len(unique_recommended_items) / total_items

# Novelty: 用户未知项目比例
novelty = novel_items / total_recommendations
```

## 故障排除

### 常见问题

1. **冷启动问题**
   - 新用户：使用基于内容的推荐
   - 新视频：使用上传者历史视频的观看者
   - 解决方案：参考用户画像建模章节的冷启动策略

2. **信息茧房**
   - 问题：推荐过于同质化
   - 解决方案：引入探索(Exploration)策略
   ```python
   # 探索系数
   explore_rate = 0.1  # 10%推荐为探索内容
   ```

3. **稀疏数据**
   - 问题：用户-项目矩阵稀疏
   - 解决方案：使用混合推荐，结合内容特征

4. **实时性要求**
   - 问题：推荐延迟高
   - 解决方案：使用预计算 + 缓存 + 在线排序

## 后续开发路线

### 阶段1（当前）
- 基于内容的推荐
- 用户画像基础建模
- 简单的协同过滤

### 阶段2
- 深度学习排序模型
- 基于图神经网络的推荐
- 多目标优化

### 阶段3
- 实时推荐服务（<100ms）
- 在线学习框架
- A/B测试平台

### 阶段4
- 跨平台推荐集成
- 因果推理推荐
- 联邦学习隐私保护

## 参考资源

- YouTube推荐系统论文: https://arxiv.org/pdf/1606.07792.pdf
- Surprise推荐库: https://surprise.readthedocs.io/
- 推荐系统实战: https://github.com/NiuTrans/InterpretableML

