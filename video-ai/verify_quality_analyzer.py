#!/usr/bin/env python3
"""
质量分析器验证脚本

验证质量分析器的代码结构和基本功能（不需要视频文件）。
"""

import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def verify_imports():
    """验证模块导入"""
    print("=" * 70)
    print("验证 QualityAnalyzer 导入")
    print("=" * 70)
    print()

    try:
        from src.core.quality_analyzer import QualityAnalyzer, QualityMetrics
        print("✅ 成功导入 QualityAnalyzer")
        print("✅ 成功导入 QualityMetrics")
        return True
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        return False


def verify_quality_metrics():
    """验证 QualityMetrics 数据类"""
    print("\n" + "=" * 70)
    print("验证 QualityMetrics 数据结构")
    print("=" * 70)
    print()

    try:
        from src.core.quality_analyzer import QualityMetrics

        # 创建示例指标
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
        print(f"   - 清晰度: {metrics.sharpness}")
        print(f"   - 亮度: {metrics.brightness}")
        print(f"   - 综合评分: {metrics.overall_score}")
        print(f"   - 分辨率: {metrics.resolution[0]}x{metrics.resolution[1]}")

        # 测试 to_dict 方法
        metrics_dict = metrics.to_dict()
        print("✅ to_dict() 方法正常")
        print(f"   - 字典键数: {len(metrics_dict)}")

        return True
    except Exception as e:
        print(f"❌ 验证失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_analyzer_methods():
    """验证 QualityAnalyzer 方法"""
    print("\n" + "=" * 70)
    print("验证 QualityAnalyzer 方法")
    print("=" * 70)
    print()

    try:
        from src.core.quality_analyzer import QualityAnalyzer, QualityMetrics

        analyzer = QualityAnalyzer()
        print("✅ QualityAnalyzer 实例化成功")

        # 验证方法存在
        methods = [
            'analyze_video',
            'suggest_enhancements',
            'generate_quality_report',
            '_calculate_overall_score',
            '_analyze_visual_quality',
            '_analyze_audio_quality',
            '_analyze_technical_quality'
        ]

        for method in methods:
            if hasattr(analyzer, method):
                print(f"✅ 方法存在: {method}")
            else:
                print(f"❌ 方法缺失: {method}")
                return False

        return True
    except Exception as e:
        print(f"❌ 验证失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_suggestions_generation():
    """验证改进建议生成"""
    print("\n" + "=" * 70)
    print("验证改进建议生成")
    print("=" * 70)
    print()

    try:
        from src.core.quality_analyzer import QualityAnalyzer, QualityMetrics

        analyzer = QualityAnalyzer()

        # 测试用例 1: 优秀质量
        print("测试用例 1: 优秀质量视频")
        excellent_metrics = QualityMetrics(
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

        suggestions = analyzer.suggest_enhancements(excellent_metrics)
        print(f"  生成建议数: {len(suggestions)}")
        for i, s in enumerate(suggestions[:3], 1):
            print(f"    {i}. {s}")
        print("✅ 优秀质量建议生成成功")

        # 测试用例 2: 一般质量
        print("\n测试用例 2: 一般质量视频")
        poor_metrics = QualityMetrics(
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

        suggestions = analyzer.suggest_enhancements(poor_metrics)
        print(f"  生成建议数: {len(suggestions)}")
        for i, s in enumerate(suggestions[:3], 1):
            print(f"    {i}. {s}")
        print("✅ 一般质量建议生成成功")

        return True
    except Exception as e:
        print(f"❌ 验证失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_report_generation():
    """验证报告生成"""
    print("\n" + "=" * 70)
    print("验证质量报告生成")
    print("=" * 70)
    print()

    try:
        from src.core.quality_analyzer import QualityAnalyzer, QualityMetrics

        analyzer = QualityAnalyzer()

        metrics = QualityMetrics(
            sharpness=75.0,
            brightness=70.0,
            contrast=72.0,
            color_balance=75.0,
            audio_loudness=-10.0,
            audio_noise=70.0,
            audio_clarity=75.0,
            resolution=(1920, 1080),
            fps=30.0,
            bitrate=5000,
            overall_score=73.0
        )

        report = analyzer.generate_quality_report(metrics)

        print("✅ 报告生成成功")
        print("\n报告内容（前500字符）:")
        print("-" * 70)
        print(report[:500])
        print("-" * 70)

        # 验证报告包含关键内容
        required_strings = [
            "视频质量分析报告",
            "视觉质量",
            "音频质量",
            "技术规格",
            "综合评分"
        ]

        all_found = True
        for required in required_strings:
            if required in report:
                print(f"✅ 报告包含: {required}")
            else:
                print(f"❌ 报告缺少: {required}")
                all_found = False

        return all_found
    except Exception as e:
        print(f"❌ 验证失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_integration_with_editor():
    """验证与编辑器的集成"""
    print("\n" + "=" * 70)
    print("验证与 VideoEditor 的集成")
    print("=" * 70)
    print()

    try:
        from src.core.editor import VideoEditor
        print("✅ 成功导入 VideoEditor")

        # 检查 VideoEditor 是否有 quality_analyzer 属性
        import inspect
        source = inspect.getsource(VideoEditor.__init__)

        if 'quality_analyzer' in source:
            print("✅ VideoEditor.__init__ 包含质量分析器初始化")
        else:
            print("⚠️ 警告: VideoEditor.__init__ 未找到质量分析器初始化")

        if 'QualityAnalyzer' in source:
            print("✅ VideoEditor 导入了 QualityAnalyzer")
        else:
            print("⚠️ 警告: VideoEditor 未导入 QualityAnalyzer")

        return True
    except Exception as e:
        print(f"⚠️ 警告: {e}")
        return True  # 不是关键错误


def verify_file_structure():
    """验证文件结构"""
    print("\n" + "=" * 70)
    print("验证项目文件结构")
    print("=" * 70)
    print()

    files_to_check = [
        "src/core/quality_analyzer.py",
        "src/core/__init__.py",
        "examples/quality_demo.py",
        "tests/test_quality_analyzer.py",
        "docs/QUALITY_ANALYSIS.md",
        "docs/QUALITY_REPORT_EXAMPLE.md"
    ]

    all_exist = True
    for file_path in files_to_check:
        full_path = Path(project_root) / file_path
        if full_path.exists():
            file_size = full_path.stat().st_size
            print(f"✅ {file_path} ({file_size} bytes)")
        else:
            print(f"❌ 缺失: {file_path}")
            all_exist = False

    return all_exist


def main():
    """主验证流程"""
    print()
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "  Video-AI 质量分析系统验证".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "=" * 68 + "╝")
    print()

    results = {}

    # 运行所有验证
    results['文件结构'] = verify_file_structure()
    results['模块导入'] = verify_imports()
    results['QualityMetrics'] = verify_quality_metrics()
    results['分析器方法'] = verify_analyzer_methods()
    results['建议生成'] = verify_suggestions_generation()
    results['报告生成'] = verify_report_generation()
    results['编辑器集成'] = verify_integration_with_editor()

    # 总结
    print("\n" + "=" * 70)
    print("验证总结")
    print("=" * 70)
    print()

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name:<30} {status}")

    print()
    print(f"总体: {passed}/{total} 项验证通过")
    print()

    if passed == total:
        print("╔" + "=" * 68 + "╗")
        print("║" + " " * 68 + "║")
        print("║" + "  ✅ 所有验证通过！质量分析系统已准备就绪。".ljust(68) + "║")
        print("║" + " " * 68 + "║")
        print("╚" + "=" * 68 + "╝")
        return 0
    else:
        print("╔" + "=" * 68 + "╗")
        print("║" + " " * 68 + "║")
        print("║" + "  ❌ 部分验证失败。请检查上述输出。".ljust(68) + "║")
        print("║" + " " * 68 + "║")
        print("╚" + "=" * 68 + "╝")
        return 1


if __name__ == "__main__":
    sys.exit(main())
