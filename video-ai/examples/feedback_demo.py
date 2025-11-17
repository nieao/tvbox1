"""
反馈学习系统演示

演示反馈收集、分析和学习的完整流程。
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
import random
import json

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.services.feedback_learning import (
    FeedbackLearningSystem,
    Feedback,
    FeedbackStats,
    LearningReport
)


def print_section(title: str):
    """打印章节标题"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def simulate_feedback_data(system: FeedbackLearningSystem, num_feedbacks: int = 50):
    """
    模拟用户反馈数据

    Args:
        system: 反馈学习系统
        num_feedbacks: 模拟的反馈数量
    """
    print_section("步骤 1: 模拟用户反馈数据")

    strategies = ["hybrid", "semantic", "temporal", "interest_based"]
    feedback_types = ["segment_quality", "transition_quality", "order_quality", "overall"]
    user_interests_options = [
        ["AI", "编程", "技术"],
        ["教育", "科学", "研究"],
        ["商业", "创业", "管理"],
        ["娱乐", "影视", "游戏"]
    ]

    # 设置不同策略的基础表现（模拟真实场景）
    strategy_base_performance = {
        "hybrid": 4.2,
        "semantic": 3.8,
        "temporal": 3.5,
        "interest_based": 4.0
    }

    print(f"正在生成 {num_feedbacks} 条模拟反馈...")

    for i in range(num_feedbacks):
        # 随机选择策略和类型
        strategy = random.choice(strategies)
        feedback_type = random.choice(feedback_types)
        user_interests = random.choice(user_interests_options)

        # 基于策略的基础性能生成评分（加入随机变化）
        base_rating = strategy_base_performance[strategy]
        rating = max(1.0, min(5.0, base_rating + random.gauss(0, 0.8)))

        # 生成评论（负面反馈有评论）
        comment = None
        if rating <= 2:
            comments = [
                "片段选择不太准确，有些内容不相关",
                "过渡效果太生硬，看起来不自然",
                "视频顺序有点混乱，逻辑不清楚",
                "信息密度太高，节奏太快",
                "保留了太多无关内容"
            ]
            comment = random.choice(comments)
        elif rating >= 4.5:
            comments = [
                "非常满意，片段选择很精准！",
                "过渡效果流畅自然",
                "叙事逻辑清晰连贯",
                "节省了大量时间，内容很有价值",
                "完美符合我的需求"
            ]
            comment = random.choice(comments)

        # 创建反馈
        feedback = Feedback(
            user_id=f"user_{random.randint(1, 20):03d}",
            video_id=f"video_{random.randint(1, 100):04d}",
            feedback_type=feedback_type,
            rating=round(rating, 1),
            comment=comment,
            user_interests=user_interests,
            used_strategy=strategy,
            timestamp=datetime.now() - timedelta(days=random.randint(0, 30)),
            video_metadata={
                'compression_ratio': random.uniform(0.3, 0.7),
                'segments_count': random.randint(5, 15)
            }
        )

        # 收集反馈
        system.collect_feedback(feedback)

        if (i + 1) % 10 == 0:
            print(f"  已生成 {i + 1}/{num_feedbacks} 条反馈...")

    print(f"\n✅ 成功生成 {num_feedbacks} 条反馈数据")
    print(f"   - 策略分布: {', '.join([f'{s}: {sum(1 for f in system.feedbacks if f.used_strategy == s)}' for s in strategies])}")
    print(f"   - 类型分布: {', '.join([f'{t}: {sum(1 for f in system.feedbacks if f.feedback_type == t)}' for t in feedback_types])}")


