"""
叙事排序模块

实现智能叙事排序算法，将不连续的视频片段按照逻辑流畅的顺序重新排列。
支持多种排序策略：语义相似度、主题聚类、图算法、混合策略。
"""

from typing import List, Dict, Optional, Tuple, Set
from dataclasses import dataclass
import numpy as np
import re
import logging
from collections import defaultdict

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

try:
    from sklearn.cluster import KMeans
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

try:
    import networkx as nx
    NETWORKX_AVAILABLE = True
except ImportError:
    NETWORKX_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class NarrativeSegment:
    """叙事片段（内部表示）"""
    index: int  # 原始索引
    start: float
    end: float
    text: str
    topic: str
    embedding: Optional[np.ndarray] = None
    keywords: List[str] = None
    relevance_score: float = 0.5
    importance_score: float = 0.5


class NarrativeSorter:
    """叙事排序器"""

    def __init__(
        self,
        strategy: str = "hybrid",  # semantic, topic, graph, hybrid, time
        model_name: str = "paraphrase-multilingual-MiniLM-L12-v2",
        use_cache: bool = True
    ):
        """
        初始化排序器

        Args:
            strategy: 排序策略 ('semantic', 'topic', 'graph', 'hybrid', 'time')
            model_name: sentence-transformers 模型名称
            use_cache: 是否使用缓存
        """
        self.strategy = strategy
        self.use_cache = use_cache
        self.embedding_cache = {}

        # 初始化模型
        if SENTENCE_TRANSFORMERS_AVAILABLE and strategy in ['semantic', 'hybrid', 'graph']:
            try:
                logger.info(f"加载语义模型: {model_name}")
                self.model = SentenceTransformer(model_name)
                logger.info("语义模型加载成功")
            except Exception as e:
                logger.warning(f"加载语义模型失败: {e}，将使用基础排序")
                self.model = None
        else:
            self.model = None
            if strategy in ['semantic', 'hybrid'] and not SENTENCE_TRANSFORMERS_AVAILABLE:
                logger.warning("sentence-transformers 未安装，将使用基础排序")

    def sort_segments(
        self,
        segments: List,  # List[KeySegment]
        preserve_order: bool = False,
        max_gap: float = 60.0  # 最大时间跳跃（秒）
    ) -> List:
        """
        排序片段

        Args:
            segments: 片段列表（KeySegment 对象）
            preserve_order: 是否部分保持原始顺序
            max_gap: 允许的最大时间跳跃（秒）

        Returns:
            排序后的片段列表
        """
        if not segments:
            return segments

        if len(segments) <= 1:
            return segments

        logger.info(f"使用 {self.strategy} 策略排序 {len(segments)} 个片段")

        # 转换为内部表示
        narrative_segments = self._convert_to_narrative_segments(segments)

        # 根据策略选择排序方法
        if self.strategy == "semantic":
            sorted_segments = self._semantic_sort(narrative_segments, max_gap)
        elif self.strategy == "topic":
            sorted_segments = self._topic_sort(narrative_segments)
        elif self.strategy == "graph":
            sorted_segments = self._graph_sort(narrative_segments, max_gap)
        elif self.strategy == "time":
            sorted_segments = self._time_sort(narrative_segments)
        elif self.strategy == "hybrid":
            sorted_segments = self._hybrid_sort(narrative_segments, max_gap)
        else:
            logger.warning(f"未知策略 {self.strategy}，使用时间排序")
            sorted_segments = self._time_sort(narrative_segments)

        # 如果需要保持部分原始顺序
        if preserve_order:
            sorted_segments = self._preserve_partial_order(
                narrative_segments,
                sorted_segments
            )

        # 转换回原始格式
        result = [segments[seg.index] for seg in sorted_segments]

        logger.info("排序完成")
        return result

    def _convert_to_narrative_segments(self, segments: List) -> List[NarrativeSegment]:
        """转换为内部叙事片段格式"""
        narrative_segments = []

        for i, seg in enumerate(segments):
            narrative_seg = NarrativeSegment(
                index=i,
                start=seg.start,
                end=seg.end,
                text=seg.text,
                topic=seg.topic,
                keywords=seg.keywords if hasattr(seg, 'keywords') else [],
                relevance_score=seg.relevance_score if hasattr(seg, 'relevance_score') else 0.5,
                importance_score=seg.importance_score if hasattr(seg, 'importance_score') else 0.5
            )
            narrative_segments.append(narrative_seg)

        return narrative_segments

    def _time_sort(self, segments: List[NarrativeSegment]) -> List[NarrativeSegment]:
        """按时间排序（基准方法）"""
        return sorted(segments, key=lambda x: x.start)

    def _semantic_sort(
        self,
        segments: List[NarrativeSegment],
        max_gap: float = 60.0
    ) -> List[NarrativeSegment]:
        """
        基于语义相似度排序
        使用贪心算法找到最优排序，最小化相邻片段的语义距离
        """
        if not self.model:
            logger.warning("语义模型不可用，使用时间排序")
            return self._time_sort(segments)

        # 计算嵌入
        embeddings = self._compute_embeddings(segments)

        # 计算相似度矩阵
        similarity_matrix = self._compute_similarity_matrix(embeddings)

        # 贪心算法构建最优路径
        sorted_segments = self._greedy_path(
            segments,
            similarity_matrix,
            max_gap
        )

        return sorted_segments

    def _topic_sort(self, segments: List[NarrativeSegment]) -> List[NarrativeSegment]:
        """
        基于主题聚类排序
        1. 按主题分组片段
        2. 组内按时间或重要性排序
        3. 组间按逻辑顺序连接
        """
        # 按主题分组
        topic_groups = defaultdict(list)
        for seg in segments:
            topic_groups[seg.topic].append(seg)

        # 组内排序（按时间）
        for topic in topic_groups:
            topic_groups[topic].sort(key=lambda x: x.start)

        # 组间排序（按第一个片段的重要性）
        sorted_topics = sorted(
            topic_groups.items(),
            key=lambda x: sum(s.importance_score for s in x[1]) / len(x[1]),
            reverse=True
        )

        # 合并结果
        result = []
        for topic, group_segments in sorted_topics:
            result.extend(group_segments)

        return result

    def _graph_sort(
        self,
        segments: List[NarrativeSegment],
        max_gap: float = 60.0
    ) -> List[NarrativeSegment]:
        """
        基于图算法排序
        1. 构建片段关系图
        2. 使用最短路径算法找最佳顺序
        3. 权重基于语义相似度和时间距离
        """
        if not NETWORKX_AVAILABLE:
            logger.warning("networkx 未安装，使用语义排序")
            return self._semantic_sort(segments, max_gap)

        if not self.model:
            logger.warning("语义模型不可用，使用主题排序")
            return self._topic_sort(segments)

        # 计算嵌入和相似度矩阵
        embeddings = self._compute_embeddings(segments)
        similarity_matrix = self._compute_similarity_matrix(embeddings)

        # 构建有向图
        G = nx.DiGraph()

        # 添加节点
        for i, seg in enumerate(segments):
            G.add_node(i, segment=seg)

        # 添加边（权重 = 语义距离 + 时间惩罚）
        for i in range(len(segments)):
            for j in range(len(segments)):
                if i == j:
                    continue

                # 语义距离（1 - 相似度）
                semantic_distance = 1 - similarity_matrix[i, j]

                # 时间距离惩罚
                time_gap = abs(segments[j].start - segments[i].end)
                time_penalty = min(time_gap / max_gap, 1.0) * 0.3

                # 总权重
                weight = semantic_distance + time_penalty

                G.add_edge(i, j, weight=weight)

        # 使用最短路径算法（从重要性最高的片段开始）
        start_idx = max(range(len(segments)), key=lambda i: segments[i].importance_score)

        try:
            # 使用贪心策略构建路径
            sorted_indices = self._graph_greedy_path(G, start_idx, len(segments))
            sorted_segments = [segments[i] for i in sorted_indices]
        except Exception as e:
            logger.warning(f"图算法失败: {e}，使用语义排序")
            sorted_segments = self._semantic_sort(segments, max_gap)

        return sorted_segments

    def _hybrid_sort(
        self,
        segments: List[NarrativeSegment],
        max_gap: float = 60.0
    ) -> List[NarrativeSegment]:
        """
        混合排序策略
        综合考虑：语义相似度、主题连贯性、时间顺序、因果关系
        """
        if not self.model:
            logger.warning("语义模型不可用，使用主题排序")
            return self._topic_sort(segments)

        # 1. 计算语义嵌入和相似度
        embeddings = self._compute_embeddings(segments)
        similarity_matrix = self._compute_similarity_matrix(embeddings)

        # 2. 检测因果关系
        causal_relations = self._detect_causal_relations(segments)

        # 3. 构建综合评分矩阵
        score_matrix = np.zeros((len(segments), len(segments)))

        for i in range(len(segments)):
            for j in range(len(segments)):
                if i == j:
                    continue

                # 语义相似度得分（40%）
                semantic_score = similarity_matrix[i, j] * 0.4

                # 主题连贯性得分（25%）
                topic_score = 0.25 if segments[i].topic == segments[j].topic else 0

                # 时间顺序得分（20%）
                time_score = 0
                if segments[j].start > segments[i].end:
                    time_gap = segments[j].start - segments[i].end
                    if time_gap <= max_gap:
                        time_score = 0.2 * (1 - time_gap / max_gap)

                # 因果关系得分（15%）
                causal_score = 0.15 if j in causal_relations.get(i, []) else 0

                # 综合得分
                score_matrix[i, j] = semantic_score + topic_score + time_score + causal_score

        # 4. 使用贪心算法构建最优路径
        sorted_segments = self._greedy_path_with_scores(segments, score_matrix)

        return sorted_segments

    def _compute_embeddings(self, segments: List[NarrativeSegment]) -> np.ndarray:
        """计算片段嵌入"""
        if not self.model:
            return np.random.rand(len(segments), 384)  # 降级方案

        embeddings = []

        for seg in segments:
            # 检查缓存
            cache_key = hash(seg.text[:500])  # 使用前500字符作为key

            if self.use_cache and cache_key in self.embedding_cache:
                embedding = self.embedding_cache[cache_key]
            else:
                # 使用文本+主题生成嵌入
                text_for_embedding = f"{seg.topic}: {seg.text}"
                embedding = self.model.encode(text_for_embedding, convert_to_numpy=True)

                if self.use_cache:
                    self.embedding_cache[cache_key] = embedding

            embeddings.append(embedding)

        return np.array(embeddings)

    def _compute_similarity_matrix(self, embeddings: np.ndarray) -> np.ndarray:
        """计算相似度矩阵"""
        if SKLEARN_AVAILABLE:
            return cosine_similarity(embeddings)
        else:
            # 手动计算余弦相似度
            norm = np.linalg.norm(embeddings, axis=1, keepdims=True)
            normalized = embeddings / (norm + 1e-8)
            return np.dot(normalized, normalized.T)

    def _greedy_path(
        self,
        segments: List[NarrativeSegment],
        similarity_matrix: np.ndarray,
        max_gap: float
    ) -> List[NarrativeSegment]:
        """
        贪心算法构建路径
        从重要性最高的片段开始，每次选择与当前片段最相似的未访问片段
        """
        n = len(segments)
        visited = [False] * n
        path = []

        # 从重要性最高的片段开始
        current = max(range(n), key=lambda i: segments[i].importance_score)
        path.append(current)
        visited[current] = True

        # 贪心选择
        while len(path) < n:
            best_next = -1
            best_score = -1

            for i in range(n):
                if visited[i]:
                    continue

                # 计算得分（相似度 - 时间惩罚）
                similarity = similarity_matrix[current, i]
                time_gap = abs(segments[i].start - segments[current].end)
                time_penalty = min(time_gap / max_gap, 1.0) * 0.3

                score = similarity - time_penalty

                if score > best_score:
                    best_score = score
                    best_next = i

            if best_next == -1:
                # 选择任意未访问的片段
                best_next = next(i for i in range(n) if not visited[i])

            path.append(best_next)
            visited[best_next] = True
            current = best_next

        return [segments[i] for i in path]

    def _greedy_path_with_scores(
        self,
        segments: List[NarrativeSegment],
        score_matrix: np.ndarray
    ) -> List[NarrativeSegment]:
        """使用综合评分矩阵的贪心路径算法"""
        n = len(segments)
        visited = [False] * n
        path = []

        # 从重要性最高的片段开始
        current = max(range(n), key=lambda i: segments[i].importance_score)
        path.append(current)
        visited[current] = True

        # 贪心选择
        while len(path) < n:
            best_next = -1
            best_score = -1

            for i in range(n):
                if visited[i]:
                    continue

                score = score_matrix[current, i]

                if score > best_score:
                    best_score = score
                    best_next = i

            if best_next == -1:
                # 选择任意未访问的片段
                best_next = next(i for i in range(n) if not visited[i])

            path.append(best_next)
            visited[best_next] = True
            current = best_next

        return [segments[i] for i in path]

    def _graph_greedy_path(
        self,
        G: 'nx.DiGraph',
        start: int,
        num_nodes: int
    ) -> List[int]:
        """图中的贪心路径"""
        visited = set([start])
        path = [start]
        current = start

        while len(path) < num_nodes:
            # 找到权重最小的未访问邻居
            neighbors = [
                (n, G[current][n]['weight'])
                for n in G[current]
                if n not in visited
            ]

            if not neighbors:
                # 没有未访问的邻居，选择任意未访问节点
                unvisited = [n for n in G.nodes() if n not in visited]
                if unvisited:
                    next_node = unvisited[0]
                else:
                    break
            else:
                # 选择权重最小的邻居
                next_node = min(neighbors, key=lambda x: x[1])[0]

            path.append(next_node)
            visited.add(next_node)
            current = next_node

        return path

    def _detect_causal_relations(
        self,
        segments: List[NarrativeSegment]
    ) -> Dict[int, List[int]]:
        """
        检测因果关系
        识别"因此"、"所以"、"由于"、"导致"等关键词
        """
        causal_relations = defaultdict(list)

        # 因果关系关键词
        causal_keywords = {
            'zh': ['因此', '所以', '因为', '由于', '导致', '造成', '结果', '从而'],
            'en': ['therefore', 'thus', 'because', 'since', 'as a result', 'consequently', 'hence']
        }

        all_keywords = causal_keywords['zh'] + causal_keywords['en']

        for i, seg in enumerate(segments):
            text_lower = seg.text.lower()

            # 检查是否包含因果关键词
            has_causal = any(keyword in text_lower for keyword in all_keywords)

            if has_causal:
                # 可能与前一个片段有因果关系
                if i > 0:
                    causal_relations[i-1].append(i)

                # 也可能引出后续片段
                if i < len(segments) - 1:
                    # 检查关键词位置
                    for keyword in all_keywords:
                        if keyword in text_lower:
                            pos = text_lower.find(keyword)
                            # 如果关键词在后半部分，可能引出下一个片段
                            if pos > len(text_lower) / 2:
                                causal_relations[i].append(i+1)
                                break

        return dict(causal_relations)

    def _preserve_partial_order(
        self,
        original: List[NarrativeSegment],
        sorted_segments: List[NarrativeSegment]
    ) -> List[NarrativeSegment]:
        """保持部分原始顺序"""
        # 简单实现：对于时间上非常接近的片段，保持原始顺序
        result = []
        time_threshold = 30.0  # 30秒内的片段保持原始顺序

        # 按时间分组
        groups = []
        current_group = [sorted_segments[0]]

        for i in range(1, len(sorted_segments)):
            if sorted_segments[i].start - current_group[-1].end <= time_threshold:
                current_group.append(sorted_segments[i])
            else:
                groups.append(current_group)
                current_group = [sorted_segments[i]]

        groups.append(current_group)

        # 组内按原始顺序排序
        for group in groups:
            group.sort(key=lambda x: x.index)
            result.extend(group)

        return result

    def evaluate_coherence(self, segments: List) -> float:
        """
        评估叙事连贯性（0-1）
        综合考虑：语义流畅性、主题一致性、时间连续性
        """
        if not segments or len(segments) <= 1:
            return 1.0

        # 转换为内部表示
        narrative_segments = self._convert_to_narrative_segments(segments)

        # 1. 语义流畅性（相邻片段的语义相似度）
        semantic_score = 0.0
        if self.model:
            embeddings = self._compute_embeddings(narrative_segments)
            similarity_matrix = self._compute_similarity_matrix(embeddings)

            for i in range(len(narrative_segments) - 1):
                semantic_score += similarity_matrix[i, i+1]

            semantic_score /= (len(narrative_segments) - 1)
        else:
            semantic_score = 0.5  # 默认值

        # 2. 主题一致性（相邻片段主题相同的比例）
        topic_score = 0.0
        for i in range(len(narrative_segments) - 1):
            if narrative_segments[i].topic == narrative_segments[i+1].topic:
                topic_score += 1

        topic_score /= (len(narrative_segments) - 1)

        # 3. 时间连续性（时间跳跃的平滑度）
        time_score = 0.0
        max_gap = 60.0

        for i in range(len(narrative_segments) - 1):
            gap = narrative_segments[i+1].start - narrative_segments[i].end
            if gap < 0:
                # 时间重叠，扣分
                time_score += 0.3
            elif gap <= max_gap:
                # 合理的时间间隔
                time_score += 1.0 - (gap / max_gap) * 0.3
            else:
                # 时间跳跃过大
                time_score += 0.5

        time_score /= (len(narrative_segments) - 1)

        # 4. 因果关系连贯性
        causal_relations = self._detect_causal_relations(narrative_segments)
        causal_score = 0.0

        for i in range(len(narrative_segments) - 1):
            if i+1 in causal_relations.get(i, []):
                causal_score += 1

        if len(narrative_segments) > 1:
            causal_score /= (len(narrative_segments) - 1)

        # 综合评分（语义40%、主题30%、时间20%、因果10%）
        coherence = (
            semantic_score * 0.4 +
            topic_score * 0.3 +
            time_score * 0.2 +
            causal_score * 0.1
        )

        return min(coherence, 1.0)

    def compare_strategies(
        self,
        segments: List,
        strategies: Optional[List[str]] = None
    ) -> Dict[str, Dict]:
        """
        比较不同排序策略的效果

        Args:
            segments: 片段列表
            strategies: 要比较的策略列表（默认：全部）

        Returns:
            每个策略的结果和评分
        """
        if strategies is None:
            strategies = ['time', 'semantic', 'topic', 'graph', 'hybrid']

        results = {}

        for strategy in strategies:
            logger.info(f"测试策略: {strategy}")

            # 临时切换策略
            original_strategy = self.strategy
            self.strategy = strategy

            try:
                # 排序
                sorted_segments = self.sort_segments(segments.copy())

                # 评估
                coherence = self.evaluate_coherence(sorted_segments)

                results[strategy] = {
                    'sorted_segments': sorted_segments,
                    'coherence_score': coherence,
                    'strategy': strategy
                }

                logger.info(f"  连贯性评分: {coherence:.3f}")

            except Exception as e:
                logger.error(f"策略 {strategy} 失败: {e}")
                results[strategy] = {
                    'error': str(e),
                    'coherence_score': 0.0
                }

            # 恢复原始策略
            self.strategy = original_strategy

        return results


if __name__ == "__main__":
    # 测试代码
    print("NarrativeSorter 模块已加载")
    print(f"sentence-transformers 可用: {SENTENCE_TRANSFORMERS_AVAILABLE}")
    print(f"scikit-learn 可用: {SKLEARN_AVAILABLE}")
    print(f"networkx 可用: {NETWORKX_AVAILABLE}")
