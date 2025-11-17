"""
实时推荐引擎模块

基于用户实时行为进行在线学习和动态推荐。
"""

from typing import List, Dict, Optional, Set, Tuple
from dataclasses import dataclass, field
import time
from collections import deque, defaultdict, Counter
import numpy as np
import random
from datetime import datetime, timedelta


@dataclass
class UserBehavior:
    """用户行为"""
    user_id: str
    action: str  # view, skip, like, dislike, share
    video_id: str
    segment_id: Optional[str] = None
    duration: float = 0.0  # 观看时长
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'user_id': self.user_id,
            'action': self.action,
            'video_id': self.video_id,
            'segment_id': self.segment_id,
            'duration': self.duration,
            'timestamp': self.timestamp
        }


@dataclass
class RealtimeProfile:
    """实时用户画像"""
    user_id: str
    recent_behaviors: deque  # 最近行为队列
    current_interests: Dict[str, float]  # 当前兴趣权重
    trending_topics: List[str]  # 当前热门主题
    last_update: float = field(default_factory=time.time)
    session_start: float = field(default_factory=time.time)

    def get_active_time(self) -> float:
        """获取用户活跃时长（分钟）"""
        return (time.time() - self.session_start) / 60.0

    def get_behavior_count(self, action: str) -> int:
        """获取特定行为的数量"""
        return sum(1 for b in self.recent_behaviors if b.action == action)


