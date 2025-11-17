"""
叙事排序器单元测试
"""

import sys
import pytest
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.narrative_sorter import NarrativeSorter, NarrativeSegment
from src.core.analyzer import KeySegment


@pytest.fixture
def sample_segments():
    """创建测试用的示例片段"""
    return [
        KeySegment(
            start=0.0,
            end=30.0,
            text="这是第一个片段，介绍AI的基础知识",
            topic="AI基础",
            relevance_score=0.9,
            importance_score=0.85,
            keywords=["AI", "基础", "知识"]
        ),
        KeySegment(
            start=60.0,
            end=90.0,
            text="第二个片段讲解机器学习的概念",
            topic="机器学习",
            relevance_score=0.88,
            importance_score=0.9,
            keywords=["机器学习", "概念"]
        ),
        KeySegment(
            start=30.0,
            end=60.0,
            text="第三个片段是深度学习的介绍",
            topic="深度学习",
            relevance_score=0.87,
            importance_score=0.88,
            keywords=["深度学习", "介绍"]
        )
    ]


class TestNarrativeSorter:
    """叙事排序器测试类"""

    def test_initialization(self):
        """测试初始化"""
        sorter = NarrativeSorter(strategy="hybrid")
        assert sorter.strategy == "hybrid"
        assert sorter.use_cache == True

    def test_time_sort(self, sample_segments):
        """测试时间排序"""
        sorter = NarrativeSorter(strategy="time")
        sorted_segs = sorter.sort_segments(sample_segments)

        # 验证是否按时间排序
        for i in range(len(sorted_segs) - 1):
            assert sorted_segs[i].start <= sorted_segs[i+1].start

    def test_semantic_sort(self, sample_segments):
        """测试语义排序"""
        sorter = NarrativeSorter(strategy="semantic")
        sorted_segs = sorter.sort_segments(sample_segments)

        # 验证返回的片段数量正确
        assert len(sorted_segs) == len(sample_segments)

        # 验证所有片段都被包含
        original_starts = {seg.start for seg in sample_segments}
        sorted_starts = {seg.start for seg in sorted_segs}
        assert original_starts == sorted_starts

    def test_topic_sort(self, sample_segments):
        """测试主题排序"""
        sorter = NarrativeSorter(strategy="topic")
        sorted_segs = sorter.sort_segments(sample_segments)

        # 验证返回的片段数量正确
        assert len(sorted_segs) == len(sample_segments)

    def test_hybrid_sort(self, sample_segments):
        """测试混合排序"""
        sorter = NarrativeSorter(strategy="hybrid")
        sorted_segs = sorter.sort_segments(sample_segments)

        # 验证返回的片段数量正确
        assert len(sorted_segs) == len(sample_segments)

    def test_evaluate_coherence(self, sample_segments):
        """测试连贯性评估"""
        sorter = NarrativeSorter(strategy="hybrid")

        # 计算连贯性
        coherence = sorter.evaluate_coherence(sample_segments)

        # 验证评分在有效范围内
        assert 0.0 <= coherence <= 1.0

    def test_coherence_improvement(self, sample_segments):
        """测试排序后连贯性是否提升"""
        sorter = NarrativeSorter(strategy="hybrid")

        # 排序前的连贯性
        coherence_before = sorter.evaluate_coherence(sample_segments)

        # 排序
        sorted_segs = sorter.sort_segments(sample_segments.copy())

        # 排序后的连贯性
        coherence_after = sorter.evaluate_coherence(sorted_segs)

        # 混合策略应该提升或至少保持连贯性
        assert coherence_after >= coherence_before * 0.9  # 允许10%的容差

    def test_empty_segments(self):
        """测试空片段列表"""
        sorter = NarrativeSorter(strategy="hybrid")
        result = sorter.sort_segments([])
        assert result == []

    def test_single_segment(self, sample_segments):
        """测试单个片段"""
        sorter = NarrativeSorter(strategy="hybrid")
        single_seg = [sample_segments[0]]
        result = sorter.sort_segments(single_seg)
        assert len(result) == 1
        assert result[0] == single_seg[0]

    def test_preserve_order(self, sample_segments):
        """测试部分保持原始顺序"""
        sorter = NarrativeSorter(strategy="hybrid")

        # 不保持顺序
        sorted_no_preserve = sorter.sort_segments(sample_segments.copy(), preserve_order=False)

        # 保持顺序
        sorted_preserve = sorter.sort_segments(sample_segments.copy(), preserve_order=True)

        # 两者可能不同（但不是必须的）
        assert len(sorted_no_preserve) == len(sorted_preserve)

    def test_detect_causal_relations(self, sample_segments):
        """测试因果关系检测"""
        sorter = NarrativeSorter(strategy="hybrid")

        # 添加因果关系关键词
        sample_segments[1].text = "因此，机器学习是AI的重要组成部分"

        narrative_segs = sorter._convert_to_narrative_segments(sample_segments)
        causal_relations = sorter._detect_causal_relations(narrative_segs)

        # 应该检测到因果关系
        assert isinstance(causal_relations, dict)

    def test_compare_strategies(self, sample_segments):
        """测试策略比较"""
        sorter = NarrativeSorter(strategy="hybrid")

        strategies = ['time', 'topic', 'hybrid']
        results = sorter.compare_strategies(sample_segments, strategies)

        # 验证所有策略都有结果
        assert len(results) == len(strategies)

        # 验证每个结果都有连贯性评分
        for strategy, result in results.items():
            if 'error' not in result:
                assert 'coherence_score' in result
                assert 0.0 <= result['coherence_score'] <= 1.0

    def test_max_gap_parameter(self, sample_segments):
        """测试最大时间跳跃参数"""
        sorter = NarrativeSorter(strategy="semantic")

        # 不同的max_gap可能产生不同的结果
        result1 = sorter.sort_segments(sample_segments.copy(), max_gap=30.0)
        result2 = sorter.sort_segments(sample_segments.copy(), max_gap=120.0)

        # 两者应该都返回正确数量的片段
        assert len(result1) == len(sample_segments)
        assert len(result2) == len(sample_segments)

    def test_compute_embeddings(self, sample_segments):
        """测试嵌入计算"""
        sorter = NarrativeSorter(strategy="semantic")
        narrative_segs = sorter._convert_to_narrative_segments(sample_segments)

        embeddings = sorter._compute_embeddings(narrative_segs)

        # 验证嵌入维度
        assert embeddings.shape[0] == len(sample_segments)
        assert embeddings.shape[1] > 0  # 应该有嵌入维度

    def test_compute_similarity_matrix(self, sample_segments):
        """测试相似度矩阵计算"""
        sorter = NarrativeSorter(strategy="semantic")
        narrative_segs = sorter._convert_to_narrative_segments(sample_segments)

        embeddings = sorter._compute_embeddings(narrative_segs)
        similarity_matrix = sorter._compute_similarity_matrix(embeddings)

        # 验证矩阵形状
        n = len(sample_segments)
        assert similarity_matrix.shape == (n, n)

        # 验证对角线为1（自相似度）
        for i in range(n):
            assert abs(similarity_matrix[i, i] - 1.0) < 0.01

        # 验证矩阵对称性
        for i in range(n):
            for j in range(n):
                assert abs(similarity_matrix[i, j] - similarity_matrix[j, i]) < 0.01


