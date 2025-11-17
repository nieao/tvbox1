"""
A/B 测试框架演示

展示如何使用 ABTestingFramework 进行实验管理、指标收集和分析。
"""

import sys
from pathlib import Path
from datetime import datetime
import random
import numpy as np

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.ab_testing import (
    ABTestingFramework,
    ExperimentStatus,
    VideoEditorABTesting
)


def simulate_user_interactions(framework, experiment_id, variant_configs, num_users=100):
    """
    模拟用户交互和指标收集

    Args:
        framework: ABTestingFramework 实例
        experiment_id: 实验ID
        variant_configs: 变体配置
        num_users: 模拟用户数
    """
    print(f"\n{'='*70}")
    print(f"模拟用户交互（{num_users} 个用户）")
    print(f"{'='*70}\n")

    # 定义各变体的指标分布
    # control: 基准版本
    # variant_a: 新UI，预期提升 10%
    # variant_b: 推荐算法改进，预期提升 15%

    variant_stats = {
        'control': {
            'completion_rate': {'mean': 0.70, 'std': 0.15},
            'user_rating': {'mean': 3.5, 'std': 1.0},
            'watch_time': {'mean': 300, 'std': 60},  # 秒
            'engagement_score': {'mean': 0.65, 'std': 0.2}
        },
        'variant_a': {
            'completion_rate': {'mean': 0.77, 'std': 0.14},  # +10%
            'user_rating': {'mean': 3.8, 'std': 0.95},
            'watch_time': {'mean': 330, 'std': 65},
            'engagement_score': {'mean': 0.71, 'std': 0.19}
        },
        'variant_b': {
            'completion_rate': {'mean': 0.81, 'std': 0.13},  # +15%
            'user_rating': {'mean': 4.0, 'std': 0.9},
            'watch_time': {'mean': 345, 'std': 70},
            'engagement_score': {'mean': 0.75, 'std': 0.18}
        }
    }

    experiment = framework.get_experiment(experiment_id)
    metrics = experiment.metrics

    for user_id in range(num_users):
        user_str = f"user_{user_id:04d}"

        # 为用户分配变体
        variant = framework.assign_variant(user_str, experiment_id)

        # 获取该变体的指标分布
        stats = variant_stats.get(variant, {})

        # 为每个指标生成数据
        for metric in metrics:
            if metric in stats:
                mean = stats[metric]['mean']
                std = stats[metric]['std']

                # 生成符合正态分布的值
                value = np.random.normal(mean, std)

                # 限制值的范围
                if metric == 'completion_rate' or metric == 'engagement_score':
                    value = max(0, min(1, value))
                elif metric == 'user_rating':
                    value = max(1, min(5, value))
                else:  # watch_time
                    value = max(0, value)

                # 记录指标
                framework.record_metric(
                    user_str,
                    experiment_id,
                    metric,
                    value,
                    metadata={'timestamp': datetime.now().isoformat()}
                )

    print(f"✓ 模拟完成，共生成 {num_users * len(metrics)} 个数据点")


def demo_experiment_lifecycle():
    """演示实验生命周期"""
    print("\n" + "="*70)
    print("演示 1: 实验生命周期管理")
    print("="*70)

    # 初始化框架
    framework = ABTestingFramework(storage_dir="/tmp/ab_tests_demo")

    # 定义变体
    variants = {
        'control': {
            'description': '原始版本',
            'ui_style': 'old',
            'algorithm': 'baseline'
        },
        'variant_a': {
            'description': '新UI设计',
            'ui_style': 'modern',
            'algorithm': 'baseline'
        },
        'variant_b': {
            'description': '优化推荐算法',
            'ui_style': 'old',
            'algorithm': 'improved_ml'
        }
    }

    # 创建实验
    experiment = framework.create_experiment(
        experiment_id='exp_ui_recommendation_001',
        name='用户界面与推荐算法优化',
        description='测试新UI设计和改进的推荐算法对用户体验的影响',
        variants=variants,
        traffic_split={
            'control': 0.34,
            'variant_a': 0.33,
            'variant_b': 0.33
        },
        metrics=[
            'completion_rate',
            'user_rating',
            'watch_time',
            'engagement_score'
        ],
        tags={
            'category': 'optimization',
            'priority': 'high',
            'owner': 'product_team'
        }
    )

    print(f"\n✓ 实验创建成功")
    print(f"  ID: {experiment.experiment_id}")
    print(f"  名称: {experiment.name}")
    print(f"  状态: {experiment.status}")
    print(f"  变体: {', '.join(experiment.variants.keys())}")

    # 启动实验
    print(f"\n启动实验...")
    experiment = framework.start_experiment('exp_ui_recommendation_001')
    print(f"✓ 实验已启动，状态: {experiment.status}")

    # 模拟用户交互
    simulate_user_interactions(
        framework,
        'exp_ui_recommendation_001',
        variants,
        num_users=150
    )

    # 获取实验摘要
    print(f"\n{'='*70}")
    print(f"实验摘要")
    print(f"{'='*70}")

    summary = framework.get_experiment_summary('exp_ui_recommendation_001')
    print(f"\n总用户数: {summary['total_users']}")
    print(f"\n变体分布:")
    for variant, count in summary['variant_distribution'].items():
        print(f"  {variant}: {count} 用户")

    print(f"\n指标数据点:")
    for metric, count in summary['metrics'].items():
        print(f"  {metric}: {count} 数据点")

    return framework, 'exp_ui_recommendation_001'


