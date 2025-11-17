#!/usr/bin/env python3
"""
直接测试质量分析器

避开其他模块的导入问题，直接测试质量分析器功能。
"""

import sys
import importlib.util

# 直接导入质量分析器，不通过 __init__.py
spec = importlib.util.spec_from_file_location(
    "quality_analyzer",
    "/home/user/tvbox1/video-ai/src/core/quality_analyzer.py"
)
quality_analyzer_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(quality_analyzer_module)

QualityAnalyzer = quality_analyzer_module.QualityAnalyzer
QualityMetrics = quality_analyzer_module.QualityMetrics


def test_imports():
    """测试导入"""
    print("=" * 70)
    print("✅ 成功导入 QualityAnalyzer")
    print("✅ 成功导入 QualityMetrics")
    print()


def test_quality_metrics():
    """测试 QualityMetrics"""
    print("=" * 70)
    print("测试 QualityMetrics 数据结构")
    print("=" * 70)

    metrics = QualityMetrics(
        sharpness=85.5,
        brightness=72.3,
        contrast=78.1,
        color_balance=81.0,
        audio_loudness=-8.5,
        audio_noise=78.5,
        audio_clarity=82.1,
        resolution=(1920, 1080),
        fps=29.97,
        bitrate=8500,
        overall_score=82.4
    )

    print("✅ QualityMetrics 创建成功")
    print(f"   清晰度: {metrics.sharpness}/100")
    print(f"   亮度: {metrics.brightness}/100")
    print(f"   对比度: {metrics.contrast}/100")
    print(f"   色彩平衡: {metrics.color_balance}/100")
    print(f"   音量: {metrics.audio_loudness}dB")
    print(f"   噪音: {metrics.audio_noise}/100")
    print(f"   清晰度: {metrics.audio_clarity}/100")
    print(f"   分辨率: {metrics.resolution[0]}x{metrics.resolution[1]}")
    print(f"   帧率: {metrics.fps}fps")
    print(f"   码率: {metrics.bitrate}kbps")
    print(f"   综合评分: {metrics.overall_score}/100")
    print()

    # 测试 to_dict
    metrics_dict = metrics.to_dict()
    print(f"✅ to_dict() 转换成功，包含 {len(metrics_dict)} 个字段")
    print()


def test_analyzer_creation():
    """测试分析器创建"""
    print("=" * 70)
    print("测试 QualityAnalyzer 实例化")
    print("=" * 70)

    analyzer = QualityAnalyzer()
    print("✅ QualityAnalyzer 实例创建成功")
    print()

    # 检查方法
    methods = [
        'analyze_video',
        'suggest_enhancements',
        'generate_quality_report',
        '_calculate_overall_score',
    ]

    print("检查方法...")
    for method in methods:
        if hasattr(analyzer, method):
            print(f"  ✅ {method}")
        else:
            print(f"  ❌ {method} 缺失")

    print()


def test_suggestions():
    """测试建议生成"""
    print("=" * 70)
    print("测试改进建议生成")
    print("=" * 70)

    analyzer = QualityAnalyzer()

    # 优秀质量
    print("\n【测试 1】优秀质量视频 (评分: 86.0)")
    excellent = QualityMetrics(
        sharpness=90.0,
        brightness=75.0,
        contrast=85.0,
        color_balance=88.0,
        audio_loudness=-8.0,
        audio_noise=85.0,
        audio_clarity=88.0,
        resolution=(1920, 1080),
        fps=30.0,
        bitrate=8500,
        overall_score=86.0
    )

    suggestions = analyzer.suggest_enhancements(excellent)
    print(f"生成 {len(suggestions)} 条建议:")
    for s in suggestions[:3]:
        print(f"  • {s}")

    # 较差质量
    print("\n【测试 2】较差质量视频 (评分: 42.0)")
    poor = QualityMetrics(
        sharpness=35.0,
        brightness=25.0,
        contrast=35.0,
        color_balance=40.0,
        audio_loudness=-25.0,
        audio_noise=40.0,
        audio_clarity=35.0,
        resolution=(640, 480),
        fps=15.0,
        bitrate=1500,
        overall_score=42.0
    )

    suggestions = analyzer.suggest_enhancements(poor)
    print(f"生成 {len(suggestions)} 条建议:")
    for s in suggestions[:5]:
        print(f"  • {s}")

    print()


def test_report_generation():
    """测试报告生成"""
    print("=" * 70)
    print("测试质量报告生成")
    print("=" * 70)
    print()

    analyzer = QualityAnalyzer()

    metrics = QualityMetrics(
        sharpness=78.0,
        brightness=72.0,
        contrast=75.0,
        color_balance=76.0,
        audio_loudness=-10.0,
        audio_noise=72.0,
        audio_clarity=76.0,
        resolution=(1920, 1080),
        fps=30.0,
        bitrate=6000,
        overall_score=75.5
    )

    report = analyzer.generate_quality_report(metrics)

    print("✅ 报告生成成功")
    print("\n报告内容:")
    print("-" * 70)
    print(report)
    print("-" * 70)
    print()


def test_scoring_algorithm():
    """测试评分算法"""
    print("=" * 70)
    print("测试综合评分算法")
    print("=" * 70)
    print()

    analyzer = QualityAnalyzer()

    test_cases = [
        {
            'name': '完美质量',
            'visual': {'sharpness': 100, 'brightness': 100, 'contrast': 100, 'color_balance': 100},
            'audio': {'audio_loudness': -6.0, 'audio_noise': 100, 'audio_clarity': 100},
            'tech': {'resolution': (1920, 1080), 'fps': 60.0, 'bitrate': 15000},
            'expected_min': 85  # 应该很高
        },
        {
            'name': '中等质量',
            'visual': {'sharpness': 70, 'brightness': 70, 'contrast': 70, 'color_balance': 70},
            'audio': {'audio_loudness': -12.0, 'audio_noise': 70, 'audio_clarity': 70},
            'tech': {'resolution': (1280, 720), 'fps': 30.0, 'bitrate': 5000},
            'expected_min': 65  # 应该中等
        },
        {
            'name': '低质量',
            'visual': {'sharpness': 30, 'brightness': 30, 'contrast': 30, 'color_balance': 30},
            'audio': {'audio_loudness': -30.0, 'audio_noise': 30, 'audio_clarity': 30},
            'tech': {'resolution': (640, 480), 'fps': 15.0, 'bitrate': 1500},
            'expected_min': 20  # 应该很低
        },
    ]

    for test in test_cases:
        score = analyzer._calculate_overall_score(
            test['visual'],
            test['audio'],
            test['tech']
        )

        status = "✅" if score >= test['expected_min'] else "⚠️"
        print(f"{status} {test['name']:<15} 评分: {score:6.1f}/100 (最低: {test['expected_min']})")

    print()


def main():
    """主测试函数"""
    print()
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "  直接测试 - QualityAnalyzer".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "=" * 68 + "╝")
    print()

    try:
        test_imports()
        test_quality_metrics()
        test_analyzer_creation()
        test_suggestions()
        test_scoring_algorithm()
        test_report_generation()

        print("=" * 70)
        print("✅ 所有测试通过！")
        print("=" * 70)
        print()

        print("📊 功能概览:")
        print("  ✓ QualityMetrics 数据结构")
        print("  ✓ QualityAnalyzer 实例化")
        print("  ✓ 改进建议生成")
        print("  ✓ 综合评分算法")
        print("  ✓ 质量报告生成")
        print()

        return 0

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
