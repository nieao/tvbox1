"""
叙事排序演示脚本

演示不同排序策略的效果，比较连贯性评分，可视化片段顺序变化。
"""

import sys
import os
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.narrative_sorter import NarrativeSorter
from src.core.analyzer import KeySegment


def create_sample_segments():
    """创建示例片段用于测试"""
    segments = [
        KeySegment(
            start=0.0,
            end=30.0,
            text="今天我要介绍人工智能的基础知识。人工智能是计算机科学的一个重要分支。",
            topic="人工智能基础",
            relevance_score=0.9,
            importance_score=0.85,
            keywords=["人工智能", "基础", "计算机"]
        ),
        KeySegment(
            start=120.0,
            end=150.0,
            text="因此，深度学习成为了人工智能的核心技术。它使用神经网络来模拟人脑的学习过程。",
            topic="深度学习",
            relevance_score=0.88,
            importance_score=0.9,
            keywords=["深度学习", "神经网络", "学习"]
        ),
        KeySegment(
            start=30.0,
            end=60.0,
            text="机器学习是人工智能的一个子领域。通过算法让计算机从数据中学习。",
            topic="机器学习",
            relevance_score=0.87,
            importance_score=0.88,
            keywords=["机器学习", "算法", "数据"]
        ),
        KeySegment(
            start=200.0,
            end=230.0,
            text="在实际应用中，我们需要大量的数据来训练模型。数据质量直接影响模型性能。",
            topic="数据处理",
            relevance_score=0.75,
            importance_score=0.7,
            keywords=["数据", "训练", "模型"]
        ),
        KeySegment(
            start=60.0,
            end=90.0,
            text="监督学习是机器学习的一种重要方法。它需要标注的数据来训练模型。",
            topic="监督学习",
            relevance_score=0.8,
            importance_score=0.75,
            keywords=["监督学习", "标注", "训练"]
        ),
        KeySegment(
            start=300.0,
            end=330.0,
            text="最后，让我们总结一下今天学习的内容。人工智能的发展离不开这些基础技术。",
            topic="总结",
            relevance_score=0.85,
            importance_score=0.8,
            keywords=["总结", "人工智能", "技术"]
        ),
        KeySegment(
            start=150.0,
            end=180.0,
            text="卷积神经网络特别适合处理图像数据。因此在计算机视觉领域广泛应用。",
            topic="计算机视觉",
            relevance_score=0.82,
            importance_score=0.78,
            keywords=["CNN", "图像", "计算机视觉"]
        ),
        KeySegment(
            start=90.0,
            end=120.0,
            text="无监督学习则不需要标注数据。它可以自动发现数据中的模式和结构。",
            topic="无监督学习",
            relevance_score=0.78,
            importance_score=0.73,
            keywords=["无监督学习", "模式", "结构"]
        )
    ]

    return segments


def visualize_segment_order(segments_dict, title="片段顺序对比"):
    """可视化不同策略的片段顺序"""
    fig, axes = plt.subplots(len(segments_dict), 1, figsize=(12, len(segments_dict) * 2))

    if len(segments_dict) == 1:
        axes = [axes]

    colors = plt.cm.Set3(np.linspace(0, 1, 10))

    for idx, (strategy, segments) in enumerate(segments_dict.items()):
        ax = axes[idx]

        # 绘制片段时间线
        for i, seg in enumerate(segments):
            # 使用主题作为颜色标识
            topic_hash = hash(seg.topic) % len(colors)
            color = colors[topic_hash]

            ax.barh(i, seg.end - seg.start, left=seg.start,
                   color=color, alpha=0.7, edgecolor='black')

            # 添加主题标签
            ax.text(seg.start + (seg.end - seg.start) / 2, i,
                   f"{seg.topic[:8]}...", ha='center', va='center',
                   fontsize=8, weight='bold')

        ax.set_xlabel('时间 (秒)')
        ax.set_ylabel('片段索引')
        ax.set_title(f'{strategy} 策略')
        ax.set_yticks(range(len(segments)))
        ax.set_yticklabels([f'片段 {i+1}' for i in range(len(segments))])
        ax.grid(axis='x', alpha=0.3)

    plt.tight_layout()
    plt.savefig('narrative_order_comparison.png', dpi=150, bbox_inches='tight')
    print(f"\n可视化结果已保存: narrative_order_comparison.png")
    plt.close()