def demo_statistical_analysis(framework, experiment_id):
    """演示统计分析"""
    print("\n" + "="*70)
    print("演示 2: 统计分析")
    print("="*70 + "\n")

    experiment = framework.get_experiment(experiment_id)
    control = 'control'

    # 分析每个指标
    for metric in experiment.metrics:
        print(f"\n{'─'*70}")
        print(f"指标分析: {metric}")
        print(f"{'─'*70}")

        analysis = framework.analyze_experiment(
            experiment_id,
            metric,
            control,
            use_cache=False
        )

        if 'error' in analysis:
            print(f"  [错误] {analysis['error']}")
            continue

        print(f"\n对照组 ({control}):")
        ctrl_result = analysis['results'].get(control, {})
        print(f"  样本量: {ctrl_result.get('count', 0)}")
        print(f"  平均值: {ctrl_result.get('mean', 0):.4f}")
        print(f"  标准差: {ctrl_result.get('std', 0):.4f}")

        for variant, result in analysis['results'].items():
            if variant == control:
                continue

            print(f"\n{variant}:")
            print(f"  样本量: {result['count']}")
            print(f"  平均值: {result['mean']:.4f}")
            print(f"  标准差: {result['std']:.4f}")

            improvement = result.get('improvement', 0)
            p_value = result.get('p_value', 1)
            is_sig = result.get('significant', False)

            print(f"  相对提升: {improvement:+.2f}%")
            print(f"  P-value: {p_value:.6f}")

            if is_sig:
                print(f"  统计显著: ✓ 是 (p < 0.05)")
            else:
                print(f"  统计显著: ✗ 否 (p >= 0.05)")

            if 'confidence_interval' in result:
                ci = result['confidence_interval']
                print(f"  95% 置信区间: ±{ci:.4f}")


def demo_report_generation(framework, experiment_id):
    """演示报告生成"""
    print("\n" + "="*70)
    print("演示 3: 报告生成")
    print("="*70 + "\n")

    # 生成报告
    report = framework.generate_report(experiment_id, 'control')

    print(report)

    # 保存报告
    report_path = Path("/tmp/ab_test_report.txt")
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"\n✓ 报告已保存到: {report_path}")


