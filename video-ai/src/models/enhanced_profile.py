"""
增强用户画像系统 (Enhanced User Profile System)

扩展用户画像从7维到15+维度，提升个性化推荐精准度

维度列表：
1. 观看习惯 - 时间、频率、时长
2. 内容偏好 - 兴趣标签、主题
3. 交互行为 - 点赞、分享、评论
4. 设备信息 - 平台、设备类型、多样性
5. 时间模式 - 高峰时段、周末/工作日活动
6. 社交属性 - 分享行为、影响力
7. 学习曲线 - 进步轨迹、知识水平
8. 注意力模式 - 专注度、跳过率、重看率
9. 内容深度 - 深度/浅层内容偏好
10. 多样性需求 - 探索/利用平衡
11. 反馈质量 - 反馈详细度、准确性
12. 付费意愿 - 潜在价值评估
13. 流失风险 - 留存预测
14. 影响因子 - 对他人的影响力
15. 生命周期阶段 - 新用户/成熟用户/流失用户
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Set
from datetime import datetime, time
from enum import Enum
import json
import math
from collections import defaultdict
from pathlib import Path


class LifecycleStage(Enum):
    """用户生命周期阶段"""
    NEW = "new"  # 新用户 (0-7天)
    GROWING = "growing"  # 成长阶段 (7-30天)
    MATURE = "mature"  # 成熟用户 (30+天，活跃)
    AT_RISK = "at_risk"  # 高风险流失
    CHURNED = "churned"  # 已流失


class ContentDepthPreference(Enum):
    """内容深度偏好"""
    SHALLOW = 0.0  # 浅层内容
    LIGHT = 0.33
    MODERATE = 0.67
    DEEP = 1.0  # 深度内容


@dataclass
class DeviceInfo:
    """设备信息"""
    device_type: str  # mobile, desktop, tablet
    platform: str  # web, ios, android
    os_version: str = "unknown"
    app_version: str = "unknown"


@dataclass
class TimePattern:
    """时间模式"""
    hour: int  # 0-23
    day_of_week: int  # 0-6 (Monday-Sunday)
    active: bool = True
    session_count: int = 0


@dataclass
class ContentPreference:
    """内容偏好"""
    category: str
    weight: float  # 0-1
    confidence: float  # 0-1
    avg_watch_duration: float = 0.0
    completion_rate: float = 0.0


@dataclass
class LearningRecord:
    """学习记录"""
    topic: str
    initial_score: float = 0.0
    current_score: float = 0.0
    progress_history: List[float] = field(default_factory=list)
    days_studying: int = 0


@dataclass
class EnhancedUserProfile:
    """增强用户画像（15+维度）"""
    user_id: str

    # ===== 维度1：观看习惯 =====
    avg_watch_time: float = 0.0  # 平均观看时长（秒）
    watch_frequency: float = 0.0  # 观看频率（次/天）
    completion_rate: float = 0.0  # 完成率
    total_watch_hours: float = 0.0  # 总观看小时数

    # ===== 维度2：内容偏好 =====
    interests: Dict[str, float] = field(default_factory=dict)  # 标签 -> 权重
    favorite_topics: List[str] = field(default_factory=list)
    disliked_topics: List[str] = field(default_factory=list)
    content_preferences: Dict[str, ContentPreference] = field(default_factory=dict)

    # ===== 维度3：交互行为 =====
    like_rate: float = 0.0  # 点赞率
    share_rate: float = 0.0  # 分享率
    comment_rate: float = 0.0  # 评论率
    save_rate: float = 0.0  # 保存率
    total_interactions: int = 0

    # ===== 维度4：设备信息 =====
    primary_device: str = "unknown"  # mobile, desktop, tablet
    primary_platform: str = "unknown"  # web, ios, android
    device_diversity: float = 0.0  # 设备多样性指数 (0-1)
    devices_used: Dict[str, int] = field(default_factory=dict)  # 设备统计

    # ===== 维度5：时间模式 =====
    peak_hours: List[int] = field(default_factory=list)  # 高峰小时 (0-23)
    weekend_usage: float = 0.0  # 周末使用率 (0-1)
    weekday_usage: float = 0.0  # 工作日使用率 (0-1)
    time_patterns: Dict[str, TimePattern] = field(default_factory=dict)
    active_period: str = "unknown"  # morning, afternoon, evening, night

    # ===== 维度6：社交属性 =====
    share_frequency: float = 0.0  # 分享频率
    social_influence_score: float = 0.0  # 社交影响力 (0-1)
    follower_count: int = 0
    following_count: int = 0
    share_targets: Dict[str, int] = field(default_factory=dict)  # 分享渠道统计

    # ===== 维度7：学习曲线 =====
    knowledge_level: Dict[str, float] = field(default_factory=dict)  # 知识水平
    learning_speed: float = 0.0  # 学习速度 (0-1)
    learning_records: Dict[str, LearningRecord] = field(default_factory=dict)
    skill_progression: Dict[str, List[float]] = field(default_factory=dict)
    expertise_areas: List[str] = field(default_factory=list)  # 专长领域

    # ===== 维度8：注意力模式 =====
    attention_span: float = 0.0  # 平均注意力持续时间（分钟）
    skip_rate: float = 0.0  # 跳过率
    rewatch_rate: float = 0.0  # 重看率
    early_drop_rate: float = 0.0  # 早期放弃率

    # ===== 维度9：内容深度 =====
    depth_preference: float = 0.5  # 0=浅层, 1=深度
    complexity_tolerance: float = 0.5  # 复杂度容受度 (0-1)
    educational_content_ratio: float = 0.0  # 教育内容比例

    # ===== 维度10：多样性需求 =====
    exploration_rate: float = 0.3  # 探索新内容的比例
    exploitation_rate: float = 0.7  # 利用已知兴趣的比例
    novelty_seeking: float = 0.5  # 寻求新奇度 (0-1)
    category_diversity: float = 0.0  # 分类多样性指数

    # ===== 维度11：反馈质量 =====
    feedback_count: int = 0
    feedback_detail_score: float = 0.0  # 反馈详细度 (0-1)
    feedback_accuracy: float = 0.0  # 反馈准确性 (0-1)
    avg_feedback_length: float = 0.0  # 平均反馈长度

    # ===== 维度12：付费意愿 =====
    premium_probability: float = 0.0  # 付费概率 (0-1)
    estimated_lifetime_value: float = 0.0  # 预估生命周期价值
    premium_feature_interest: Dict[str, float] = field(default_factory=dict)
    price_sensitivity: float = 0.5  # 价格敏感度 (0=不敏感, 1=敏感)

    # ===== 维度13：流失风险 =====
    churn_risk: float = 0.0  # 流失风险 (0-1)
    days_since_last_active: int = 0
    activity_decline: float = 0.0  # 活动衰减趋势
    risk_factors: List[str] = field(default_factory=list)  # 风险因素

    # ===== 维度14：影响因子 =====
    content_creator: bool = False
    community_contribution: float = 0.0  # 社区贡献度 (0-1)
    influence_score: float = 0.0  # 影响力评分
    content_sharing_impact: float = 0.0  # 内容分享影响力

    # ===== 维度15：生命周期阶段 =====
    lifecycle_stage: LifecycleStage = LifecycleStage.NEW
    days_since_signup: int = 0
    stage_transition_history: List[Tuple[LifecycleStage, datetime]] = field(
        default_factory=list
    )

    # ===== 元数据 =====
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    signup_date: Optional[datetime] = None


class EnhancedProfileManager:
    """增强用户画像管理器"""

    def __init__(self):
        """初始化管理器"""
        self.profiles: Dict[str, EnhancedUserProfile] = {}
        self.behavior_history: Dict[str, List[Dict]] = defaultdict(list)

    def create_profile(self, user_id: str) -> EnhancedUserProfile:
        """创建新用户画像"""
        if user_id not in self.profiles:
            profile = EnhancedUserProfile(
                user_id=user_id,
                signup_date=datetime.now()
            )
            self.profiles[user_id] = profile
        return self.profiles[user_id]

    def get_profile(self, user_id: str) -> Optional[EnhancedUserProfile]:
        """获取用户画像"""
        return self.profiles.get(user_id)

    def update_from_watch_event(
        self,
        user_id: str,
        video_id: str,
        category: str,
        tags: List[str],
        watch_time: float,
        watch_percentage: float,
        device: str,
        platform: str,
        timestamp: Optional[datetime] = None
    ):
        """
        从观看事件更新画像

        Args:
            user_id: 用户ID
            video_id: 视频ID
            category: 视频分类
            tags: 视频标签
            watch_time: 观看时长（秒）
            watch_percentage: 观看百分比 (0-1)
            device: 设备类型
            platform: 平台
            timestamp: 时间戳
        """
        if user_id not in self.profiles:
            self.create_profile(user_id)

        profile = self.profiles[user_id]
        timestamp = timestamp or datetime.now()

        # 记录行为
        self.behavior_history[user_id].append({
            'type': 'watch',
            'video_id': video_id,
            'category': category,
            'tags': tags,
            'watch_time': watch_time,
            'watch_percentage': watch_percentage,
            'device': device,
            'platform': platform,
            'timestamp': timestamp
        })

        # 更新各维度
        self._update_watch_habits(profile, watch_time, watch_percentage)
        self._update_content_preferences(profile, category, tags, watch_percentage)
        self._update_device_info(profile, device, platform)
        self._update_time_patterns(profile, timestamp)
        self._update_attention_patterns(profile, watch_time, watch_percentage)
        self._update_depth_preferences(profile, tags)
        self._update_learning_curve(profile, tags, watch_percentage)
        self._update_lifecycle(profile)

        profile.last_updated = datetime.now()

    def update_from_interaction_event(
        self,
        user_id: str,
        video_id: str,
        action: str,  # like, dislike, share, comment, save
        details: Optional[Dict] = None,
        timestamp: Optional[datetime] = None
    ):
        """
        从交互事件更新画像

        Args:
            user_id: 用户ID
            video_id: 视频ID
            action: 交互动作
            details: 额外信息
            timestamp: 时间戳
        """
        if user_id not in self.profiles:
            self.create_profile(user_id)

        profile = self.profiles[user_id]
        timestamp = timestamp or datetime.now()
        details = details or {}

        # 记录行为
        self.behavior_history[user_id].append({
            'type': 'interaction',
            'video_id': video_id,
            'action': action,
            'details': details,
            'timestamp': timestamp
        })

        # 更新交互行为维度
        self._update_interaction_behaviors(profile, action, details)

        # 更新社交属性
        if action == 'share':
            self._update_social_attributes(profile, action, details)

        # 更新反馈质量
        if action == 'comment':
            self._update_feedback_quality(profile, details.get('comment_text', ''))

        profile.total_interactions += 1
        profile.last_updated = datetime.now()

    def _update_watch_habits(
        self,
        profile: EnhancedUserProfile,
        watch_time: float,
        watch_percentage: float
    ):
        """更新观看习惯维度"""
        # 更新平均观看时长（指数移动平均）
        alpha = 0.3
        profile.avg_watch_time = (
            (1 - alpha) * profile.avg_watch_time + alpha * watch_time
        )

        # 更新总观看小时数
        profile.total_watch_hours += watch_time / 3600

        # 更新观看频率
        if profile.days_since_signup > 0:
            watch_count = sum(
                1 for e in self.behavior_history[profile.user_id]
                if e['type'] == 'watch'
            )
            profile.watch_frequency = watch_count / max(profile.days_since_signup, 1)

        # 更新完成率
        completion_rates = [
            e['watch_percentage'] for e in self.behavior_history[profile.user_id]
            if e['type'] == 'watch'
        ]
        if completion_rates:
            profile.completion_rate = sum(completion_rates) / len(completion_rates)

    def _update_content_preferences(
        self,
        profile: EnhancedUserProfile,
        category: str,
        tags: List[str],
        watch_percentage: float
    ):
        """更新内容偏好维度"""
        # 更新分类偏好
        if category not in profile.content_preferences:
            profile.content_preferences[category] = ContentPreference(
                category=category,
                weight=0.0,
                confidence=0.0
            )

        pref = profile.content_preferences[category]
        alpha = 0.3
        pref.weight = (1 - alpha) * pref.weight + alpha * watch_percentage

        # 更新标签权重
        for tag in tags:
            if tag not in profile.interests:
                profile.interests[tag] = 0.0
            profile.interests[tag] = (
                (1 - alpha) * profile.interests[tag] + alpha * watch_percentage
            )

        # 更新热门话题
        sorted_interests = sorted(
            profile.interests.items(),
            key=lambda x: x[1],
            reverse=True
        )
        profile.favorite_topics = [t[0] for t in sorted_interests[:5]]

    def _update_device_info(
        self,
        profile: EnhancedUserProfile,
        device: str,
        platform: str
    ):
        """更新设备信息维度"""
        # 更新设备类型
        if device not in profile.devices_used:
            profile.devices_used[device] = 0
        profile.devices_used[device] += 1

        # 设置主要设备
        if profile.devices_used[device] >= sum(profile.devices_used.values()) * 0.3:
            profile.primary_device = device
            profile.primary_platform = platform

        # 计算设备多样性 (Shannon熵)
        total = sum(profile.devices_used.values())
        if total > 0:
            entropy = 0.0
            for count in profile.devices_used.values():
                p = count / total
                if p > 0:
                    entropy -= p * math.log2(p)
            max_entropy = math.log2(max(len(profile.devices_used), 1))
            profile.device_diversity = entropy / max_entropy if max_entropy > 0 else 0

    def _update_time_patterns(
        self,
        profile: EnhancedUserProfile,
        timestamp: datetime
    ):
        """更新时间模式维度"""
        hour = timestamp.hour
        day_of_week = timestamp.weekday()

        # 计算每小时活动
        hour_key = f"hour_{hour}"
        if hour_key not in profile.time_patterns:
            profile.time_patterns[hour_key] = TimePattern(
                hour=hour,
                day_of_week=-1
            )
        profile.time_patterns[hour_key].session_count += 1

        # 计算周末/工作日使用率
        total_sessions = sum(
            p.session_count for p in profile.time_patterns.values()
        )
        if total_sessions > 0:
            weekend_sessions = sum(
                p.session_count for p in profile.time_patterns.values()
                if p.day_of_week >= 5
            )
            profile.weekend_usage = weekend_sessions / total_sessions
            profile.weekday_usage = 1 - profile.weekend_usage

        # 确定高峰时段
        time_pattern_list = sorted(
            profile.time_patterns.values(),
            key=lambda x: x.session_count,
            reverse=True
        )
        profile.peak_hours = [p.hour for p in time_pattern_list[:3]]

        # 确定活跃时段
        if profile.peak_hours:
            avg_hour = sum(profile.peak_hours) / len(profile.peak_hours)
            if 6 <= avg_hour < 12:
                profile.active_period = "morning"
            elif 12 <= avg_hour < 18:
                profile.active_period = "afternoon"
            elif 18 <= avg_hour < 24:
                profile.active_period = "evening"
            else:
                profile.active_period = "night"

    def _update_interaction_behaviors(
        self,
        profile: EnhancedUserProfile,
        action: str,
        details: Dict
    ):
        """更新交互行为维度"""
        watch_count = sum(
            1 for e in self.behavior_history[profile.user_id]
            if e['type'] == 'watch'
        ) or 1

        interaction_count = sum(
            1 for e in self.behavior_history[profile.user_id]
            if e['type'] == 'interaction'
        ) + 1

        if action == 'like':
            profile.like_rate = interaction_count / watch_count
        elif action == 'share':
            profile.share_rate = interaction_count / watch_count
        elif action == 'comment':
            profile.comment_rate = interaction_count / watch_count
        elif action == 'save':
            profile.save_rate = interaction_count / watch_count

    def _update_social_attributes(
        self,
        profile: EnhancedUserProfile,
        action: str,
        details: Dict
    ):
        """更新社交属性维度"""
        if action == 'share':
            target = details.get('target', 'unknown')
            if target not in profile.share_targets:
                profile.share_targets[target] = 0
            profile.share_targets[target] += 1

            # 更新分享频率
            profile.share_frequency = profile.share_rate

            # 计算社交影响力（分享频率和范围）
            unique_targets = len(profile.share_targets)
            total_shares = sum(profile.share_targets.values())
            profile.social_influence_score = min(
                (profile.share_frequency + unique_targets / 10) / 2,
                1.0
            )

            # 估算影响力
            profile.influence_score = (
                profile.social_influence_score * (profile.follower_count / 1000 + 1)
            )

    def _update_feedback_quality(
        self,
        profile: EnhancedUserProfile,
        feedback_text: str
    ):
        """更新反馈质量维度"""
        profile.feedback_count += 1

        # 计算反馈详细度
        text_length = len(feedback_text.split())
        profile.avg_feedback_length = (
            (profile.avg_feedback_length * (profile.feedback_count - 1) + text_length) /
            profile.feedback_count
        )
        profile.feedback_detail_score = min(text_length / 50, 1.0)

        # 简化的准确性评估（可基于后续用户反馈）
        profile.feedback_accuracy = 0.7  # 默认值，应由系统更新

    def _update_attention_patterns(
        self,
        profile: EnhancedUserProfile,
        watch_time: float,
        watch_percentage: float
    ):
        """更新注意力模式维度"""
        # 计算注意力持续时间
        if watch_percentage > 0.9:
            attention_minutes = watch_time / 60
            alpha = 0.3
            profile.attention_span = (
                (1 - alpha) * profile.attention_span + alpha * attention_minutes
            )

        # 计算跳过率
        skip_events = sum(
            1 for e in self.behavior_history[profile.user_id]
            if e['type'] == 'interaction' and e['action'] == 'skip'
        )
        total_events = sum(
            1 for e in self.behavior_history[profile.user_id]
            if e['type'] == 'watch' or (e['type'] == 'interaction' and e['action'] == 'skip')
        ) or 1
        profile.skip_rate = skip_events / total_events

        # 计算重看率（需要跟踪视频ID）
        watch_events = [
            e for e in self.behavior_history[profile.user_id]
            if e['type'] == 'watch'
        ]
        video_ids = [e['video_id'] for e in watch_events]
        rewatch_count = sum(1 for vid in video_ids if video_ids.count(vid) > 1)
        profile.rewatch_rate = rewatch_count / len(video_ids) if video_ids else 0

        # 计算早期放弃率
        early_drops = sum(
            1 for e in watch_events
            if e['watch_percentage'] < 0.2
        )
        profile.early_drop_rate = early_drops / len(watch_events) if watch_events else 0

    def _update_depth_preferences(
        self,
        profile: EnhancedUserProfile,
        tags: List[str]
    ):
        """更新内容深度维度"""
        # 根据标签判断内容深度
        deep_keywords = {'深入', '详细', '完整', '高级', '专业', '深度', '分析'}
        shallow_keywords = {'速览', '简介', '快速', '简单', '入门', '基础'}

        deep_count = sum(1 for tag in tags if any(kw in tag for kw in deep_keywords))
        shallow_count = sum(1 for tag in tags if any(kw in tag for kw in shallow_keywords))

        if deep_count + shallow_count > 0:
            alpha = 0.3
            new_depth = deep_count / (deep_count + shallow_count)
            profile.depth_preference = (
                (1 - alpha) * profile.depth_preference + alpha * new_depth
            )

    def _update_learning_curve(
        self,
        profile: EnhancedUserProfile,
        tags: List[str],
        watch_percentage: float
    ):
        """更新学习曲线维度"""
        for tag in tags:
            if tag not in profile.learning_records:
                profile.learning_records[tag] = LearningRecord(topic=tag)

            record = profile.learning_records[tag]
            record.days_studying += 1

            # 模拟学习进度
            if watch_percentage > 0.8:
                progress = min(record.current_score + 0.1, 1.0)
            elif watch_percentage > 0.5:
                progress = min(record.current_score + 0.05, 1.0)
            else:
                progress = record.current_score

            record.current_score = progress
            record.progress_history.append(progress)

        # 更新学习速度
        if profile.learning_records:
            avg_progress = sum(
                max(0, r.current_score - r.initial_score)
                for r in profile.learning_records.values()
            ) / len(profile.learning_records)
            profile.learning_speed = min(avg_progress, 1.0)

            # 确定专长领域
            profile.expertise_areas = [
                topic for topic, record in profile.learning_records.items()
                if record.current_score > 0.7
            ]

    def _update_lifecycle(self, profile: EnhancedUserProfile):
        """更新生命周期阶段维度"""
        if profile.signup_date:
            profile.days_since_signup = (
                datetime.now() - profile.signup_date
            ).days

        # 计算日期最后活跃
        if self.behavior_history[profile.user_id]:
            last_event = self.behavior_history[profile.user_id][-1]
            profile.days_since_last_active = (
                datetime.now() - last_event['timestamp']
            ).days

        # 确定生命周期阶段
        old_stage = profile.lifecycle_stage

        if profile.days_since_signup < 7:
            new_stage = LifecycleStage.NEW
        elif profile.days_since_signup < 30:
            new_stage = LifecycleStage.GROWING
        elif profile.churn_risk > 0.7:
            new_stage = LifecycleStage.AT_RISK
        elif profile.days_since_last_active > 30:
            new_stage = LifecycleStage.CHURNED
        else:
            new_stage = LifecycleStage.MATURE

        profile.lifecycle_stage = new_stage

        # 记录阶段变化
        if old_stage != new_stage:
            profile.stage_transition_history.append((new_stage, datetime.now()))

    def calculate_churn_risk(self, user_id: str) -> float:
        """
        计算用户流失风险

        Args:
            user_id: 用户ID

        Returns:
            流失风险评分 (0-1)
        """
        profile = self.profiles.get(user_id)
        if not profile:
            return 0.5

        # 多因素评估流失风险
        risk_score = 0.0
        weight_sum = 0.0

        # 1. 最近活动衰退
        if profile.days_since_last_active > 0:
            recency_risk = min(profile.days_since_last_active / 60, 1.0) * 0.3
            risk_score += recency_risk
            weight_sum += 0.3

        # 2. 活动频率下降
        watch_events = [
            e for e in self.behavior_history[user_id]
            if e['type'] == 'watch'
        ]
        if len(watch_events) > 10:
            # 比较最近10个和之前的活动
            recent = watch_events[-10:]
            earlier = watch_events[:10]
            recent_interval = (
                (recent[-1]['timestamp'] - recent[0]['timestamp']).total_seconds() / 9
                if len(recent) > 1 else 0
            )
            earlier_interval = (
                (earlier[-1]['timestamp'] - earlier[0]['timestamp']).total_seconds() / 9
                if len(earlier) > 1 else 1
            )

            if earlier_interval > 0:
                frequency_decline = min(recent_interval / earlier_interval, 1.0)
                activity_decline_risk = (1 - frequency_decline) * 0.3
                risk_score += activity_decline_risk
                profile.activity_decline = 1 - frequency_decline
                weight_sum += 0.3

        # 3. 低参与度
        engagement = (profile.like_rate + profile.comment_rate + profile.share_rate) / 3
        engagement_risk = (1 - engagement) * 0.2
        risk_score += engagement_risk
        weight_sum += 0.2

        # 4. 完成率低
        completion_risk = (1 - profile.completion_rate) * 0.2
        risk_score += completion_risk
        weight_sum += 0.2

        profile.churn_risk = risk_score / weight_sum if weight_sum > 0 else 0.5

        # 识别风险因素
        profile.risk_factors = []
        if profile.days_since_last_active > 14:
            profile.risk_factors.append("长期不活跃")
        if profile.activity_decline > 0.5:
            profile.risk_factors.append("活动频率下降")
        if engagement < 0.2:
            profile.risk_factors.append("参与度低")
        if profile.completion_rate < 0.5:
            profile.risk_factors.append("完成率低")

        return profile.churn_risk

    def calculate_lifetime_value(self, user_id: str) -> float:
        """
        计算用户生命周期价值（LTV）

        Args:
            user_id: 用户ID

        Returns:
            估计LTV
        """
        profile = self.profiles.get(user_id)
        if not profile:
            return 0.0

        # 基于多个因素计算LTV
        ltv = 0.0

        # 1. 参与度贡献
        engagement = (
            (profile.like_rate + profile.comment_rate + profile.share_rate) / 3
        )
        ltv += engagement * 100

        # 2. 学习速度贡献
        ltv += profile.learning_speed * 50

        # 3. 社交影响力贡献
        ltv += profile.social_influence_score * 100

        # 4. 总观看小时贡献
        ltv += min(profile.total_watch_hours / 100 * 100, 100)

        # 5. 内容创作者奖励
        if profile.content_creator:
            ltv += 200

        # 6. 付费意愿
        ltv += profile.premium_probability * 100

        profile.estimated_lifetime_value = ltv
        return ltv

    def get_personalization_vector(
        self,
        user_id: str
    ) -> Dict[str, float]:
        """
        获取用户的个性化向量（用于推荐系统）

        Args:
            user_id: 用户ID

        Returns:
            个性化向量字典
        """
        profile = self.profiles.get(user_id)
        if not profile:
            return {}

        # 计算各个维度的综合向量
        vector = {
            # 维度1：观看习惯
            'engagement_level': min(
                (profile.like_rate + profile.share_rate) / 2,
                1.0
            ),
            'watch_frequency': min(profile.watch_frequency / 2, 1.0),
            'completion_tendency': profile.completion_rate,

            # 维度2：内容偏好
            'interest_diversity': len(profile.favorite_topics) / 20,
            'favorite_topic_count': len(profile.favorite_topics),

            # 维度3：交互行为
            'interaction_rate': profile.comment_rate,
            'sharing_tendency': profile.share_rate,

            # 维度4：设备多样性
            'device_diversity': profile.device_diversity,
            'is_mobile_primary': 1.0 if profile.primary_device == 'mobile' else 0.0,

            # 维度5：时间模式
            'peak_hour_concentration': len(profile.peak_hours) / 24,
            'weekend_preference': profile.weekend_usage,

            # 维度6：社交属性
            'social_influence': profile.social_influence_score,
            'sharing_frequency': profile.share_frequency,

            # 维度7：学习曲线
            'learning_speed': profile.learning_speed,
            'expertise_count': len(profile.expertise_areas) / 10,

            # 维度8：注意力模式
            'attention_span_normalized': min(profile.attention_span / 30, 1.0),
            'skip_rate': profile.skip_rate,
            'rewatch_tendency': profile.rewatch_rate,

            # 维度9：内容深度
            'depth_preference': profile.depth_preference,
            'complexity_tolerance': profile.complexity_tolerance,

            # 维度10：多样性需求
            'exploration_rate': profile.exploration_rate,
            'novelty_seeking': profile.novelty_seeking,

            # 维度11：反馈质量
            'feedback_quality': profile.feedback_detail_score,

            # 维度12：付费意愿
            'premium_probability': profile.premium_probability,

            # 维度13：流失风险
            'churn_risk': profile.churn_risk,
            'days_inactive': min(profile.days_since_last_active / 30, 1.0),

            # 维度14：影响因子
            'creator_status': 1.0 if profile.content_creator else 0.0,
            'community_contribution': profile.community_contribution,

            # 维度15：生命周期
            'is_new_user': 1.0 if profile.lifecycle_stage == LifecycleStage.NEW else 0.0,
            'is_mature_user': 1.0 if profile.lifecycle_stage == LifecycleStage.MATURE else 0.0,
            'is_at_risk': 1.0 if profile.lifecycle_stage == LifecycleStage.AT_RISK else 0.0,
        }

        return vector

    def get_profile_summary(self, user_id: str) -> Dict:
        """获取用户画像摘要"""
        profile = self.profiles.get(user_id)
        if not profile:
            return {}

        # 计算流失风险和LTV
        self.calculate_churn_risk(user_id)
        self.calculate_lifetime_value(user_id)

        return {
            'user_id': user_id,
            '观看习惯': {
                '平均观看时长': f"{profile.avg_watch_time:.1f}秒",
                '观看频率': f"{profile.watch_frequency:.2f}次/天",
                '完成率': f"{profile.completion_rate:.1%}",
                '总观看小时数': f"{profile.total_watch_hours:.1f}小时"
            },
            '内容偏好': {
                '热门话题': profile.favorite_topics[:3],
                '兴趣标签数': len(profile.interests)
            },
            '交互行为': {
                '点赞率': f"{profile.like_rate:.1%}",
                '分享率': f"{profile.share_rate:.1%}",
                '评论率': f"{profile.comment_rate:.1%}",
                '总交互数': profile.total_interactions
            },
            '设备信息': {
                '主要设备': profile.primary_device,
                '主要平台': profile.primary_platform,
                '设备多样性': f"{profile.device_diversity:.2f}"
            },
            '时间模式': {
                '高峰小时': profile.peak_hours,
                '活跃时段': profile.active_period,
                '周末使用率': f"{profile.weekend_usage:.1%}"
            },
            '社交属性': {
                '社交影响力': f"{profile.social_influence_score:.2f}",
                '分享频率': f"{profile.share_frequency:.2f}",
                '粉丝数': profile.follower_count
            },
            '学习曲线': {
                '学习速度': f"{profile.learning_speed:.2f}",
                '专长领域': profile.expertise_areas[:3]
            },
            '注意力模式': {
                '注意力跨度': f"{profile.attention_span:.1f}分钟",
                '跳过率': f"{profile.skip_rate:.1%}",
                '重看率': f"{profile.rewatch_rate:.1%}"
            },
            '内容深度': {
                '深度偏好': f"{profile.depth_preference:.2f}",
                '复杂度容受度': f"{profile.complexity_tolerance:.2f}"
            },
            '多样性需求': {
                '探索率': f"{profile.exploration_rate:.1%}",
                '利用率': f"{profile.exploitation_rate:.1%}",
                '新奇寻求': f"{profile.novelty_seeking:.2f}"
            },
            '反馈质量': {
                '反馈数量': profile.feedback_count,
                '反馈详细度': f"{profile.feedback_detail_score:.2f}"
            },
            '付费意愿': {
                '付费概率': f"{profile.premium_probability:.1%}",
                '生命周期价值': f"${profile.estimated_lifetime_value:.2f}"
            },
            '流失风险': {
                '风险评分': f"{profile.churn_risk:.2f}",
                '最后活跃天数': profile.days_since_last_active,
                '风险因素': profile.risk_factors
            },
            '影响因子': {
                '内容创作者': profile.content_creator,
                '社区贡献度': f"{profile.community_contribution:.2f}",
                '影响力评分': f"{profile.influence_score:.2f}"
            },
            '生命周期': {
                '当前阶段': profile.lifecycle_stage.value,
                '注册天数': profile.days_since_signup
            }
        }

    def save_profile(self, user_id: str, filepath: str):
        """保存用户画像到文件"""
        profile = self.profiles.get(user_id)
        if not profile:
            return

        # 转换为可序列化的格式
        data = {
            'user_id': profile.user_id,
            'avg_watch_time': profile.avg_watch_time,
            'watch_frequency': profile.watch_frequency,
            'completion_rate': profile.completion_rate,
            'total_watch_hours': profile.total_watch_hours,
            'interests': profile.interests,
            'favorite_topics': profile.favorite_topics,
            'disliked_topics': profile.disliked_topics,
            'like_rate': profile.like_rate,
            'share_rate': profile.share_rate,
            'comment_rate': profile.comment_rate,
            'save_rate': profile.save_rate,
            'primary_device': profile.primary_device,
            'primary_platform': profile.primary_platform,
            'device_diversity': profile.device_diversity,
            'peak_hours': profile.peak_hours,
            'weekend_usage': profile.weekend_usage,
            'weekday_usage': profile.weekday_usage,
            'active_period': profile.active_period,
            'social_influence_score': profile.social_influence_score,
            'learning_speed': profile.learning_speed,
            'expertise_areas': profile.expertise_areas,
            'attention_span': profile.attention_span,
            'skip_rate': profile.skip_rate,
            'rewatch_rate': profile.rewatch_rate,
            'depth_preference': profile.depth_preference,
            'complexity_tolerance': profile.complexity_tolerance,
            'exploration_rate': profile.exploration_rate,
            'exploitation_rate': profile.exploitation_rate,
            'feedback_count': profile.feedback_count,
            'feedback_detail_score': profile.feedback_detail_score,
            'premium_probability': profile.premium_probability,
            'estimated_lifetime_value': profile.estimated_lifetime_value,
            'churn_risk': profile.churn_risk,
            'lifecycle_stage': profile.lifecycle_stage.value,
            'days_since_signup': profile.days_since_signup,
            'days_since_last_active': profile.days_since_last_active,
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)

    def load_profile(self, filepath: str) -> Optional[EnhancedUserProfile]:
        """从文件加载用户画像"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        user_id = data['user_id']
        profile = EnhancedUserProfile(user_id=user_id)

        # 恢复各个字段
        profile.avg_watch_time = data.get('avg_watch_time', 0.0)
        profile.watch_frequency = data.get('watch_frequency', 0.0)
        profile.completion_rate = data.get('completion_rate', 0.0)
        profile.total_watch_hours = data.get('total_watch_hours', 0.0)
        profile.interests = data.get('interests', {})
        profile.favorite_topics = data.get('favorite_topics', [])
        profile.disliked_topics = data.get('disliked_topics', [])
        profile.like_rate = data.get('like_rate', 0.0)
        profile.share_rate = data.get('share_rate', 0.0)
        profile.comment_rate = data.get('comment_rate', 0.0)
        profile.save_rate = data.get('save_rate', 0.0)
        profile.primary_device = data.get('primary_device', 'unknown')
        profile.primary_platform = data.get('primary_platform', 'unknown')
        profile.device_diversity = data.get('device_diversity', 0.0)
        profile.peak_hours = data.get('peak_hours', [])
        profile.weekend_usage = data.get('weekend_usage', 0.0)
        profile.weekday_usage = data.get('weekday_usage', 0.0)
        profile.active_period = data.get('active_period', 'unknown')
        profile.social_influence_score = data.get('social_influence_score', 0.0)
        profile.learning_speed = data.get('learning_speed', 0.0)
        profile.expertise_areas = data.get('expertise_areas', [])
        profile.attention_span = data.get('attention_span', 0.0)
        profile.skip_rate = data.get('skip_rate', 0.0)
        profile.rewatch_rate = data.get('rewatch_rate', 0.0)
        profile.depth_preference = data.get('depth_preference', 0.5)
        profile.complexity_tolerance = data.get('complexity_tolerance', 0.5)
        profile.exploration_rate = data.get('exploration_rate', 0.3)
        profile.exploitation_rate = data.get('exploitation_rate', 0.7)
        profile.feedback_count = data.get('feedback_count', 0)
        profile.feedback_detail_score = data.get('feedback_detail_score', 0.0)
        profile.premium_probability = data.get('premium_probability', 0.0)
        profile.estimated_lifetime_value = data.get('estimated_lifetime_value', 0.0)
        profile.churn_risk = data.get('churn_risk', 0.0)

        stage_str = data.get('lifecycle_stage', 'new')
        profile.lifecycle_stage = LifecycleStage(stage_str)
        profile.days_since_signup = data.get('days_since_signup', 0)
        profile.days_since_last_active = data.get('days_since_last_active', 0)

        self.profiles[user_id] = profile
        return profile


if __name__ == "__main__":
    print("增强用户画像系统已加载")
