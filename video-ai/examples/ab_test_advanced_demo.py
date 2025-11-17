"""
A/B 测试框架高级演示

展示与视频编辑器的深度集成，包括实验管理、策略对比、结果分析等。
"""

import sys
from pathlib import Path
import json
import random
import numpy as np

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.ab_testing import ABTestingFramework


def demo_editing_strategy_comparison():
    """演示不同剪辑策略的对比实验"""
    print("\n" + "="*70)
    print("演示：不同剪辑策略的对比实验")
    print("="*70 + "\n")

    # 初始化框架
    framework = ABTestingFramework(storage_dir="/tmp/ab_tests_strategy")

    # 定义不同的剪辑策略
    variants = {
        'baseline': {
            'description': '基准策略：基于关键词提取',
            'min_segment_length': 10,
            'max_segments': 10,
            'transition_style': 'text',
            'compression_target': 0.30
        },
        'aggressive': {
            'description': '激进策略：最大化压缩',
            'min_segment_length': 5,
            'max_segments': 15,
            'transition_style': 'fade',
            'compression_target': 0.50
        },
        'balanced': {
            'description': '平衡策略：质量和压缩的折中',
            'min_segment_length': 8,
            'max_segments': 12,
            'transition_style': 'modern',
            'compression_target': 0.35
        },
        'quality_first': {
            'description': '质量优先：最少压缩',
            'min_segment_length': 15,
            'max_segments': 8,
            'transition_style': 'text',
            'compression_target': 0.20
        }
    }

    # 创建实验
    experiment = framework.create_experiment(
        experiment_id='exp_editing_strategy_v1',
        name='剪辑策略优化实验',
        description='对比不同剪辑策略对用户体验的影响',
        variants=variants,
        traffic_split={
            'baseline': 0.25,
            'aggressive': 0.25,
            'balanced': 0.25,
            'quality_first': 0.25
        },
        metrics=[
            'completion_rate',
            'watch_quality_score',
            'information_density',
            'user_satisfaction'
        ],
        tags={
            'domain': 'video_editing',
            'version': 'v1.0',
            'owner': 'ai_team'
        }
    )

    print("✓ 创建实验完成")
    print(f"  名称: {experiment.name}")
    print(f"  ID: {experiment.experiment_id}")
    print(f"  变体数: {len(variants)}")

    # 启动实验
    framework.start_experiment('exp_editing_strategy_v1')
    print(f"\n✓ 实验已启动")

    # 模拟用户数据
    print("\n模拟用户编辑数据...")

    # 定义各策略的预期表现
    strategy_performance = {
        'baseline': {
            'completion_rate': {'mean': 0.85, 'std': 0.12},
            'watch_quality_score': {'mean': 0.78, 'std': 0.15},
            'information_density': {'mean': 0.65, 'std': 0.18},
            'user_satisfaction': {'mean': 3.8, 'std': 0.9}
        },
        'aggressive': {
            'completion_rate': {'mean': 0.72, 'std': 0.14},
            'watch_quality_score': {'mean': 0.65, 'std': 0.18},
            'information_density': {'mean': 0.85, 'std': 0.12},
            'user_satisfaction': {'mean': 3.2, 'std': 1.1}
        },
        'balanced': {
            'completion_rate': {'mean': 0.88, 'std': 0.11},
            'watch_quality_score': {'mean': 0.81, 'std': 0.13},
            'information_density': {'mean': 0.72, 'std': 0.16},
            'user_satisfaction': {'mean': 4.1, 'std': 0.8}
        },
        'quality_first': {
            'completion_rate': {'mean': 0.92, 'std': 0.10},
            'watch_quality_score': {'mean': 0.88, 'std': 0.10},
            'information_density': {'mean': 0.55, 'std': 0.20},
            'user_satisfaction': {'mean': 4.3, 'std': 0.7}
        }
    }

    num_users = 200
    for user_id in range(num_users):
        user_str = f"user_{user_id:04d}"
        variant = framework.assign_variant(user_str, 'exp_editing_strategy_v1')

        metrics = experiment.metrics
        stats = strategy_performance.get(variant, {})

        for metric in metrics:
            if metric in stats:
                mean = stats[metric]['mean']
                std = stats[metric]['std']
                value = np.random.normal(mean, std)

                # 限制范围
                if metric in ['completion_rate', 'watch_quality_score', 'information_density']:
                    value = max(0, min(1, value))
                elif metric == 'user_satisfaction':
                    value = max(1, min(5, value))

                framework.record_metric(user_str, 'exp_editing_strategy_v1', metric, value)

    print(f"✓ 模拟完成（{num_users} 个用户，{num_users * len(experiment.metrics)} 个数据点）")

    # 分析结果
    print("\n" + "─"*70)
    print("实验结果分析")
    print("─"*70 + "\n")

    for metric in experiment.metrics:
        print(f"\n指标：{metric}")
        print("─" * 70)

        analysis = framework.analyze_experiment(
            'exp_editing_strategy_v1',
            metric,
            'baseline',
            use_cache=False
        )

        results = analysis['results']

        # 按平均值排序
        sorted_variants = sorted(
            results.items(),
            key=lambda x: x[1]['mean'],
            reverse=True
        )

        for rank, (variant, result) in enumerate(sorted_variants, 1):
            print(f"\n{rank}. {variant}")
            print(f"   平均值: {result['mean']:.4f}")
            print(f"   样本量: {result['count']}")

            if variant != 'baseline':
                improvement = result.get('improvement', 0)
                p_value = result.get('p_value', 1)
                is_sig = result.get('significant', False)

                symbol = "▲" if improvement > 0 else "▼"
                print(f"   {symbol} 相对提升: {improvement:+.2f}%")
                print(f"   P-value: {p_value:.6f} {'*' if is_sig else ''}")