def demo_data_export(framework, experiment_id):
    """演示数据导出"""
    print("\n" + "="*70)
    print("演示 4: 数据导出")
    print("="*70 + "\n")

    # 导出为 JSON
    print("导出为 JSON 格式...")
    json_data = framework.export_data(experiment_id, output_format='json')
    json_path = Path("/tmp/ab_test_data.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        f.write(json_data)
    print(f"✓ 已保存到: {json_path}")

    # 导出为 CSV
    print("\n导出为 CSV 格式...")
    csv_data = framework.export_data(experiment_id, output_format='csv')
    csv_path = Path("/tmp/ab_test_data.csv")
    with open(csv_path, 'w', encoding='utf-8') as f:
        f.write(csv_data)
    print(f"✓ 已保存到: {csv_path}")


def demo_variant_comparison(framework, experiment_id):
    """演示变体对比"""
    print("\n" + "="*70)
    print("演示 5: 多变体对比（ANOVA）")
    print("="*70 + "\n")

    experiment = framework.get_experiment(experiment_id)

    for metric in experiment.metrics[:2]:  # 只展示前2个指标
        print(f"\n{'─'*70}")
        print(f"指标: {metric}")
        print(f"{'─'*70}\n")

        result = framework.compare_variants(
            experiment_id,
            metric,
            list(experiment.variants.keys())
        )

        print("各变体统计信息:")
        for variant, stats in result['results'].items():
            if variant == 'anova':
                continue
            print(f"\n  {variant}:")
            print(f"    平均值: {stats['mean']:.4f}")
            print(f"    标准差: {stats['std']:.4f}")
            print(f"    样本量: {stats['count']}")

        # 显示 ANOVA 结果
        if 'anova' in result['results']:
            anova = result['results']['anova']
            print(f"\nANOVA 分析:")
            print(f"  F 统计量: {anova['f_statistic']:.4f}")
            print(f"  P-value: {anova['p_value']:.6f}")
            print(f"  统计显著: {'✓ 是' if anova['significant'] else '✗ 否'}")


def demo_editor_integration():
    """演示与视频编辑器的集成"""
    print("\n" + "="*70)
    print("演示 6: 与视频编辑器的集成")
    print("="*70 + "\n")

    # 初始化框架
    framework = ABTestingFramework(storage_dir="/tmp/ab_tests_editor")

    # 创建实验
    variants = {
        'control': {'strategy': 'baseline'},
        'aggressive': {'strategy': 'aggressive_cuts'},
        'balanced': {'strategy': 'balanced'}
    }

    framework.create_experiment(
        experiment_id='exp_editing_strategy',
        name='剪辑策略优化',
        description='测试不同剪辑策略对观看体验的影响',
        variants=variants
    )

    framework.start_experiment('exp_editing_strategy')

    # 初始化编辑器集成
    editor_ab = VideoEditorABTesting(framework)

    print("模拟编辑过程:\n")

    # 模拟5个用户的编辑过程
    for user_id in range(5):
        user = f"user_{user_id:03d}"

        # 设置实验
        variant = editor_ab.set_experiment('exp_editing_strategy', user)

        # 获取变体配置
        variant_config = editor_ab.get_variant_config()

        print(f"{user}:")
        print(f"  分配变体: {variant}")
        print(f"  策略配置: {variant_config}")

        # 模拟编辑过程中的指标收集
        completion_rate = np.random.uniform(0.7, 0.95)
        engagement = np.random.uniform(0.6, 0.9)

        editor_ab.record_metric('completion_rate', completion_rate)
        editor_ab.record_metric('engagement_score', engagement)

        print(f"  记录指标: completion_rate={completion_rate:.2f}, engagement={engagement:.2f}\n")

    # 分析结果
    print(f"\n{'─'*70}")
    print("实验结果:")
    print(f"{'─'*70}\n")

    analysis = framework.analyze_experiment(
        'exp_editing_strategy',
        'completion_rate',
        'control'
    )

    for variant, result in analysis['results'].items():
        print(f"{variant}:")
        print(f"  平均完成率: {result['mean']:.2%}")
        print(f"  样本量: {result['count']}")


def demo_experiment_pause_resume():
    """演示实验暂停和恢复"""
    print("\n" + "="*70)
    print("演示 7: 实验暂停和恢复")
    print("="*70 + "\n")

    framework = ABTestingFramework(storage_dir="/tmp/ab_tests_pause")

    # 创建并启动实验
    framework.create_experiment(
        experiment_id='exp_pause_test',
        name='暂停测试实验',
        description='演示实验的暂停和恢复功能',
        variants={'control': {}, 'variant_a': {}},
    )

    exp = framework.start_experiment('exp_pause_test')
    print(f"1. 实验已启动")
    print(f"   状态: {exp.status}")

    # 暂停实验
    exp = framework.pause_experiment('exp_pause_test')
    print(f"\n2. 实验已暂停")
    print(f"   状态: {exp.status}")

    # 停止实验
    exp = framework.stop_experiment('exp_pause_test')
    print(f"\n3. 实验已完成")
    print(f"   状态: {exp.status}")
    print(f"   结束时间: {exp.end_time}")


def main():
    """主函数"""
    print("\n" + "="*70)
    print("A/B 测试框架完整演示")
    print("="*70)

    # 演示 1: 实验生命周期
    framework, experiment_id = demo_experiment_lifecycle()

    # 演示 2: 统计分析
    demo_statistical_analysis(framework, experiment_id)

    # 演示 3: 报告生成
    demo_report_generation(framework, experiment_id)

    # 演示 4: 数据导出
    demo_data_export(framework, experiment_id)

    # 演示 5: 变体对比
    demo_variant_comparison(framework, experiment_id)

    # 演示 6: 编辑器集成
    demo_editor_integration()

    # 演示 7: 暂停恢复
    demo_experiment_pause_resume()

    print("\n" + "="*70)
    print("演示完成!")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
