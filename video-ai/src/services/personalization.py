"""
个性化服务模块

管理用户配置、偏好和个性化推荐。
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict
import json
from pathlib import Path


@dataclass
class PersonalizationConfig:
    """个性化配置"""

    # 用户兴趣
    interests: List[str] = field(default_factory=list)

    # 要跳过的主题
    skip_topics: List[str] = field(default_factory=lambda: ["广告", "推广"])

    # 播放速度偏好
    pace: str = "normal"  # slow, normal, fast

    # 过渡风格
    transition_style: str = "text"  # text, simple, ai_generated

    # 语言
    language: str = "zh-CN"

    # 输出长度
    output_length: str = "medium"  # short (30%), medium (50%), long (70%)

    def __post_init__(self):
        """验证配置"""
        valid_paces = ["slow", "normal", "fast"]
        if self.pace not in valid_paces:
            raise ValueError(f"pace 必须是 {valid_paces} 之一")

        valid_transitions = ["text", "simple", "ai_generated"]
        if self.transition_style not in valid_transitions:
            raise ValueError(f"transition_style 必须是 {valid_transitions} 之一")

        valid_lengths = ["short", "medium", "long"]
        if self.output_length not in valid_lengths:
            raise ValueError(f"output_length 必须是 {valid_lengths} 之一")

    def get_target_compression(self) -> float:
        """获取目标压缩率"""
        compression_map = {
            "short": 0.70,   # 保留30%
            "medium": 0.50,  # 保留50%
            "long": 0.30     # 保留70%
        }
        return compression_map[self.output_length]

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'interests': self.interests,
            'skip_topics': self.skip_topics,
            'pace': self.pace,
            'transition_style': self.transition_style,
            'language': self.language,
            'output_length': self.output_length
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'PersonalizationConfig':
        """从字典创建"""
        return cls(**data)

    def save(self, filepath: str):
        """保存配置到文件"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)

    @classmethod
    def load(cls, filepath: str) -> 'PersonalizationConfig':
        """从文件加载配置"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls.from_dict(data)


@dataclass
class UserProfile:
    """用户画像"""

    user_id: str
    config: PersonalizationConfig
    watch_history: List[Dict] = field(default_factory=list)
    feedback_history: List[Dict] = field(default_factory=list)

    def add_watch_history(self, video_id: str, segments_watched: List[int], rating: Optional[float] = None):
        """添加观看历史"""
        self.watch_history.append({
            'video_id': video_id,
            'segments_watched': segments_watched,
            'rating': rating,
            'timestamp': self._get_timestamp()
        })

    def add_feedback(self, video_id: str, feedback_type: str, details: Optional[Dict] = None):
        """添加用户反馈"""
        self.feedback_history.append({
            'video_id': video_id,
            'type': feedback_type,  # like, dislike, skip, save
            'details': details or {},
            'timestamp': self._get_timestamp()
        })

    def update_interests_from_feedback(self):
        """根据反馈更新兴趣（简化实现）"""
        # TODO: 实现基于反馈的兴趣学习算法
        pass

    def get_engagement_score(self) -> float:
        """计算用户参与度评分"""
        if not self.watch_history:
            return 0.0

        total_videos = len(self.watch_history)
        total_segments = sum(len(h['segments_watched']) for h in self.watch_history)

        return min(total_segments / (total_videos * 10), 1.0)  # 假设平均10个片段

    @staticmethod
    def _get_timestamp():
        """获取当前时间戳"""
        from datetime import datetime
        return datetime.now().isoformat()

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'user_id': self.user_id,
            'config': self.config.to_dict(),
            'watch_history': self.watch_history,
            'feedback_history': self.feedback_history
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'UserProfile':
        """从字典创建"""
        return cls(
            user_id=data['user_id'],
            config=PersonalizationConfig.from_dict(data['config']),
            watch_history=data.get('watch_history', []),
            feedback_history=data.get('feedback_history', [])
        )

    def save(self, filepath: str):
        """保存用户画像到文件"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)

    @classmethod
    def load(cls, filepath: str) -> 'UserProfile':
        """从文件加载用户画像"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls.from_dict(data)


class PersonalizationService:
    """个性化服务"""

    def __init__(self, storage_dir: str = "data/profiles", enable_realtime: bool = True):
        """
        初始化个性化服务

        Args:
            storage_dir: 用户画像存储目录
            enable_realtime: 是否启用实时推荐引擎
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        # 实时推荐引擎
        self.enable_realtime = enable_realtime
        if enable_realtime:
            try:
                from .realtime_recommendation import RealtimeRecommendationEngine, UserBehavior
                self.realtime_engine = RealtimeRecommendationEngine()
                self.UserBehavior = UserBehavior
            except ImportError as e:
                print(f"警告: 无法加载实时推荐引擎: {e}")
                self.enable_realtime = False
                self.realtime_engine = None

    def create_profile(
        self,
        user_id: str,
        config: Optional[PersonalizationConfig] = None
    ) -> UserProfile:
        """
        创建用户画像

        Args:
            user_id: 用户ID
            config: 个性化配置

        Returns:
            UserProfile对象
        """
        if config is None:
            config = PersonalizationConfig()

        profile = UserProfile(user_id=user_id, config=config)
        self.save_profile(profile)

        return profile

    def get_profile(self, user_id: str) -> Optional[UserProfile]:
        """获取用户画像"""
        filepath = self.storage_dir / f"{user_id}.json"

        if not filepath.exists():
            return None

        return UserProfile.load(str(filepath))

    def save_profile(self, profile: UserProfile):
        """保存用户画像"""
        filepath = self.storage_dir / f"{profile.user_id}.json"
        profile.save(str(filepath))

    def update_profile(
        self,
        user_id: str,
        **updates
    ) -> UserProfile:
        """
        更新用户画像

        Args:
            user_id: 用户ID
            **updates: 要更新的字段

        Returns:
            更新后的UserProfile
        """
        profile = self.get_profile(user_id)

        if profile is None:
            raise ValueError(f"用户 {user_id} 不存在")

        # 更新配置
        if 'interests' in updates:
            profile.config.interests = updates['interests']
        if 'skip_topics' in updates:
            profile.config.skip_topics = updates['skip_topics']
        if 'pace' in updates:
            profile.config.pace = updates['pace']
        if 'transition_style' in updates:
            profile.config.transition_style = updates['transition_style']
        if 'output_length' in updates:
            profile.config.output_length = updates['output_length']

        self.save_profile(profile)
        return profile

    def recommend_config(self, user_id: str) -> PersonalizationConfig:
        """
        根据用户历史推荐配置（阶段三功能）

        Args:
            user_id: 用户ID

        Returns:
            推荐的PersonalizationConfig
        """
        profile = self.get_profile(user_id)

        if profile is None or not profile.watch_history:
            # 返回默认配置
            return PersonalizationConfig()

        # TODO: 实现基于历史的智能推荐算法
        # 这里简化实现：返回用户当前配置
        return profile.config

    # ========== 实时推荐功能 ==========

    def track_user_action(
        self,
        user_id: str,
        action: str,
        video_id: str,
        segment_id: Optional[str] = None,
        duration: float = 0.0
    ):
        """
        追踪用户行为

        Args:
            user_id: 用户ID
            action: 行为类型 (view, skip, like, dislike, share等)
            video_id: 视频ID
            segment_id: 片段ID（可选）
            duration: 观看时长（秒）
        """
        if not self.enable_realtime:
            return

        behavior = self.UserBehavior(
            user_id=user_id,
            action=action,
            video_id=video_id,
            segment_id=segment_id,
            duration=duration
        )
        self.realtime_engine.track_behavior(behavior)

        # 同时更新用户画像的历史记录
        profile = self.get_profile(user_id)
        if profile:
            if action in ['view', 'like', 'share']:
                # 添加反馈
                profile.add_feedback(video_id, action, {
                    'duration': duration,
                    'segment_id': segment_id
                })
                self.save_profile(profile)

    def add_video_metadata(self, video_id: str, metadata: Dict):
        """
        添加视频元数据到实时推荐引擎

        Args:
            video_id: 视频ID
            metadata: 元数据字典
        """
        if not self.enable_realtime:
            return

        self.realtime_engine.add_video_metadata(video_id, metadata)

    def get_realtime_recommendations(
        self,
        user_id: str,
        num: int = 10,
        exclude_watched: bool = True
    ) -> List[Dict]:
        """
        获取实时推荐

        Args:
            user_id: 用户ID
            num: 推荐数量
            exclude_watched: 是否排除已观看的视频

        Returns:
            推荐列表
        """
        if not self.enable_realtime:
            return []

        return self.realtime_engine.get_recommendations(
            user_id,
            num_recommendations=num,
            exclude_watched=exclude_watched
        )

    def get_user_insights(self, user_id: str) -> Dict:
        """
        获取用户洞察数据

        Args:
            user_id: 用户ID

        Returns:
            用户洞察字典
        """
        if not self.enable_realtime:
            return {'status': 'disabled', 'message': '实时推荐未启用'}

        return self.realtime_engine.get_user_insights(user_id)

    def get_trending_videos(self) -> Dict[str, float]:
        """
        获取当前热门视频

        Returns:
            视频ID到热度分数的映射
        """
        if not self.enable_realtime:
            return {}

        return self.realtime_engine.trending_cache

    def get_recommendation_stats(self) -> Dict:
        """
        获取推荐系统统计信息

        Returns:
            统计数据字典
        """
        if not self.enable_realtime:
            return {'status': 'disabled'}

        return self.realtime_engine.get_statistics()


if __name__ == "__main__":
    # 测试代码
    print("PersonalizationService 模块已加载")

    # 示例用法
    # service = PersonalizationService()
    # config = PersonalizationConfig(
    #     interests=["AI", "编程"],
    #     output_length="short"
    # )
    # profile = service.create_profile("user123", config)
    # print(f"用户画像已创建: {profile.user_id}")