def demo_feature_testing():
    """演示新功能的 A/B 测试"""
    print("\n" + "="*70)
    print("演示：新功能的 A/B 测试")
    print("="*70 + "\n")

    framework = ABTestingFramework(storage_dir="/tmp/ab_tests_features")

    # 测试新的 AI 推荐功能
    variants = {
        'control': {
            'ai_recommendations': False,
            'recommendation_model': None,
            'description': '无 AI 推荐（基准）'
        },
        'ai_v1': {
            'ai_recommendations': True,
            'recommendation_model': 'simple_llm',
            'description': 'Simple LLM 模型'
        },
        'ai_v2': {
            'ai_recommendations': True,
            'recommendation_model': 'advanced_ml',
            'description': '高级 ML 模型'
        }
    }

    experiment = framework.create_experiment(
        experiment_id='exp_ai_recommendations',
        name='AI 推荐功能测试',
        description='测试不同推荐模型对用户体验的影响',
        variants=variants,
        metrics=['click_through_rate', 'segment_relevance', 'recommendation_quality']
    )

    framework.start_experiment('exp_ai_recommendations')

    print("✓ 实验创建并启动")
    print(f"  测试功能: AI 推荐系统")
    print(f"  对照组: 无 AI 推荐")
    print(f"  试验组: {len(variants) - 1} 个不同的模型配置")

    # 模拟数据
    print("\n模拟用户交互数据...")

    feature_perf = {
        'control': {
            'click_through_rate': {'mean': 0.35, 'std': 0.15},
            'segment_relevance': {'mean': 0.72, 'std': 0.18},
            'recommendation_quality': {'mean': 3.5, 'std': 1.0}
        },
        'ai_v1': {
            'click_through_rate': {'mean': 0.42, 'std': 0.14},
            'segment_relevance': {'mean': 0.78, 'std': 0.16},
            'recommendation_quality': {'mean': 3.9, 'std': 0.95}
        },
        'ai_v2': {
            'click_through_rate': {'mean': 0.48, 'std': 0.13},
            'segment_relevance': {'mean': 0.82, 'std': 0.14},
            'recommendation_quality': {'mean': 4.2, 'std': 0.85}
        }
    }

    for user_id in range(150):
        user_str = f"user_{user_id:04d}"
        variant = framework.assign_variant(user_str, 'exp_ai_recommendations')

        stats = feature_perf.get(variant, {})
        for metric in experiment.metrics:
            if metric in stats:
                mean = stats[metric]['mean']
                std = stats[metric]['std']
                value = np.random.normal(mean, std)

                if metric in ['click_through_rate', 'segment_relevance']:
                    value = max(0, min(1, value))
                elif metric == 'recommendation_quality':
                    value = max(1, min(5, value))

                framework.record_metric(user_str, 'exp_ai_recommendations', metric, value)

    print("✓ 数据模拟完成（150 个用户）")

    # 分析关键指标
    print("\n" + "─"*70)
    print("关键指标分析：点击率 (CTR)")
    print("─"*70 + "\n")

    analysis = framework.analyze_experiment(
        'exp_ai_recommendations',
        'click_through_rate',
        'control',
        use_cache=False
    )

    control_mean = analysis['results']['control']['mean']
    print(f"对照组 CTR: {control_mean:.2%}\n")

    for variant in ['ai_v1', 'ai_v2']:
        result = analysis['results'][variant]
        improvement = result['improvement']
        p_value = result.get('p_value', 1)
        is_sig = result.get('significant', False)

        print(f"{variant}:")
        print(f"  CTR: {result['mean']:.2%}")
        print(f"  相对提升: {improvement:+.2f}%")
        print(f"  显著性: {'显著 ✓' if is_sig else '不显著'}")
        print()


