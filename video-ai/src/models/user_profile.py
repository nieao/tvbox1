"""
用户画像模型

完整的用户特征建模和兴趣学习系统
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set
from datetime import datetime, timedelta
import json
from pathlib import Path


@dataclass
class WatchEvent:
    """观看事件"""
    video_id: str
    category: str
    tags: List[str]
    watch_time: float  # 秒
    watch_percentage: float  # 0-1
    timestamp: str


@dataclass
class FeedbackEvent:
    """反馈事件"""
    video_id: str
    action: str  # like, dislike, skip, save, share
    timestamp: str


@dataclass
class UserInterest:
    """用户兴趣"""
    topic: str
    weight: float  # 0-1，兴趣强度
    confidence: float  # 0-1，置信度
    last_updated: str


class UserProfile:
    """用户画像"""

    def __init__(
        self,
        user_id: str,
        age_range: Optional[str] = None,
        location: Optional[str] = None,
        language: str = "zh-CN",
        device_type: str = "unknown"
    ):
        """
        初始化用户画像

        Args:
            user_id: 用户ID
            age_range: 年龄段 (e.g., "18-24", "25-34")
            location: 位置
            language: 语言
            device_type: 设备类型
        """
        self.user_id = user_id
        self.age_range = age_range
        self.location = location
        self.language = language
        self.device_type = device_type

        # 行为数据
        self.watch_history: List[WatchEvent] = []
        self.feedback_history: List[FeedbackEvent] = []

        # 兴趣维度
        self.interests: Dict[str, UserInterest] = {}
        self.category_interests: Dict[str, float] = {}

        # 偏好设置
        self.preferences = {
            "preferred_duration": "medium",  # short, medium, long
            "preferred_quality": "HD",
            "subtitle_enabled": True,
            "skip_topics": ["广告", "推广", "垃圾内容"]
        }

        # 计算指标
        self.engagement_score = 0.0
        self.loyalty_score = 0.0
        self.activity_level = "inactive"  # active, inactive, dormant
        self.last_active = None

        # 用户聚类
        self.cluster_id = None
        self.cluster_name = None

    def add_watch_event(
        self,
        video_id: str,
        category: str,
        tags: List[str],
        watch_time: float,
        watch_percentage: float
    ):
        """
        添加观看事件

        Args:
            video_id: 视频ID
            category: 视频分类
            tags: 视频标签
            watch_time: 观看时长（秒）
            watch_percentage: 观看比例（0-1）
        """
        event = WatchEvent(
            video_id=video_id,
            category=category,
            tags=tags,
            watch_time=watch_time,
            watch_percentage=watch_percentage,
            timestamp=datetime.now().isoformat()
        )

        self.watch_history.append(event)
        self.last_active = datetime.now()

        # 更新兴趣
        self._update_interests_from_watch(event)

        # 更新分类兴趣
        self._update_category_interests(category)

    def add_feedback_event(self, video_id: str, action: str):
        """
        添加反馈事件

        Args:
            video_id: 视频ID
            action: 动作类型（like, dislike, skip, save, share）
        """
        event = FeedbackEvent(
            video_id=video_id,
            action=action,
            timestamp=datetime.now().isoformat()
        )

        self.feedback_history.append(event)
        self.last_active = datetime.now()

        # 强化或削弱兴趣
        self._update_interests_from_feedback(video_id, action)

    def _update_interests_from_watch(self, event: WatchEvent):
        """根据观看事件更新用户兴趣"""
        # 权重计算：观看比例越高，权重越大
        weight = event.watch_percentage

        # 更新标签兴趣
        for tag in event.tags:
            if tag not in self.interests:
                self.interests[tag] = UserInterest(
                    topic=tag,
                    weight=0.0,
                    confidence=0.0,
                    last_updated=datetime.now().isoformat()
                )

            interest = self.interests[tag]

            # 更新权重（指数移动平均）
            alpha = 0.3  # 学习率
            interest.weight = (1 - alpha) * interest.weight + alpha * weight

            # 更新置信度（观看次数越多，置信度越高）
            tag_count = sum(1 for e in self.watch_history if tag in e.tags)
            interest.confidence = min(tag_count / 10, 1.0)

            interest.last_updated = datetime.now().isoformat()

    def _update_interests_from_feedback(self, video_id: str, action: str):
        """根据反馈事件更新用户兴趣"""
        # 找到对应的观看事件
        for event in reversed(self.watch_history):
            if event.video_id == video_id:
                # 强化或削弱因子
                factor = {
                    'like': 1.2,      # 加强兴趣
                    'dislike': 0.8,   # 减弱兴趣
                    'skip': 0.6,      # 显著减弱
                    'save': 1.3,      # 加强兴趣
                    'share': 1.4      # 强烈加强
                }.get(action, 1.0)

                # 调整标签兴趣
                for tag in event.tags:
                    if tag in self.interests:
                        self.interests[tag].weight *= factor
                        self.interests[tag].weight = min(self.interests[tag].weight, 1.0)

                break

    def _update_category_interests(self, category: str):
        """更新分类兴趣"""
        if category not in self.category_interests:
            self.category_interests[category] = 0.0

        # 简单权重更新
        alpha = 0.1
        self.category_interests[category] = (
            (1 - alpha) * self.category_interests[category] + alpha
        )

    def calculate_engagement_score(self) -> float:
        """
        计算参与度评分

        Returns:
            参与度评分 (0-1)
        """
        if not self.watch_history:
            return 0.0

        total_watch_time = sum(e.watch_time for e in self.watch_history)
        avg_watch_percentage = sum(e.watch_percentage for e in self.watch_history) / len(self.watch_history)

        feedback_count = len(self.feedback_history)
        total_events = len(self.watch_history) + feedback_count

        # 权重化计算
        watch_score = min(total_watch_time / (3600 * 10), 1.0)  # 10小时为满分
        completion_score = avg_watch_percentage
        feedback_score = min(feedback_count / len(self.watch_history) if self.watch_history else 0, 1.0)

        engagement = (watch_score * 0.4 + completion_score * 0.4 + feedback_score * 0.2)

        self.engagement_score = engagement
        return engagement

    def calculate_loyalty_score(self) -> float:
        """
        计算忠诚度评分

        Returns:
            忠诚度评分 (0-1)
        """
        if not self.watch_history:
            return 0.0

        # 忠诚度指标
        days_active = (datetime.now() - datetime.fromisoformat(self.watch_history[0].timestamp)).days + 1
        watch_frequency = len(self.watch_history) / max(days_active, 1)
        consistency = self._calculate_consistency()

        # 权重化计算
        frequency_score = min(watch_frequency / 2, 1.0)  # 平均每天2次为满分
        consistency_score = consistency
        recency_score = self._calculate_recency_score()

        loyalty = (frequency_score * 0.4 + consistency_score * 0.4 + recency_score * 0.2)

        self.loyalty_score = loyalty
        return loyalty

    def _calculate_consistency(self) -> float:
        """计算行为一致性"""
        if len(self.watch_history) < 2:
            return 0.5

        # 检查兴趣的稳定性
        interest_stability = 0.0
        for interest in self.interests.values():
            if interest.confidence > 0.5:
                interest_stability += 1

        stability_score = min(interest_stability / len(self.interests), 1.0) if self.interests else 0.5

        return stability_score

    def _calculate_recency_score(self) -> float:
        """计算近期活跃度"""
        if not self.last_active:
            return 0.0

        days_since_active = (datetime.now() - self.last_active).days

        # 指数衰减
        recency = max(1 - days_since_active / 30, 0)

        return recency

    def update_activity_level(self):
        """更新活跃度等级"""
        if not self.last_active:
            self.activity_level = "inactive"
            return

        days_since_active = (datetime.now() - self.last_active).days

        if days_since_active <= 7:
            self.activity_level = "active"
        elif days_since_active <= 30:
            self.activity_level = "inactive"
        else:
            self.activity_level = "dormant"

    def get_top_interests(self, k: int = 10) -> List[UserInterest]:
        """
        获取用户的top-k兴趣

        Args:
            k: 兴趣数量

        Returns:
            兴趣列表
        """
        sorted_interests = sorted(
            self.interests.values(),
            key=lambda x: x.weight * x.confidence,
            reverse=True
        )

        return sorted_interests[:k]

    def get_top_categories(self, k: int = 5) -> List[tuple]:
        """
        获取用户的top-k分类兴趣

        Args:
            k: 分类数量

        Returns:
            [(分类, 权重), ...]
        """
        sorted_categories = sorted(
            self.category_interests.items(),
            key=lambda x: x[1],
            reverse=True
        )

        return sorted_categories[:k]

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "user_id": self.user_id,
            "age_range": self.age_range,
            "location": self.location,
            "language": self.language,
            "device_type": self.device_type,
            "interests": {
                topic: {
                    "weight": interest.weight,
                    "confidence": interest.confidence,
                    "last_updated": interest.last_updated
                }
                for topic, interest in self.interests.items()
            },
            "category_interests": self.category_interests,
            "preferences": self.preferences,
            "engagement_score": self.engagement_score,
            "loyalty_score": self.loyalty_score,
            "activity_level": self.activity_level,
            "last_active": self.last_active.isoformat() if self.last_active else None,
            "cluster_id": self.cluster_id,
            "cluster_name": self.cluster_name
        }

    def save(self, filepath: str):
        """保存用户画像"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)

    @classmethod
    def load(cls, filepath: str) -> 'UserProfile':
        """加载用户画像"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        profile = cls(
            user_id=data['user_id'],
            age_range=data.get('age_range'),
            location=data.get('location'),
            language=data.get('language', 'zh-CN'),
            device_type=data.get('device_type', 'unknown')
        )

        # 恢复兴趣
        for topic, interest_data in data.get('interests', {}).items():
            profile.interests[topic] = UserInterest(
                topic=topic,
                weight=interest_data['weight'],
                confidence=interest_data['confidence'],
                last_updated=interest_data['last_updated']
            )

        # 恢复其他数据
        profile.category_interests = data.get('category_interests', {})
        profile.preferences = data.get('preferences', {})
        profile.engagement_score = data.get('engagement_score', 0.0)
        profile.loyalty_score = data.get('loyalty_score', 0.0)
        profile.activity_level = data.get('activity_level', 'inactive')
        profile.cluster_id = data.get('cluster_id')
        profile.cluster_name = data.get('cluster_name')

        return profile


if __name__ == "__main__":
    print("用户画像模型已加载")

    # 示例使用
    profile = UserProfile(user_id="user123", age_range="25-34", location="China", device_type="mobile")

    # 添加观看事件
    profile.add_watch_event("video1", "Technology", ["AI", "机器学习"], 600, 0.9)
    profile.add_watch_event("video2", "Technology", ["编程", "Python"], 400, 0.8)
    profile.add_watch_event("video3", "Education", ["教学", "在线教育"], 300, 0.7)

    # 添加反馈事件
    profile.add_feedback_event("video1", "like")
    profile.add_feedback_event("video2", "like")
    profile.add_feedback_event("video3", "save")

    # 计算指标
    profile.calculate_engagement_score()
    profile.calculate_loyalty_score()
    profile.update_activity_level()

    # 输出用户画像
    print(f"\n用户ID: {profile.user_id}")
    print(f"参与度评分: {profile.engagement_score:.3f}")
    print(f"忠诚度评分: {profile.loyalty_score:.3f}")
    print(f"活跃度: {profile.activity_level}")

    print("\nTop兴趣:")
    for interest in profile.get_top_interests(5):
        print(f"  {interest.topic}: 权重={interest.weight:.3f}, 置信度={interest.confidence:.3f}")

    print("\nTop分类:")
    for category, weight in profile.get_top_categories(3):
        print(f"  {category}: {weight:.3f}")