def visualize_coherence_scores(results):
    """可视化连贯性评分"""
    strategies = list(results.keys())
    scores = [results[s]['coherence_score'] for s in strategies]

    fig, ax = plt.subplots(figsize=(10, 6))

    bars = ax.bar(strategies, scores, color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8'])

    # 添加数值标签
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
               f'{height:.3f}',
               ha='center', va='bottom', fontweight='bold')

    ax.set_ylabel('连贯性评分', fontsize=12, fontweight='bold')
    ax.set_xlabel('排序策略', fontsize=12, fontweight='bold')
    ax.set_title('不同排序策略的连贯性评分对比', fontsize=14, fontweight='bold')
    ax.set_ylim(0, 1.0)
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    plt.savefig('coherence_scores.png', dpi=150, bbox_inches='tight')
    print(f"连贯性评分图已保存: coherence_scores.png")
    plt.close()


def print_segment_details(segments, strategy_name):
    """打印片段详细信息"""
    print(f"\n{'='*80}")
    print(f"{strategy_name} 策略 - 片段详情")
    print(f"{'='*80}")

    for i, seg in enumerate(segments, 1):
        print(f"\n片段 {i}:")
        print(f"  时间: {seg.start:.1f}s - {seg.end:.1f}s (时长: {seg.end - seg.start:.1f}s)")
        print(f"  主题: {seg.topic}")
        print(f"  文本: {seg.text[:80]}...")
        print(f"  相关性: {seg.relevance_score:.2f} | 重要性: {seg.importance_score:.2f}")
        print(f"  关键词: {', '.join(seg.keywords[:5])}")


def analyze_time_jumps(segments, strategy_name):
    """分析时间跳跃情况"""
    print(f"\n{strategy_name} - 时间跳跃分析:")

    total_jump = 0
    max_jump = 0
    jump_count = 0

    for i in range(len(segments) - 1):
        gap = segments[i+1].start - segments[i].end

        if gap < 0:
            print(f"  片段 {i+1} -> {i+2}: 时间重叠 {abs(gap):.1f}s")
        elif gap > 30:
            print(f"  片段 {i+1} -> {i+2}: 时间跳跃 {gap:.1f}s")
            total_jump += gap
            max_jump = max(max_jump, gap)
            jump_count += 1

    if jump_count > 0:
        print(f"  总跳跃次数: {jump_count}")
        print(f"  平均跳跃: {total_jump / jump_count:.1f}s")
        print(f"  最大跳跃: {max_jump:.1f}s")
    else:
        print(f"  无明显时间跳跃")


def analyze_topic_transitions(segments, strategy_name):
    """分析主题转换情况"""
    print(f"\n{strategy_name} - 主题转换分析:")

    topic_changes = 0
    for i in range(len(segments) - 1):
        if segments[i].topic != segments[i+1].topic:
            topic_changes += 1
            print(f"  片段 {i+1} -> {i+2}: {segments[i].topic} → {segments[i+1].topic}")

    print(f"  主题转换次数: {topic_changes}/{len(segments)-1}")
    continuity_ratio = 1 - (topic_changes / max(len(segments) - 1, 1))
    print(f"  主题连续性: {continuity_ratio:.2%}")


def run_comparison_demo():
    """运行对比演示"""
    print("\n" + "="*80)
    print("叙事排序算法演示".center(80))
    print("="*80)

    # 创建示例片段
    print("\n1. 创建示例片段...")
    segments = create_sample_segments()
    print(f"   创建了 {len(segments)} 个示例片段")

    # 打印原始片段信息
    print_segment_details(segments, "原始顺序")

    # 创建排序器
    print("\n2. 初始化叙事排序器...")
    sorter = NarrativeSorter(strategy="hybrid")

    # 比较不同策略
    print("\n3. 比较不同排序策略...")
    strategies = ['time', 'semantic', 'topic', 'graph', 'hybrid']
    results = sorter.compare_strategies(segments.copy(), strategies)

    # 打印结果摘要
    print("\n" + "="*80)
    print("排序结果摘要".center(80))
    print("="*80)

    segments_dict = {}

    for strategy, result in results.items():
        if 'error' in result:
            print(f"\n{strategy} 策略: 失败 - {result['error']}")
            continue

        coherence = result['coherence_score']
        sorted_segs = result['sorted_segments']

        print(f"\n{strategy.upper()} 策略:")
        print(f"  连贯性评分: {coherence:.3f}")

        # 保存用于可视化
        segments_dict[strategy] = sorted_segs

        # 详细分析
        analyze_time_jumps(sorted_segs, strategy)
        analyze_topic_transitions(sorted_segs, strategy)

    # 可视化
    print("\n4. 生成可视化图表...")

    try:
        visualize_segment_order(segments_dict)
        visualize_coherence_scores(results)
    except Exception as e:
        print(f"   警告: 可视化失败 - {e}")
        print("   请确保已安装 matplotlib")

    # 最佳策略推荐
    print("\n" + "="*80)
    print("最佳策略推荐".center(80))
    print("="*80)

    best_strategy = max(results.items(), key=lambda x: x[1].get('coherence_score', 0))
    print(f"\n推荐使用: {best_strategy[0].upper()} 策略")
    print(f"连贯性评分: {best_strategy[1]['coherence_score']:.3f}")

    # 打印最佳策略的详细片段
    if 'sorted_segments' in best_strategy[1]:
        print_segment_details(best_strategy[1]['sorted_segments'], best_strategy[0].upper())