def demo_report_and_export():
    """演示报告生成和数据导出"""
    print("\n" + "="*70)
    print("演示：报告生成和数据导出")
    print("="*70 + "\n")

    framework = ABTestingFramework(storage_dir="/tmp/ab_tests_report")

    # 创建一个简单的实验
    framework.create_experiment(
        experiment_id='exp_report_demo',
        name='报告演示实验',
        description='演示报告生成功能',
        variants={
            'control': {'version': '1.0'},
            'variant_a': {'version': '2.0'},
        }
    )

    framework.start_experiment('exp_report_demo')

    # 添加一些数据
    for user_id in range(50):
        user_str = f"user_{user_id:04d}"
        variant = framework.assign_variant(user_str, 'exp_report_demo')

        for metric in ['completion_rate', 'user_rating']:
            if metric == 'completion_rate':
                value = np.random.uniform(0.7, 0.95)
            else:
                value = np.random.uniform(3.5, 4.5)

            framework.record_metric(user_str, 'exp_report_demo', metric, value)

    # 生成报告
    print("生成 A/B 测试报告...\n")
    report = framework.generate_report('exp_report_demo', 'control')

    # 显示报告（截断）
    report_lines = report.split('\n')
    for line in report_lines[:40]:
        print(line)

    print(f"\n... （共 {len(report_lines)} 行）")

    # 保存报告
    report_path = Path("/tmp/ab_test_advanced_report.txt")
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"\n✓ 完整报告已保存到: {report_path}")

    # 导出数据为 JSON
    print("\n导出实验数据...")
    json_data = framework.export_data('exp_report_demo', output_format='json')

    json_path = Path("/tmp/ab_test_data_advanced.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        f.write(json_data)

    print(f"✓ JSON 数据已导出到: {json_path}")

    # 显示数据摘要
    data = json.loads(json_data)
    print(f"\n数据摘要:")
    print(f"  实验 ID: {data['experiment_id']}")
    for variant, metrics in data['metrics_data'].items():
        total_points = sum(len(v) for v in metrics.values())
        print(f"  {variant}: {total_points} 个数据点")


def print_summary():
    """打印总结"""
    print("\n" + "="*70)
    print("A/B 测试框架高级功能总结")
    print("="*70 + "\n")

    features = [
        ("实验管理", "创建、启动、停止、暂停实验"),
        ("流量分配", "灵活配置不同变体的流量比例"),
        ("指标收集", "自动收集各种关键业务指标"),
        ("统计分析", "使用 t-test 和 ANOVA 进行统计显著性检验"),
        ("报告生成", "自动生成详细的 A/B 测试报告"),
        ("数据导出", "支持 JSON 和 CSV 格式导出"),
        ("编辑器集成", "与视频编辑器深度集成"),
        ("缓存优化", "智能缓存分析结果，提升性能"),
    ]

    for i, (feature, description) in enumerate(features, 1):
        print(f"{i}. {feature}")
        print(f"   └─ {description}\n")


def main():
    """主函数"""
    print("\n" + "="*70)
    print("A/B 测试框架高级演示")
    print("="*70)

    # 演示 1：剪辑策略对比
    demo_editing_strategy_comparison()

    # 演示 2：新功能测试
    demo_feature_testing()

    # 演示 3：报告生成
    demo_report_and_export()

    # 总结
    print_summary()

    print("="*70)
    print("演示完成！")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