def analyze_feedback(system: FeedbackLearningSystem):
    """分析反馈数据"""
    print_section("步骤 2: 反馈数据分析")

    # 整体统计
    print("📊 整体统计:")
    stats = system.analyze_feedback()

    print(f"  总反馈数: {stats.total_count}")
    print(f"  平均评分: {stats.average_rating:.2f}/5.0")
    print(f"  正面反馈: {stats.positive_count} ({stats.positive_count/max(stats.total_count, 1):.1%})")
    print(f"  中性反馈: {stats.neutral_count} ({stats.neutral_count/max(stats.total_count, 1):.1%})")
    print(f"  负面反馈: {stats.negative_count} ({stats.negative_count/max(stats.total_count, 1):.1%})")
    print(f"  评分趋势: {stats.trend}")

    # 按策略统计
    print("\n🎯 策略性能分析:")
    if stats.by_strategy:
        sorted_strategies = sorted(stats.by_strategy.items(), key=lambda x: x[1], reverse=True)
        for i, (strategy, rating) in enumerate(sorted_strategies, 1):
            icon = "🏆" if i == 1 else "⭐" if i == 2 else "✅"
            confidence = system.get_strategy_confidence(strategy)
            print(f"  {icon} {strategy:20s} | 评分: {rating:.2f}/5.0 | 置信度: {confidence:.1%}")

    # 按类型统计
    print("\n📈 反馈类型分析:")
    if stats.by_type:
        type_names = {
            'segment_quality': '片段选择',
            'transition_quality': '过渡效果',
            'order_quality': '叙事排序',
            'overall': '整体体验'
        }
        for ftype, rating in sorted(stats.by_type.items(), key=lambda x: x[1], reverse=True):
            status = "✅" if rating >= 4.0 else "⚠️" if rating >= 3.0 else "❌"
            print(f"  {status} {type_names.get(ftype, ftype):15s} | 评分: {rating:.2f}/5.0")


def demonstrate_learning(system: FeedbackLearningSystem):
    """演示学习过程"""
    print_section("步骤 3: 从反馈中学习")

    print("🧠 开始学习过程...")
    report = system.learn_from_feedback(auto_update=True)

    # 最佳策略
    print("\n🏆 最佳策略:")
    if report.best_strategy:
        strategy, rating = report.best_strategy
        print(f"  策略: {strategy}")
        print(f"  平均评分: {rating:.2f}/5.0")
        print(f"  推荐使用场景: 所有场景")

    # 最差策略
    print("\n⚠️ 最差策略:")
    if report.worst_strategy:
        strategy, rating = report.worst_strategy
        print(f"  策略: {strategy}")
        print(f"  平均评分: {rating:.2f}/5.0")
        print(f"  需要改进")

    # 策略排名
    print("\n📊 策略完整排名:")
    for i, (strategy, score) in enumerate(report.strategy_rankings, 1):
        confidence = system.get_strategy_confidence(strategy)
        print(f"  {i}. {strategy:20s} | 性能: {score:.3f} | 置信度: {confidence:.1%}")

    # 负面反馈模式
    print("\n⚠️ 负面反馈模式:")
    if report.negative_patterns:
        for pattern in report.negative_patterns:
            print(f"\n  类型: {pattern['type']}")
            print(f"  数量: {pattern['count']} ({pattern['percentage']:.1f}%)")
            print(f"  平均评分: {pattern['avg_rating']:.2f}/5.0")

            if pattern.get('strategies'):
                print(f"  涉及策略: {', '.join([f'{s}({c})' for s, c in pattern['strategies'].items()])}")

            if pattern.get('common_themes'):
                print(f"  常见问题: {', '.join(pattern['common_themes'][:3])}")
    else:
        print("  ✅ 未发现明显的负面模式")

    # 改进建议
    print("\n💡 改进建议:")
    if report.improvements:
        for i, improvement in enumerate(report.improvements, 1):
            print(f"  {i}. {improvement}")
    else:
        print("  ✅ 当前表现良好，无需特别改进")

    # 推荐
    print("\n🌟 推荐:")
    if report.recommendations:
        for i, rec in enumerate(report.recommendations, 1):
            print(f"  {i}. {rec}")