class RealtimeRecommendationEngine:
    """实时推荐引擎"""

    def __init__(
        self,
        window_size: int = 100,  # 行为窗口大小
        update_interval: float = 60.0,  # 更新间隔（秒）
        decay_factor: float = 0.95,  # 兴趣衰减因子
        trending_window: int = 3600,  # 热门内容时间窗口（秒）
        min_interest_score: float = 0.05  # 最小兴趣分数
    ):
        """
        初始化实时推荐引擎

        Args:
            window_size: 保留最近N个行为
            update_interval: 兴趣更新间隔
            decay_factor: 时间衰减因子
            trending_window: 热门内容时间窗口
            min_interest_score: 最小兴趣分数阈值
        """
        self.window_size = window_size
        self.update_interval = update_interval
        self.decay_factor = decay_factor
        self.trending_window = trending_window
        self.min_interest_score = min_interest_score

        # 用户画像缓存
        self.profiles: Dict[str, RealtimeProfile] = {}

        # 行为队列（用于协同过滤）
        self.global_behaviors = deque(maxlen=10000)

        # 热门内容缓存
        self.trending_cache: Dict[str, float] = {}
        self.trending_last_update = time.time()

        # 视频元数据缓存
        self.video_metadata: Dict[str, Dict] = {}

        # 用户相似度缓存
        self.user_similarity_cache: Dict[Tuple[str, str], float] = {}
        self.similarity_cache_ttl = 300  # 5分钟
        self.similarity_cache_timestamp: Dict[Tuple[str, str], float] = {}

    def track_behavior(self, behavior: UserBehavior):
        """
        追踪用户行为

        Args:
            behavior: 用户行为对象
        """
        # 更新用户画像
        if behavior.user_id not in self.profiles:
            self.profiles[behavior.user_id] = RealtimeProfile(
                user_id=behavior.user_id,
                recent_behaviors=deque(maxlen=self.window_size),
                current_interests={},
                trending_topics=[]
            )

        profile = self.profiles[behavior.user_id]
        profile.recent_behaviors.append(behavior)

        # 更新全局行为队列
        self.global_behaviors.append(behavior)

        # 检查是否需要更新兴趣
        if time.time() - profile.last_update > self.update_interval:
            self._update_interests(profile)

        # 检查是否需要更新热门内容
        if time.time() - self.trending_last_update > self.trending_window / 10:
            self.update_trending()

    def add_video_metadata(self, video_id: str, metadata: Dict):
        """
        添加视频元数据

        Args:
            video_id: 视频ID
            metadata: 元数据字典，包含topics, tags, category等
        """
        self.video_metadata[video_id] = metadata

    def _extract_topics(self, video_id: str) -> List[str]:
        """
        从视频中提取主题/标签

        Args:
            video_id: 视频ID

        Returns:
            主题列表
        """
        if video_id not in self.video_metadata:
            # 如果没有元数据，返回默认主题
            return ["general"]

        metadata = self.video_metadata[video_id]
        topics = []

        # 从不同字段提取主题
        if 'topics' in metadata:
            topics.extend(metadata['topics'])
        if 'tags' in metadata:
            topics.extend(metadata['tags'])
        if 'category' in metadata:
            topics.append(metadata['category'])

        return topics if topics else ["general"]

    def _get_behavior_weight(self, behavior: UserBehavior) -> float:
        """
        根据行为类型获取权重

        Args:
            behavior: 用户行为

        Returns:
            权重值
        """
        weights = {
            'view': 1.0,
            'like': 3.0,
            'share': 5.0,
            'skip': -2.0,
            'dislike': -3.0,
            'comment': 2.5,
            'bookmark': 4.0
        }

        base_weight = weights.get(behavior.action, 1.0)

        # 根据观看时长调整权重（对于view行为）
        if behavior.action == 'view' and behavior.duration > 0:
            # 假设视频平均长度为10分钟，观看时长越长权重越高
            duration_factor = min(behavior.duration / 600, 1.5)
            base_weight *= duration_factor

        return base_weight

    def _update_interests(self, profile: RealtimeProfile):
        """
        更新用户兴趣

        Args:
            profile: 用户画像
        """
        # 从最近行为中提取兴趣
        interests: Dict[str, float] = {}

        current_time = time.time()

        for behavior in profile.recent_behaviors:
            # 根据行为类型赋予不同权重
            weight = self._get_behavior_weight(behavior)

            # 时间衰减：越旧的行为权重越低
            time_diff = current_time - behavior.timestamp
            time_decay = self.decay_factor ** (time_diff / 3600)  # 每小时衰减

            # 提取视频主题/标签
            topics = self._extract_topics(behavior.video_id)

            for topic in topics:
                interests[topic] = interests.get(topic, 0) + weight * time_decay

        # 过滤掉分数太低的兴趣
        interests = {k: v for k, v in interests.items() if v > self.min_interest_score}

        # 归一化
        total = sum(interests.values())
        if total > 0:
            interests = {k: v / total for k, v in interests.items()}

        profile.current_interests = interests
        profile.last_update = current_time

        # 更新热门主题（用户当前最感兴趣的主题）
        sorted_interests = sorted(interests.items(), key=lambda x: x[1], reverse=True)
        profile.trending_topics = [topic for topic, _ in sorted_interests[:5]]

    def get_recommendations(
        self,
        user_id: str,
        num_recommendations: int = 10,
        exclude_watched: bool = True
    ) -> List[Dict[str, any]]:
        """
        获取实时推荐

        Args:
            user_id: 用户ID
            num_recommendations: 推荐数量
            exclude_watched: 是否排除已观看的视频

        Returns:
            推荐结果列表，每个元素包含video_id, score, reason等
        """
        if user_id not in self.profiles:
            # 冷启动：返回热门内容
            return self._get_trending_videos(num_recommendations)

        profile = self.profiles[user_id]

        # 确保兴趣是最新的
        if time.time() - profile.last_update > self.update_interval:
            self._update_interests(profile)

        # 获取已观看的视频（用于过滤）
        watched_videos = set()
        if exclude_watched:
            watched_videos = {b.video_id for b in profile.recent_behaviors}

        # 1. 基于当前兴趣推荐 (50%)
        interest_based = self._recommend_by_interests(
            profile.current_interests,
            max(num_recommendations // 2, 5),
            watched_videos
        )

        # 2. 基于协同过滤推荐 (30%)
        collaborative = self._recommend_collaborative(
            user_id,
            max(num_recommendations // 3, 3),
            watched_videos
        )

        # 3. 探索性推荐（热门+多样性）(20%)
        exploratory = self._recommend_exploratory(
            max(num_recommendations // 5, 2),
            watched_videos
        )

        # 合并推荐结果
        all_recommendations = {}

        for rec in interest_based:
            all_recommendations[rec['video_id']] = rec

        for rec in collaborative:
            if rec['video_id'] in all_recommendations:
                # 合并分数
                all_recommendations[rec['video_id']]['score'] += rec['score'] * 0.5
                all_recommendations[rec['video_id']]['reason'] += f", {rec['reason']}"
            else:
                all_recommendations[rec['video_id']] = rec

        for rec in exploratory:
            if rec['video_id'] in all_recommendations:
                all_recommendations[rec['video_id']]['score'] += rec['score'] * 0.3
                all_recommendations[rec['video_id']]['reason'] += f", {rec['reason']}"
            else:
                all_recommendations[rec['video_id']] = rec

        # 排序并返回
        recommendations = sorted(
            all_recommendations.values(),
            key=lambda x: x['score'],
            reverse=True
        )

        return recommendations[:num_recommendations]

    def _recommend_by_interests(
        self,
        interests: Dict[str, float],
        num: int,
        exclude: Set[str]
    ) -> List[Dict]:
        """
        基于兴趣推荐

        Args:
            interests: 用户兴趣字典
            num: 推荐数量
            exclude: 要排除的视频ID集合

        Returns:
            推荐列表
        """
        recommendations = []

        # 遍历所有视频，计算匹配分数
        for video_id, metadata in self.video_metadata.items():
            if video_id in exclude:
                continue

            # 计算视频主题与用户兴趣的匹配度
            video_topics = self._extract_topics(video_id)
            match_score = 0.0

            for topic in video_topics:
                if topic in interests:
                    match_score += interests[topic]

            # 归一化
            if len(video_topics) > 0:
                match_score /= len(video_topics)

            if match_score > 0:
                recommendations.append({
                    'video_id': video_id,
                    'score': match_score,
                    'reason': '基于您的兴趣',
                    'method': 'interest_based'
                })

        # 排序并返回
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        return recommendations[:num]

    def _calculate_user_similarity(self, user_id1: str, user_id2: str) -> float:
        """
        计算两个用户的相似度

        Args:
            user_id1: 用户1 ID
            user_id2: 用户2 ID

        Returns:
            相似度分数 (0-1)
        """
        # 检查缓存
        cache_key = tuple(sorted([user_id1, user_id2]))
        if cache_key in self.user_similarity_cache:
            cache_time = self.similarity_cache_timestamp.get(cache_key, 0)
            if time.time() - cache_time < self.similarity_cache_ttl:
                return self.user_similarity_cache[cache_key]

        # 获取两个用户的画像
        if user_id1 not in self.profiles or user_id2 not in self.profiles:
            return 0.0

        profile1 = self.profiles[user_id1]
        profile2 = self.profiles[user_id2]

        # 基于兴趣的余弦相似度
        interests1 = profile1.current_interests
        interests2 = profile2.current_interests

        # 获取所有主题
        all_topics = set(interests1.keys()) | set(interests2.keys())

        if not all_topics:
            return 0.0

        # 构建向量
        vec1 = np.array([interests1.get(topic, 0) for topic in all_topics])
        vec2 = np.array([interests2.get(topic, 0) for topic in all_topics])

        # 计算余弦相似度
        dot_product = np.dot(vec1, vec2)
        magnitude1 = np.linalg.norm(vec1)
        magnitude2 = np.linalg.norm(vec2)

        if magnitude1 > 0 and magnitude2 > 0:
            similarity = dot_product / (magnitude1 * magnitude2)
        else:
            similarity = 0.0

        # 缓存结果
        self.user_similarity_cache[cache_key] = similarity
        self.similarity_cache_timestamp[cache_key] = time.time()

        return similarity

    def _recommend_collaborative(
        self,
        user_id: str,
        num: int,
        exclude: Set[str]
    ) -> List[Dict]:
        """
        协同过滤推荐

        Args:
            user_id: 用户ID
            num: 推荐数量
            exclude: 要排除的视频ID集合

        Returns:
            推荐列表
        """
        # 找到相似用户
        similar_users = []

        for other_user_id in self.profiles.keys():
            if other_user_id != user_id:
                similarity = self._calculate_user_similarity(user_id, other_user_id)
                if similarity > 0.1:  # 相似度阈值
                    similar_users.append((other_user_id, similarity))

        # 按相似度排序
        similar_users.sort(key=lambda x: x[1], reverse=True)

        # 统计相似用户喜欢的视频
        video_scores = defaultdict(float)

        for similar_user_id, similarity in similar_users[:10]:  # 考虑前10个相似用户
            similar_profile = self.profiles[similar_user_id]

            # 统计该用户的正向行为
            for behavior in similar_profile.recent_behaviors:
                if behavior.action in ['view', 'like', 'share', 'bookmark']:
                    if behavior.video_id not in exclude:
                        weight = self._get_behavior_weight(behavior)
                        video_scores[behavior.video_id] += similarity * weight

        # 转换为推荐列表
        recommendations = []
        for video_id, score in video_scores.items():
            recommendations.append({
                'video_id': video_id,
                'score': score,
                'reason': '相似用户也喜欢',
                'method': 'collaborative'
            })

        # 排序并返回
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        return recommendations[:num]

    def _recommend_exploratory(
        self,
        num: int,
        exclude: Set[str]
    ) -> List[Dict]:
        """
        探索性推荐（结合热门内容和多样性）

        Args:
            num: 推荐数量
            exclude: 要排除的视频ID集合

        Returns:
            推荐列表
        """
        recommendations = []

        # 从热门内容中选择
        trending_videos = [
            (video_id, score)
            for video_id, score in self.trending_cache.items()
            if video_id not in exclude
        ]

        # 添加一些随机视频以增加多样性
        all_videos = list(self.video_metadata.keys())
        random_videos = [
            v for v in random.sample(all_videos, min(len(all_videos), num * 2))
            if v not in exclude
        ]

        # 混合热门和随机
        for video_id, score in trending_videos[:num // 2]:
            recommendations.append({
                'video_id': video_id,
                'score': score * 0.8,  # 降低权重
                'reason': '热门内容',
                'method': 'trending'
            })

        for video_id in random_videos[:num // 2]:
            recommendations.append({
                'video_id': video_id,
                'score': 0.3,  # 固定较低分数
                'reason': '探索新内容',
                'method': 'exploration'
            })

        return recommendations[:num]

    def _get_trending_videos(self, num: int) -> List[Dict]:
        """
        获取热门视频（冷启动）

        Args:
            num: 推荐数量

        Returns:
            推荐列表
        """
        trending = sorted(
            self.trending_cache.items(),
            key=lambda x: x[1],
            reverse=True
        )

        recommendations = []
        for video_id, score in trending[:num]:
            recommendations.append({
                'video_id': video_id,
                'score': score,
                'reason': '热门推荐',
                'method': 'trending'
            })

        return recommendations

    def update_trending(self):
        """更新热门内容缓存"""
        current_time = time.time()
        cutoff_time = current_time - self.trending_window

        # 统计时间窗口内的行为
        video_engagement = defaultdict(lambda: {'views': 0, 'likes': 0, 'shares': 0})

        for behavior in self.global_behaviors:
            if behavior.timestamp >= cutoff_time:
                video_id = behavior.video_id

                if behavior.action == 'view':
                    video_engagement[video_id]['views'] += 1
                elif behavior.action == 'like':
                    video_engagement[video_id]['likes'] += 1
                elif behavior.action == 'share':
                    video_engagement[video_id]['shares'] += 1

        # 计算热度分数
        trending_scores = {}

        for video_id, engagement in video_engagement.items():
            views = engagement['views']
            likes = engagement['likes']
            shares = engagement['shares']

            # 热度公式：加权组合
            if views > 0:
                score = (
                    views * 1.0 +
                    likes * 3.0 +
                    shares * 5.0
                )
                # 归一化
                score = score / (views + 1)
                trending_scores[video_id] = score

        # 归一化所有分数到 0-1 范围
        if trending_scores:
            max_score = max(trending_scores.values())
            if max_score > 0:
                trending_scores = {
                    k: v / max_score
                    for k, v in trending_scores.items()
                }

        self.trending_cache = trending_scores
        self.trending_last_update = current_time

    def get_user_insights(self, user_id: str) -> Dict:
        """
        获取用户洞察

        Args:
            user_id: 用户ID

        Returns:
            用户洞察数据
        """
        if user_id not in self.profiles:
            return {
                'status': 'new_user',
                'message': '新用户，暂无数据'
            }

        profile = self.profiles[user_id]

        # 统计行为
        total_behaviors = len(profile.recent_behaviors)
        action_counts = Counter(b.action for b in profile.recent_behaviors)

        # 计算参与度
        engagement_score = (
            action_counts.get('view', 0) * 1 +
            action_counts.get('like', 0) * 3 +
            action_counts.get('share', 0) * 5
        ) / max(total_behaviors, 1)

        return {
            'status': 'active',
            'total_behaviors': total_behaviors,
            'action_counts': dict(action_counts),
            'top_interests': profile.trending_topics,
            'interest_scores': profile.current_interests,
            'engagement_score': engagement_score,
            'active_time_minutes': profile.get_active_time(),
            'last_update': datetime.fromtimestamp(profile.last_update).isoformat()
        }

    def get_statistics(self) -> Dict:
        """
        获取系统统计信息

        Returns:
            统计数据
        """
        return {
            'total_users': len(self.profiles),
            'total_behaviors': len(self.global_behaviors),
            'total_videos': len(self.video_metadata),
            'trending_videos_count': len(self.trending_cache),
            'active_users': sum(
                1 for p in self.profiles.values()
                if time.time() - p.last_update < 3600
            ),
            'cache_size': {
                'similarity_cache': len(self.user_similarity_cache),
                'trending_cache': len(self.trending_cache)
            }
        }


if __name__ == "__main__":
    print("实时推荐引擎模块已加载")

    # 示例用法
    engine = RealtimeRecommendationEngine()

    # 添加视频元数据
    engine.add_video_metadata("video1", {
        'topics': ['AI', '技术'],
        'category': '教育'
    })
    engine.add_video_metadata("video2", {
        'topics': ['编程', 'Python'],
        'category': '教育'
    })
    engine.add_video_metadata("video3", {
        'topics': ['游戏', '娱乐'],
        'category': '娱乐'
    })

    # 模拟用户行为
    behaviors = [
        UserBehavior("user1", "view", "video1", duration=300),
        UserBehavior("user1", "like", "video1"),
        UserBehavior("user1", "view", "video2", duration=200),
        UserBehavior("user2", "view", "video1", duration=400),
        UserBehavior("user2", "share", "video1"),
    ]

    for behavior in behaviors:
        engine.track_behavior(behavior)

    # 获取推荐
    print("\n用户1的推荐:")
    recommendations = engine.get_recommendations("user1", num_recommendations=5)
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec['video_id']} (分数: {rec['score']:.3f}) - {rec['reason']}")

    # 获取用户洞察
    print("\n用户1的洞察:")
    insights = engine.get_user_insights("user1")
    print(f"总行为数: {insights['total_behaviors']}")
    print(f"主要兴趣: {insights['top_interests']}")
    print(f"参与度评分: {insights['engagement_score']:.2f}")

    # 系统统计
    print("\n系统统计:")
    stats = engine.get_statistics()
    for key, value in stats.items():
        print(f"{key}: {value}")
