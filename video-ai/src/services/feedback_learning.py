"""
用户反馈学习系统

从用户反馈中持续学习和优化视频编辑策略。
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime
import json
from pathlib import Path
from collections import defaultdict
import numpy as np


@dataclass
class Feedback:
    """用户反馈"""
    user_id: str
    video_id: str
    feedback_type: str  # segment_quality, transition_quality, order_quality, overall
    rating: float  # 1-5 星
    segment_id: Optional[str] = None
    comment: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)

    # 上下文信息
    user_interests: List[str] = field(default_factory=list)
    used_strategy: str = ""  # 使用的策略名称
    video_metadata: Dict = field(default_factory=dict)  # 视频元数据

    def to_dict(self) -> Dict:
        """转换为字典"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict) -> 'Feedback':
        """从字典创建"""
        data = data.copy()
        if 'timestamp' in data and isinstance(data['timestamp'], str):
            data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)


@dataclass
class FeedbackStats:
    """反馈统计"""
    total_count: int = 0
    average_rating: float = 0.0
    positive_count: int = 0  # 评分 >= 4
    negative_count: int = 0  # 评分 <= 2
    neutral_count: int = 0  # 评分 == 3
    by_strategy: Dict[str, float] = field(default_factory=dict)
    by_type: Dict[str, float] = field(default_factory=dict)
    trend: str = "stable"  # improving, declining, stable

    def to_dict(self) -> Dict:
        """转换为字典"""
        return asdict(self)


@dataclass
class LearningReport:
    """学习报告"""
    best_strategy: Optional[Tuple[str, float]] = None
    worst_strategy: Optional[Tuple[str, float]] = None
    negative_patterns: List[Dict] = field(default_factory=list)
    improvements: List[str] = field(default_factory=list)
    stats: Optional[FeedbackStats] = None
    strategy_rankings: List[Tuple[str, float]] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """转换为字典"""
        data = asdict(self)
        if self.stats:
            data['stats'] = self.stats.to_dict()
        return data