def demonstrate_strategy_selection(system: FeedbackLearningSystem):
    """演示策略选择"""
    print_section("步骤 4: 智能策略选择")

    # 不同场景下的策略推荐
    scenarios = [
        {
            'name': '编程教程视频',
            'context': {'interests': ['编程', 'AI', '技术'], 'output_length': 'medium'}
        },
        {
            'name': '商业讲座',
            'context': {'interests': ['商业', '创业', '管理'], 'output_length': 'short'}
        },
        {
            'name': '科学纪录片',
            'context': {'interests': ['科学', '教育', '研究'], 'output_length': 'long'}
        },
        {
            'name': '娱乐视频',
            'context': {'interests': ['娱乐', '影视', '游戏'], 'output_length': 'short'}
        }
    ]

    print("为不同场景推荐最佳策略：\n")

    for scenario in scenarios:
        strategy = system.get_best_strategy(scenario['context'])
        confidence = system.get_strategy_confidence(strategy)

        print(f"  📹 {scenario['name']}")
        print(f"     推荐策略: {strategy}")
        print(f"     置信度: {confidence:.1%}")
        print(f"     兴趣标签: {', '.join(scenario['context']['interests'])}")
        print()


def export_learning_report(system: FeedbackLearningSystem):
    """导出学习报告"""
    print_section("步骤 5: 导出学习报告")

    output_dir = project_root / "data" / "reports"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / f"feedback_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    print(f"正在生成报告...")
    report_json = system.export_report(str(output_path))

    print(f"\n✅ 报告已导出:")
    print(f"   文件路径: {output_path}")
    print(f"   文件大小: {len(report_json)} 字节")

    # 显示报告摘要
    report_data = json.loads(report_json)

    print(f"\n📄 报告摘要:")
    print(f"   生成时间: {report_data['generated_at']}")
    print(f"   总反馈数: {report_data['total_feedbacks']}")
    print(f"   策略数量: {len(report_data['strategy_performance'])}")

    if report_data.get('best_strategy'):
        print(f"   最佳策略: {report_data['best_strategy'][0]} ({report_data['best_strategy'][1]:.2f}/5.0)")


def demonstrate_ab_testing(system: FeedbackLearningSystem):
    """演示 A/B 测试"""
    print_section("步骤 6: A/B 测试分析")

    print("比较两个策略的表现:\n")

    # 选择评分最高和最低的两个策略
    if len(system.strategy_performance) >= 2:
        sorted_strategies = sorted(
            system.strategy_performance.items(),
            key=lambda x: x[1],
            reverse=True
        )

        strategy_a = sorted_strategies[0][0]
        strategy_b = sorted_strategies[-1][0]

        # 分析策略A
        stats_a = system.analyze_feedback(strategy=strategy_a)
        print(f"📊 策略 A: {strategy_a}")
        print(f"   总反馈数: {stats_a.total_count}")
        print(f"   平均评分: {stats_a.average_rating:.2f}/5.0")
        print(f"   正面率: {stats_a.positive_count/max(stats_a.total_count, 1):.1%}")
        print(f"   负面率: {stats_a.negative_count/max(stats_a.total_count, 1):.1%}")

        print()

        # 分析策略B
        stats_b = system.analyze_feedback(strategy=strategy_b)
        print(f"📊 策略 B: {strategy_b}")
        print(f"   总反馈数: {stats_b.total_count}")
        print(f"   平均评分: {stats_b.average_rating:.2f}/5.0")
        print(f"   正面率: {stats_b.positive_count/max(stats_b.total_count, 1):.1%}")
        print(f"   负面率: {stats_b.negative_count/max(stats_b.total_count, 1):.1%}")

        # 对比结论
        print(f"\n🎯 A/B 测试结论:")

        rating_diff = stats_a.average_rating - stats_b.average_rating
        if abs(rating_diff) > 0.5:
            winner = strategy_a if rating_diff > 0 else strategy_b
            print(f"   胜出策略: {winner}")
            print(f"   评分优势: {abs(rating_diff):.2f} 分")
            print(f"   建议: 优先使用 {winner} 策略")
        else:
            print(f"   两个策略表现相近（差异: {abs(rating_diff):.2f}分）")
            print(f"   建议: 可以根据具体场景灵活选择")