def run_single_strategy_demo(strategy='hybrid'):
    """运行单一策略演示"""
    print("\n" + "="*80)
    print(f"{strategy.upper()} 策略详细演示".center(80))
    print("="*80)

    # 创建示例片段
    segments = create_sample_segments()

    # 创建排序器
    sorter = NarrativeSorter(strategy=strategy)

    # 排序前评估
    print("\n排序前:")
    print_segment_details(segments, "原始顺序")
    coherence_before = sorter.evaluate_coherence(segments)
    print(f"\n连贯性评分: {coherence_before:.3f}")
    analyze_time_jumps(segments, "原始顺序")
    analyze_topic_transitions(segments, "原始顺序")

    # 执行排序
    print("\n执行排序...")
    sorted_segments = sorter.sort_segments(segments.copy())

    # 排序后评估
    print("\n排序后:")
    print_segment_details(sorted_segments, strategy.upper())
    coherence_after = sorter.evaluate_coherence(sorted_segments)
    print(f"\n连贯性评分: {coherence_after:.3f}")
    analyze_time_jumps(sorted_segments, strategy.upper())
    analyze_topic_transitions(sorted_segments, strategy.upper())

    # 改进总结
    improvement = ((coherence_after - coherence_before) / max(coherence_before, 0.01)) * 100
    print("\n" + "="*80)
    print("改进总结".center(80))
    print("="*80)
    print(f"连贯性提升: {improvement:+.1f}%")
    print(f"排序前: {coherence_before:.3f}")
    print(f"排序后: {coherence_after:.3f}")


def run_interactive_demo():
    """运行交互式演示"""
    print("\n" + "="*80)
    print("叙事排序交互式演示".center(80))
    print("="*80)

    print("\n可用的排序策略:")
    print("  1. time      - 时间顺序排序")
    print("  2. semantic  - 语义相似度排序")
    print("  3. topic     - 主题聚类排序")
    print("  4. graph     - 图算法排序")
    print("  5. hybrid    - 混合策略排序（推荐）")
    print("  6. compare   - 比较所有策略")

    choice = input("\n请选择策略 (1-6) 或直接按回车使用 hybrid: ").strip()

    strategy_map = {
        '1': 'time',
        '2': 'semantic',
        '3': 'topic',
        '4': 'graph',
        '5': 'hybrid',
        '6': 'compare',
        '': 'hybrid'
    }

    strategy = strategy_map.get(choice, 'hybrid')

    if strategy == 'compare':
        run_comparison_demo()
    else:
        run_single_strategy_demo(strategy)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='叙事排序演示')
    parser.add_argument('--mode', choices=['compare', 'single', 'interactive'],
                       default='compare', help='演示模式')
    parser.add_argument('--strategy', choices=['time', 'semantic', 'topic', 'graph', 'hybrid'],
                       default='hybrid', help='排序策略（单一模式）')

    args = parser.parse_args()

    try:
        if args.mode == 'compare':
            run_comparison_demo()
        elif args.mode == 'single':
            run_single_strategy_demo(args.strategy)
        else:
            run_interactive_demo()

        print("\n" + "="*80)
        print("演示完成！".center(80))
        print("="*80)

    except KeyboardInterrupt:
        print("\n\n演示已中断")
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