class TestIntegration:
    """集成测试"""

    def test_full_pipeline(self, sample_segments):
        """测试完整流程"""
        sorter = NarrativeSorter(strategy="hybrid")

        # 1. 排序
        sorted_segs = sorter.sort_segments(sample_segments.copy())

        # 2. 评估
        coherence = sorter.evaluate_coherence(sorted_segs)

        # 3. 验证结果
        assert len(sorted_segs) == len(sample_segments)
        assert 0.0 <= coherence <= 1.0

    def test_all_strategies(self, sample_segments):
        """测试所有策略"""
        strategies = ['time', 'semantic', 'topic', 'hybrid']

        for strategy in strategies:
            sorter = NarrativeSorter(strategy=strategy)
            sorted_segs = sorter.sort_segments(sample_segments.copy())

            # 验证基本属性
            assert len(sorted_segs) == len(sample_segments)

            # 验证连贯性评分
            coherence = sorter.evaluate_coherence(sorted_segs)
            assert 0.0 <= coherence <= 1.0


def test_performance():
    """性能测试 - 10个片段排序 < 1秒"""
    import time

    # 创建10个片段
    segments = [
        KeySegment(
            start=float(i * 30),
            end=float((i + 1) * 30),
            text=f"这是第 {i+1} 个片段的内容，包含一些描述性文字",
            topic=f"主题{i % 3 + 1}",
            relevance_score=0.8,
            importance_score=0.7,
            keywords=[f"关键词{i}"]
        )
        for i in range(10)
    ]

    sorter = NarrativeSorter(strategy="hybrid")

    # 测量时间
    start_time = time.time()
    sorted_segs = sorter.sort_segments(segments)
    end_time = time.time()

    elapsed = end_time - start_time

    # 验证性能要求
    assert elapsed < 1.0, f"排序耗时 {elapsed:.3f}s，超过 1s 要求"

    # 验证结果正确
    assert len(sorted_segs) == 10


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "-s"])
