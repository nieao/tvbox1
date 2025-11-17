"""
推荐引擎模块

实现混合推荐算法：协同过滤 + 基于内容 + 热度算法
"""

from typing import List, Dict, Optional, Tuple, Set
from dataclasses import dataclass
import numpy as np
from collections import defaultdict
import math

try:
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


@dataclass
class RecommendationItem:
    """推荐项目"""
    video_id: str
    score: float
    reason: str  # 推荐原因
    cf_score: float = 0.0      # 协同过滤评分
    cb_score: float = 0.0      # 内容推荐评分
    popularity_score: float = 0.0  # 热度评分


class CollaborativeFiltering:
    """协同过滤算法"""

    def __init__(self, similarity_threshold: float = 0.1):
        """
        初始化协同过滤

        Args:
            similarity_threshold: 相似度阈值
        """
        self.similarity_threshold = similarity_threshold
        self.user_item_matrix = {}  # user_id -> {item_id: rating}
        self.similarity_cache = {}

    def add_interaction(self, user_id: str, video_id: str, rating: float):
        """添加用户-项目交互"""
        if user_id not in self.user_item_matrix:
            self.user_item_matrix[user_id] = {}
        self.user_item_matrix[user_id][video_id] = rating

    def _calculate_user_similarity(self, user_i: str, user_j: str) -> float:
        """计算两个用户的相似度（基于Cosine）"""
        # 检查缓存
        cache_key = (min(user_i, user_j), max(user_i, user_j))
        if cache_key in self.similarity_cache:
            return self.similarity_cache[cache_key]

        if user_i not in self.user_item_matrix or user_j not in self.user_item_matrix:
            return 0.0

        items_i = set(self.user_item_matrix[user_i].keys())
        items_j = set(self.user_item_matrix[user_j].keys())

        # 找出共同交互的项目
        common_items = items_i & items_j

        if len(common_items) == 0:
            similarity = 0.0
        else:
            # 计算向量
            ratings_i = np.array([self.user_item_matrix[user_i][item] for item in common_items])
            ratings_j = np.array([self.user_item_matrix[user_j][item] for item in common_items])

            # Cosine相似度
            dot_product = np.dot(ratings_i, ratings_j)
            magnitude_i = np.sqrt(np.sum(ratings_i ** 2))
            magnitude_j = np.sqrt(np.sum(ratings_j ** 2))

            if magnitude_i > 0 and magnitude_j > 0:
                similarity = dot_product / (magnitude_i * magnitude_j)
            else:
                similarity = 0.0

        self.similarity_cache[cache_key] = similarity
        return similarity

    def recommend(self, user_id: str, k: int = 10, n_similar_users: int = 10) -> List[Tuple[str, float]]:
        """
        基于用户的协同过滤推荐

        Args:
            user_id: 用户ID
            k: 推荐数量
            n_similar_users: 考虑的相似用户数量

        Returns:
            [(video_id, score), ...]
        """
        if user_id not in self.user_item_matrix:
            return []

        # 获取用户已交互的项目
        user_items = set(self.user_item_matrix[user_id].keys())

        # 找出相似用户
        similarities = []
        for other_user in self.user_item_matrix:
            if other_user != user_id:
                sim = self._calculate_user_similarity(user_id, other_user)
                if sim > self.similarity_threshold:
                    similarities.append((other_user, sim))

        # 按相似度排序
        similarities.sort(key=lambda x: x[1], reverse=True)
        similar_users = similarities[:n_similar_users]

        if not similar_users:
            return []

        # 计算推荐分数
        scores = defaultdict(float)
        for similar_user, similarity in similar_users:
            for item, rating in self.user_item_matrix[similar_user].items():
                if item not in user_items:
                    scores[item] += similarity * rating

        # 排序并返回
        recommendations = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return recommendations[:k]