def demonstrate_continuous_learning(system: FeedbackLearningSystem):
    """演示持续学习"""
    print_section("步骤 7: 持续学习演示")

    print("模拟系统持续学习过程...\n")

    # 初始状态
    initial_stats = system.get_statistics_summary()
    print(f"📊 初始状态:")
    print(f"   平均评分: {initial_stats['average_rating']:.2f}/5.0")
    print(f"   满意度: {initial_stats['positive_rate']:.1%}")
    if initial_stats['top_strategy']:
        print(f"   最佳策略: {initial_stats['top_strategy'][0]}")

    # 模拟新反馈（更高质量）
    print(f"\n📥 收集新一轮反馈（模拟质量改进）...")

    best_strategy = initial_stats['top_strategy'][0] if initial_stats['top_strategy'] else "hybrid"

    for i in range(10):
        feedback = Feedback(
            user_id=f"user_{random.randint(100, 200):03d}",
            video_id=f"video_new_{i:04d}",
            feedback_type="overall",
            rating=round(random.uniform(4.0, 5.0), 1),  # 高质量反馈
            comment="系统改进后效果很好！",
            user_interests=["AI", "技术"],
            used_strategy=best_strategy
        )
        system.collect_feedback(feedback)

    print(f"   已收集 10 条新反馈")

    # 重新学习
    print(f"\n🧠 重新学习...")
    system.learn_from_feedback(auto_update=True)

    # 更新后状态
    updated_stats = system.get_statistics_summary()
    print(f"\n📊 更新后状态:")
    print(f"   平均评分: {updated_stats['average_rating']:.2f}/5.0")
    print(f"   满意度: {updated_stats['positive_rate']:.1%}")
    if updated_stats['top_strategy']:
        print(f"   最佳策略: {updated_stats['top_strategy'][0]}")

    # 对比改进
    print(f"\n📈 改进效果:")
    rating_improvement = updated_stats['average_rating'] - initial_stats['average_rating']
    satisfaction_improvement = updated_stats['positive_rate'] - initial_stats['positive_rate']

    print(f"   评分提升: {rating_improvement:+.2f}")
    print(f"   满意度提升: {satisfaction_improvement:+.1%}")

    if rating_improvement > 0:
        print(f"   ✅ 系统通过学习实现了性能提升！")
    else:
        print(f"   ℹ️ 系统保持稳定表现")


def main():
    """主函数"""
    print("\n" + "="*70)
    print("  📝 反馈学习系统演示")
    print("  Video-AI - 个性化视频编辑")
    print("="*70)

    # 初始化系统
    feedback_dir = project_root / "data" / "feedback_demo"
    feedback_dir.mkdir(parents=True, exist_ok=True)

    system = FeedbackLearningSystem(
        storage_dir=str(feedback_dir),
        learning_rate=0.1,
        min_feedback_count=3
    )

    try:
        # 运行演示流程
        simulate_feedback_data(system, num_feedbacks=50)
        analyze_feedback(system)
        demonstrate_learning(system)
        demonstrate_strategy_selection(system)
        export_learning_report(system)
        demonstrate_ab_testing(system)
        demonstrate_continuous_learning(system)

        # 完成
        print_section("演示完成")
        print("✅ 所有演示步骤已完成！")
        print("\n核心功能:")
        print("  ✓ 反馈收集和存储")
        print("  ✓ 反馈分析和统计")
        print("  ✓ 策略性能评估")
        print("  ✓ 负面模式识别")
        print("  ✓ 改进建议生成")
        print("  ✓ 智能策略选择")
        print("  ✓ A/B 测试支持")
        print("  ✓ 持续学习优化")
        print("\n📁 数据保存位置:")
        print(f"  {feedback_dir}")

        print("\n🚀 下一步:")
        print("  1. 查看生成的反馈数据和报告")
        print("  2. 在 Web UI 中集成反馈功能")
        print("  3. 开始真实用户反馈收集")
        print("  4. 持续优化 AI 策略")

    except Exception as e:
        print(f"\n❌ 演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