class FeedbackLearningSystem:
    """反馈学习系统"""

    def __init__(
        self,
        storage_dir: str = "data/feedback",
        learning_rate: float = 0.1,
        min_feedback_count: int = 3
    ):
        """
        初始化反馈学习系统

        Args:
            storage_dir: 反馈数据存储目录
            learning_rate: 学习率
            min_feedback_count: 最少反馈数量（用于统计）
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        self.learning_rate = learning_rate
        self.min_feedback_count = min_feedback_count

        # 反馈缓存
        self.feedbacks: List[Feedback] = []

        # 策略性能统计
        self.strategy_performance: Dict[str, float] = {}

        # 加载历史反馈
        self._load_feedbacks()

        # 初始化策略权重
        self._initialize_strategy_weights()

    def collect_feedback(self, feedback: Feedback) -> bool:
        """
        收集用户反馈

        Args:
            feedback: 反馈对象

        Returns:
            是否成功收集
        """
        try:
            # 验证反馈
            if not self._validate_feedback(feedback):
                return False

            # 保存到内存
            self.feedbacks.append(feedback)

            # 持久化
            self._save_feedback(feedback)

            # 更新统计
            self._update_statistics(feedback)

            return True

        except Exception as e:
            print(f"收集反馈失败: {e}")
            return False

    def _validate_feedback(self, feedback: Feedback) -> bool:
        """验证反馈有效性"""
        if not feedback.user_id or not feedback.video_id:
            return False

        if feedback.rating < 1 or feedback.rating > 5:
            return False

        if feedback.feedback_type not in ['segment_quality', 'transition_quality',
                                          'order_quality', 'overall']:
            return False

        return True

    def analyze_feedback(
        self,
        feedback_type: Optional[str] = None,
        min_rating: Optional[float] = None,
        max_rating: Optional[float] = None,
        strategy: Optional[str] = None,
        days: Optional[int] = None
    ) -> FeedbackStats:
        """
        分析反馈数据

        Args:
            feedback_type: 过滤的反馈类型
            min_rating: 最小评分过滤
            max_rating: 最大评分过滤
            strategy: 策略名称过滤
            days: 最近N天的反馈

        Returns:
            FeedbackStats对象
        """
        # 过滤反馈
        filtered = self.feedbacks.copy()

        if feedback_type:
            filtered = [f for f in filtered if f.feedback_type == feedback_type]

        if min_rating is not None:
            filtered = [f for f in filtered if f.rating >= min_rating]

        if max_rating is not None:
            filtered = [f for f in filtered if f.rating <= max_rating]

        if strategy:
            filtered = [f for f in filtered if f.used_strategy == strategy]

        if days:
            cutoff = datetime.now().timestamp() - (days * 24 * 3600)
            filtered = [f for f in filtered if f.timestamp.timestamp() >= cutoff]

        # 计算统计
        total = len(filtered)
        if total == 0:
            return FeedbackStats()

        avg_rating = sum(f.rating for f in filtered) / total
        positive = sum(1 for f in filtered if f.rating >= 4)
        negative = sum(1 for f in filtered if f.rating <= 2)
        neutral = sum(1 for f in filtered if f.rating == 3)

        # 按策略统计
        by_strategy = defaultdict(list)
        for f in filtered:
            if f.used_strategy:
                by_strategy[f.used_strategy].append(f.rating)

        # 计算每个策略的平均分
        strategy_avg = {
            k: sum(v) / len(v) for k, v in by_strategy.items()
        }

        # 按反馈类型统计
        by_type = defaultdict(list)
        for f in filtered:
            by_type[f.feedback_type].append(f.rating)

        type_avg = {
            k: sum(v) / len(v) for k, v in by_type.items()
        }

        # 分析趋势
        trend = self._analyze_trend(filtered)

        return FeedbackStats(
            total_count=total,
            average_rating=avg_rating,
            positive_count=positive,
            negative_count=negative,
            neutral_count=neutral,
            by_strategy=strategy_avg,
            by_type=type_avg,
            trend=trend
        )

    def _analyze_trend(self, feedbacks: List[Feedback]) -> str:
        """分析评分趋势"""
        if len(feedbacks) < 10:
            return "stable"

        # 按时间排序
        sorted_feedbacks = sorted(feedbacks, key=lambda f: f.timestamp)

        # 计算前半部分和后半部分的平均分
        mid = len(sorted_feedbacks) // 2
        first_half_avg = sum(f.rating for f in sorted_feedbacks[:mid]) / mid
        second_half_avg = sum(f.rating for f in sorted_feedbacks[mid:]) / (len(sorted_feedbacks) - mid)

        diff = second_half_avg - first_half_avg

        if diff > 0.3:
            return "improving"
        elif diff < -0.3:
            return "declining"
        else:
            return "stable"

    def learn_from_feedback(
        self,
        auto_update: bool = True
    ) -> LearningReport:
        """
        从反馈中学习，更新模型参数

        Args:
            auto_update: 是否自动更新策略权重

        Returns:
            LearningReport对象
        """
        # 分析反馈趋势
        stats = self.analyze_feedback()

        # 识别表现最好和最差的策略
        best_strategy = None
        worst_strategy = None

        if stats.by_strategy:
            sorted_strategies = sorted(
                stats.by_strategy.items(),
                key=lambda x: x[1],
                reverse=True
            )
            best_strategy = sorted_strategies[0]
            worst_strategy = sorted_strategies[-1]

            # 调整策略权重
            if auto_update:
                for strategy, rating in stats.by_strategy.items():
                    self._update_strategy_weights(strategy, rating)

        # 识别负面反馈模式
        negative_patterns = self._analyze_negative_feedback()

        # 生成优化建议
        improvements = self._generate_improvements(negative_patterns, stats)

        # 生成推荐
        recommendations = self._generate_recommendations(stats, best_strategy)

        # 策略排名
        strategy_rankings = sorted(
            self.strategy_performance.items(),
            key=lambda x: x[1],
            reverse=True
        )

        return LearningReport(
            best_strategy=best_strategy,
            worst_strategy=worst_strategy,
            negative_patterns=negative_patterns,
            improvements=improvements,
            stats=stats,
            strategy_rankings=strategy_rankings,
            recommendations=recommendations
        )

    def _update_strategy_weights(self, strategy: str, rating: float):
        """更新策略权重"""
        if strategy not in self.strategy_performance:
            self.strategy_performance[strategy] = 0.5

        # 增量更新
        current = self.strategy_performance[strategy]
        # 将1-5评分映射到0-1范围
        target = (rating - 1.0) / 4.0

        self.strategy_performance[strategy] = (
            current * (1 - self.learning_rate) +
            target * self.learning_rate
        )

        # 保存更新后的权重
        self._save_strategy_weights()

    def _analyze_negative_feedback(self) -> List[Dict]:
        """分析负面反馈模式"""
        negative = [f for f in self.feedbacks if f.rating <= 2]

        patterns = []

        # 按反馈类型分组
        by_type = defaultdict(list)
        for f in negative:
            by_type[f.feedback_type].append(f)

        # 分析每种类型的问题
        for ftype, feedbacks in by_type.items():
            if len(feedbacks) >= self.min_feedback_count:
                # 提取常见主题
                common_themes = self._extract_common_themes(feedbacks)

                # 统计使用的策略
                strategies_used = defaultdict(int)
                for f in feedbacks:
                    if f.used_strategy:
                        strategies_used[f.used_strategy] += 1

                patterns.append({
                    'type': ftype,
                    'count': len(feedbacks),
                    'avg_rating': sum(f.rating for f in feedbacks) / len(feedbacks),
                    'common_themes': common_themes,
                    'strategies': dict(strategies_used),
                    'percentage': len(feedbacks) / len(self.feedbacks) * 100
                })

        # 按出现次数排序
        patterns.sort(key=lambda x: x['count'], reverse=True)

        return patterns

    def _extract_common_themes(self, feedbacks: List[Feedback]) -> List[str]:
        """提取常见主题/关键词"""
        comments = [f.comment for f in feedbacks if f.comment]

        if not comments:
            return []

        # 简化实现：提取关键词频率
        # TODO: 使用NLP进行更高级的主题提取

        # 分词并统计
        word_freq = defaultdict(int)
        for comment in comments:
            # 简单的中文分词（按字）
            words = comment.split()
            for word in words:
                if len(word) > 1:  # 只考虑长度大于1的词
                    word_freq[word] += 1

        # 返回最常见的主题
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, _ in sorted_words[:5]]

    def _generate_improvements(
        self,
        patterns: List[Dict],
        stats: FeedbackStats
    ) -> List[str]:
        """生成改进建议"""
        improvements = []

        # 基于负面模式的建议
        for pattern in patterns:
            if pattern['type'] == 'segment_quality':
                if pattern['percentage'] > 10:
                    improvements.append(
                        f"⚠️ 片段选择需要优化：{pattern['count']}个用户（{pattern['percentage']:.1f}%）"
                        f"反馈片段质量不佳（平均评分：{pattern['avg_rating']:.1f}）"
                    )
                    improvements.append(
                        f"   建议：提高片段相关性阈值，增强内容质量过滤"
                    )

            elif pattern['type'] == 'transition_quality':
                if pattern['percentage'] > 10:
                    improvements.append(
                        f"⚠️ 过渡效果需要改进：{pattern['count']}个用户（{pattern['percentage']:.1f}%）"
                        f"反馈过渡不流畅（平均评分：{pattern['avg_rating']:.1f}）"
                    )
                    improvements.append(
                        f"   建议：调整过渡时长，优化过渡风格选择"
                    )

            elif pattern['type'] == 'order_quality':
                if pattern['percentage'] > 10:
                    improvements.append(
                        f"⚠️ 叙事排序需要优化：{pattern['count']}个用户（{pattern['percentage']:.1f}%）"
                        f"反馈顺序不连贯（平均评分：{pattern['avg_rating']:.1f}）"
                    )
                    improvements.append(
                        f"   建议：强化叙事连贯性算法，考虑时间顺序"
                    )

        # 基于整体统计的建议
        if stats.average_rating < 3.5:
            improvements.append(
                f"⚠️ 整体满意度偏低：平均评分{stats.average_rating:.1f}/5.0"
            )
            improvements.append(
                f"   建议：全面审查当前策略，考虑增加用户配置选项"
            )

        if stats.negative_count > stats.positive_count:
            improvements.append(
                f"⚠️ 负面反馈超过正面反馈：负面{stats.negative_count}个 vs 正面{stats.positive_count}个"
            )
            improvements.append(
                f"   建议：优先处理负面反馈最多的问题类型"
            )

        # 基于趋势的建议
        if stats.trend == "declining":
            improvements.append(
                f"📉 评分呈下降趋势，需要立即关注"
            )
            improvements.append(
                f"   建议：回滚最近的策略更改，重新评估算法调整"
            )

        if not improvements:
            improvements.append("✅ 当前表现良好，继续保持！")

        return improvements

    def _generate_recommendations(
        self,
        stats: FeedbackStats,
        best_strategy: Optional[Tuple[str, float]]
    ) -> List[str]:
        """生成推荐建议"""
        recommendations = []

        if best_strategy:
            strategy_name, rating = best_strategy
            recommendations.append(
                f"🏆 推荐使用 '{strategy_name}' 策略（平均评分：{rating:.1f}/5.0）"
            )

        if stats.trend == "improving":
            recommendations.append(
                "📈 系统表现持续改善，当前策略方向正确"
            )

        if stats.positive_count > stats.total_count * 0.7:
            recommendations.append(
                f"🎉 用户满意度高（{stats.positive_count}/{stats.total_count}个正面反馈）"
            )

        # 基于反馈类型的推荐
        if stats.by_type:
            best_type = max(stats.by_type.items(), key=lambda x: x[1])
            worst_type = min(stats.by_type.items(), key=lambda x: x[1])

            if best_type[1] >= 4.0:
                type_names = {
                    'segment_quality': '片段选择',
                    'transition_quality': '过渡效果',
                    'order_quality': '叙事排序',
                    'overall': '整体体验'
                }
                recommendations.append(
                    f"⭐ {type_names.get(best_type[0], best_type[0])}表现优异（{best_type[1]:.1f}/5.0）"
                )

            if worst_type[1] < 3.5:
                type_names = {
                    'segment_quality': '片段选择',
                    'transition_quality': '过渡效果',
                    'order_quality': '叙事排序',
                    'overall': '整体体验'
                }
                recommendations.append(
                    f"⚠️ 需要关注{type_names.get(worst_type[0], worst_type[0])}（{worst_type[1]:.1f}/5.0）"
                )

        if not recommendations:
            recommendations.append("继续收集反馈以获得更多洞察")

        return recommendations

    def get_best_strategy(
        self,
        context: Optional[Dict] = None,
        fallback: str = "hybrid"
    ) -> str:
        """
        根据当前上下文推荐最佳策略

        Args:
            context: 上下文信息（用户兴趣、视频类型等）
            fallback: 默认策略

        Returns:
            推荐的策略名称
        """
        # 如果没有足够的数据，返回默认策略
        if not self.strategy_performance:
            return fallback

        # TODO: 基于上下文进行个性化策略选择
        # 目前简化实现：返回性能最好的策略

        # 获取性能最好的策略
        best_strategy = max(
            self.strategy_performance.items(),
            key=lambda x: x[1]
        )

        # 如果最好的策略评分太低，返回默认策略
        if best_strategy[1] < 0.3:
            return fallback

        return best_strategy[0]

    def get_strategy_confidence(self, strategy: str) -> float:
        """
        获取策略的置信度

        Args:
            strategy: 策略名称

        Returns:
            置信度（0-1）
        """
        if strategy not in self.strategy_performance:
            return 0.5  # 未知策略，中等置信度

        # 基于反馈数量调整置信度
        feedback_count = sum(
            1 for f in self.feedbacks if f.used_strategy == strategy
        )

        base_confidence = self.strategy_performance[strategy]

        # 反馈数量越多，置信度越高
        feedback_factor = min(feedback_count / 20, 1.0)  # 20个反馈达到最大置信度

        return base_confidence * (0.5 + 0.5 * feedback_factor)

    def export_report(
        self,
        output_path: Optional[str] = None
    ) -> str:
        """
        导出学习报告

        Args:
            output_path: 输出路径（可选）

        Returns:
            报告的JSON字符串
        """
        report = self.learn_from_feedback(auto_update=False)

        report_data = report.to_dict()

        # 添加额外信息
        report_data['generated_at'] = datetime.now().isoformat()
        report_data['total_feedbacks'] = len(self.feedbacks)
        report_data['strategy_performance'] = self.strategy_performance

        report_json = json.dumps(report_data, ensure_ascii=False, indent=2)

        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report_json)

        return report_json

    def _save_feedback(self, feedback: Feedback):
        """持久化反馈"""
        filename = f"feedback_{feedback.user_id}_{feedback.timestamp.strftime('%Y%m%d_%H%M%S')}.json"
        filepath = self.storage_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(feedback.to_dict(), f, ensure_ascii=False, indent=2)

    def _load_feedbacks(self):
        """加载历史反馈"""
        if not self.storage_dir.exists():
            return

        for filepath in self.storage_dir.glob("feedback_*.json"):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    feedback = Feedback.from_dict(data)
                    self.feedbacks.append(feedback)
            except Exception as e:
                print(f"加载反馈失败 {filepath}: {e}")

    def _initialize_strategy_weights(self):
        """初始化策略权重"""
        # 尝试加载已保存的权重
        weights_file = self.storage_dir / "strategy_weights.json"

        if weights_file.exists():
            try:
                with open(weights_file, 'r', encoding='utf-8') as f:
                    self.strategy_performance = json.load(f)
                return
            except Exception as e:
                print(f"加载策略权重失败: {e}")

        # 初始化默认权重
        default_strategies = ["hybrid", "semantic", "temporal", "interest_based"]
        for strategy in default_strategies:
            if strategy not in self.strategy_performance:
                self.strategy_performance[strategy] = 0.5

    def _save_strategy_weights(self):
        """保存策略权重"""
        weights_file = self.storage_dir / "strategy_weights.json"

        try:
            with open(weights_file, 'w', encoding='utf-8') as f:
                json.dump(self.strategy_performance, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存策略权重失败: {e}")

    def _update_statistics(self, feedback: Feedback):
        """更新实时统计"""
        # 目前在内存中维护，可以扩展为 Redis 缓存
        pass

    def get_statistics_summary(self) -> Dict:
        """获取统计摘要"""
        stats = self.analyze_feedback()

        return {
            'total_feedbacks': len(self.feedbacks),
            'average_rating': stats.average_rating,
            'positive_rate': stats.positive_count / max(stats.total_count, 1),
            'negative_rate': stats.negative_count / max(stats.total_count, 1),
            'trend': stats.trend,
            'top_strategy': max(
                self.strategy_performance.items(),
                key=lambda x: x[1]
            ) if self.strategy_performance else None
        }


if __name__ == "__main__":
    # 测试代码
    print("FeedbackLearningSystem 模块已加载")

    # 示例用法
    system = FeedbackLearningSystem()

    # 模拟收集反馈
    feedback = Feedback(
        user_id="user123",
        video_id="video456",
        feedback_type="overall",
        rating=4.5,
        comment="视频剪辑很好，但过渡有点生硬",
        user_interests=["AI", "编程"],
        used_strategy="hybrid"
    )

    system.collect_feedback(feedback)

    # 分析反馈
    stats = system.analyze_feedback()
    print(f"\n反馈统计: {stats}")

    # 学习并生成报告
    report = system.learn_from_feedback()
    print(f"\n学习报告: {report}")