class ContentBasedRecommender:
    """基于内容的推荐"""

    def __init__(self):
        """初始化基于内容的推荐器"""
        self.video_features = {}  # video_id -> feature_vector
        self.feature_index = {}

    def add_video(self, video_id: str, features: Dict[str, float]):
        """
        添加视频特征

        Args:
            video_id: 视频ID
            features: 特征字典 {feature_name: value}
        """
        self.video_features[video_id] = features

    def _calculate_similarity(self, features_1: Dict, features_2: Dict) -> float:
        """计算两个特征向量的余弦相似度"""
        # 获取所有特征键
        all_keys = set(features_1.keys()) | set(features_2.keys())

        if not all_keys:
            return 0.0

        # 构建向量
        vec1 = np.array([features_1.get(key, 0.0) for key in all_keys])
        vec2 = np.array([features_2.get(key, 0.0) for key in all_keys])

        # Cosine相似度
        dot_product = np.dot(vec1, vec2)
        magnitude_1 = np.sqrt(np.sum(vec1 ** 2))
        magnitude_2 = np.sqrt(np.sum(vec2 ** 2))

        if magnitude_1 > 0 and magnitude_2 > 0:
            return dot_product / (magnitude_1 * magnitude_2)
        else:
            return 0.0

    def recommend(self, video_id: str, k: int = 10) -> List[Tuple[str, float]]:
        """
        基于内容的推荐

        Args:
            video_id: 查询视频ID
            k: 推荐数量

        Returns:
            [(similar_video_id, similarity_score), ...]
        """
        if video_id not in self.video_features:
            return []

        query_features = self.video_features[video_id]
        similarities = []

        for other_video, features in self.video_features.items():
            if other_video != video_id:
                similarity = self._calculate_similarity(query_features, features)
                if similarity > 0:
                    similarities.append((other_video, similarity))

        # 排序并返回
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:k]


class HybridRecommender:
    """混合推荐系统"""

    def __init__(
        self,
        cf_weight: float = 0.40,
        cb_weight: float = 0.35,
        popularity_weight: float = 0.15,
        diversity_weight: float = 0.10
    ):
        """
        初始化混合推荐器

        Args:
            cf_weight: 协同过滤权重
            cb_weight: 内容推荐权重
            popularity_weight: 热度算法权重
            diversity_weight: 多样性权重
        """
        self.cf_weight = cf_weight
        self.cb_weight = cb_weight
        self.popularity_weight = popularity_weight
        self.diversity_weight = diversity_weight

        self.cf = CollaborativeFiltering()
        self.cb = ContentBasedRecommender()
        self.video_stats = {}  # video_id -> {views, likes, shares, ...}

    def add_video_interaction(self, user_id: str, video_id: str, rating: float):
        """添加用户-视频交互"""
        self.cf.add_interaction(user_id, video_id, rating)

    def add_video_features(self, video_id: str, features: Dict[str, float]):
        """添加视频特征"""
        self.cb.add_video(video_id, features)

    def add_video_stats(self, video_id: str, views: int, likes: int, shares: int, comments: int):
        """添加视频统计数据"""
        self.video_stats[video_id] = {
            'views': views,
            'likes': likes,
            'shares': shares,
            'comments': comments
        }

    def _calculate_popularity_score(self, video_id: str) -> float:
        """计算视频的热度评分"""
        if video_id not in self.video_stats:
            return 0.5

        stats = self.video_stats[video_id]
        views = stats.get('views', 1)
        likes = stats.get('likes', 0)
        shares = stats.get('shares', 0)
        comments = stats.get('comments', 0)

        # 权重化热度分数
        score = (
            math.log(views + 1) / 20 * 0.5 +  # 浏览数
            likes / (views + 1) * 0.3 +         # 点赞率
            (shares + comments) / (views + 1) * 0.2  # 互动率
        )

        return min(score, 1.0)

    def _calculate_diversity_penalty(self, recommendations: List[Dict], recommended_ids: Set[str]) -> float:
        """计算多样性惩罚（避免推荐相似视频）"""
        if not recommended_ids:
            return 1.0

        # 检查与已推荐视频的相似度
        penalty = 1.0
        for rec in recommendations:
            for rec_id in recommended_ids:
                # 这里简化处理，实际应计算特征相似度
                if rec['video_id'] == rec_id:
                    penalty -= 0.2

        return max(penalty, 0.5)

    def recommend(
        self,
        user_id: str,
        k: int = 10,
        consider_cf: bool = True,
        consider_cb: bool = True,
        seed_video_id: Optional[str] = None
    ) -> List[RecommendationItem]:
        """
        混合推荐

        Args:
            user_id: 用户ID
            k: 推荐数量
            consider_cf: 是否使用协同过滤
            consider_cb: 是否使用内容推荐
            seed_video_id: 种子视频ID（用于内容推荐）

        Returns:
            推荐项目列表
        """
        recommendation_scores = defaultdict(lambda: {'cf': 0, 'cb': 0, 'pop': 0})

        # 协同过滤推荐
        if consider_cf:
            cf_recommendations = self.cf.recommend(user_id, k=k*2)
            for video_id, score in cf_recommendations:
                recommendation_scores[video_id]['cf'] = score

        # 基于内容的推荐
        if consider_cb and seed_video_id:
            cb_recommendations = self.cb.recommend(seed_video_id, k=k*2)
            for video_id, score in cb_recommendations:
                recommendation_scores[video_id]['cb'] = score

        # 热度评分
        for video_id in recommendation_scores:
            recommendation_scores[video_id]['pop'] = self._calculate_popularity_score(video_id)

        # 计算最终分数
        final_recommendations = []
        recommended_ids = set()

        for video_id, scores in recommendation_scores.items():
            # 加权综合
            final_score = (
                scores['cf'] * self.cf_weight +
                scores['cb'] * self.cb_weight +
                scores['pop'] * self.popularity_weight
            )

            # 应用多样性惩罚
            diversity_penalty = self._calculate_diversity_penalty(final_recommendations, recommended_ids)
            final_score *= diversity_penalty

            # 确定推荐原因
            reasons = []
            if scores['cf'] > 0.3:
                reasons.append("基于相似用户的推荐")
            if scores['cb'] > 0.3:
                reasons.append("内容相似")
            if scores['pop'] > 0.3:
                reasons.append("热门内容")

            reason = "，".join(reasons) or "算法推荐"

            final_recommendations.append(RecommendationItem(
                video_id=video_id,
                score=final_score,
                reason=reason,
                cf_score=scores['cf'],
                cb_score=scores['cb'],
                popularity_score=scores['pop']
            ))

            recommended_ids.add(video_id)

        # 排序并返回Top-K
        final_recommendations.sort(key=lambda x: x.score, reverse=True)
        return final_recommendations[:k]

    def get_recommendations_for_exploration(self, k: int = 10) -> List[Tuple[str, float]]:
        """
        获取探索性推荐（多样性）

        Args:
            k: 推荐数量

        Returns:
            视频ID和分数列表
        """
        # 按热度排序，推荐中等热度的视频（避免过度推荐热点）
        recommendations = []
        for video_id, stats in self.video_stats.items():
            pop_score = self._calculate_popularity_score(video_id)
            # 偏好中等热度视频（0.3-0.7范围）
            if 0.3 <= pop_score <= 0.7:
                recommendations.append((video_id, pop_score))

        recommendations.sort(key=lambda x: x[1], reverse=True)
        return recommendations[:k]


if __name__ == "__main__":
    print("推荐引擎模块已加载")

    # 示例使用
    recommender = HybridRecommender()

    # 添加用户交互数据
    recommender.add_video_interaction("user1", "video1", 0.8)
    recommender.add_video_interaction("user1", "video2", 0.7)
    recommender.add_video_interaction("user2", "video1", 0.9)
    recommender.add_video_interaction("user2", "video3", 0.6)

    # 添加视频特征
    recommender.add_video_features("video1", {"ai": 0.9, "tech": 0.8})
    recommender.add_video_features("video2", {"gaming": 0.8, "ai": 0.3})
    recommender.add_video_features("video3", {"ai": 0.7, "tech": 0.9})

    # 添加视频统计
    recommender.add_video_stats("video1", views=100000, likes=5000, shares=500, comments=1000)
    recommender.add_video_stats("video2", views=50000, likes=2000, shares=200, comments=500)
    recommender.add_video_stats("video3", views=30000, likes=1500, shares=150, comments=300)

    # 获取推荐
    recommendations = recommender.recommend("user1", k=5, seed_video_id="video1")
    print("\n推荐结果:")
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec.video_id} (分数: {rec.score:.3f}) - {rec.reason}")
