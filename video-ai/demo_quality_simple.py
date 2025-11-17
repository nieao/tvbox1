#!/usr/bin/env python3
"""
简单的质量分析器演示

演示如何使用质量分析器，包括：
1. 创建质量指标
2. 生成改进建议
3. 生成质量报告
"""

import sys
import importlib.util

# 直接导入质量分析器，避免循环导入问题
spec = importlib.util.spec_from_file_location(
    "quality_analyzer",
    "/home/user/tvbox1/video-ai/src/core/quality_analyzer.py"
)
quality_analyzer_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(quality_analyzer_module)

QualityAnalyzer = quality_analyzer_module.QualityAnalyzer
QualityMetrics = quality_analyzer_module.QualityMetrics


def demo_excellent_quality():
    """演示：优秀质量视频"""
    print("\n" + "=" * 70)
    print("演示 1: 优秀质量视频")
    print("=" * 70 + "\n")

    analyzer = QualityAnalyzer()

    # 创建优秀质量的指标
    metrics = QualityMetrics(
        sharpness=87.5,
        brightness=75.0,
        contrast=82.1,
        color_balance=84.5,
        audio_loudness=-8.2,
        audio_noise=82.1,
        audio_clarity=85.3,
        resolution=(1920, 1080),
        fps=29.97,
        bitrate=8500,
        overall_score=83.2
    )

    # 生成报告
    report = analyzer.generate_quality_report(metrics)
    print(report)


def demo_poor_quality():
    """演示：较差质量视频"""
    print("\n" + "=" * 70)
    print("演示 2: 较差质量视频")
    print("=" * 70 + "\n")

    analyzer = QualityAnalyzer()

    # 创建较差质量的指标
    metrics = QualityMetrics(
        sharpness=38.2,
        brightness=32.5,
        contrast=35.8,
        color_balance=42.0,
        audio_loudness=-22.5,
        audio_noise=42.1,
        audio_clarity=38.9,
        resolution=(640, 480),
        fps=15.0,
        bitrate=1800,
        overall_score=38.5
    )

    # 生成报告
    report = analyzer.generate_quality_report(metrics)
    print(report)

    # 生成改进建议
    print("\n详细改进建议:")
    suggestions = analyzer.suggest_enhancements(metrics)
    for i, suggestion in enumerate(suggestions, 1):
        print(f"{i:2d}. {suggestion}")


def demo_comparison():
    """演示：视频对比"""
    print("\n" + "=" * 70)
    print("演示 3: 视频质量对比")
    print("=" * 70 + "\n")

    analyzer = QualityAnalyzer()

    # 视频 1: 高质量
    metrics1 = QualityMetrics(
        sharpness=82.5,
        brightness=71.8,
        contrast=79.2,
        color_balance=80.5,
        audio_loudness=-8.2,
        audio_noise=78.5,
        audio_clarity=81.3,
        resolution=(1920, 1080),
        fps=29.97,
        bitrate=8500,
        overall_score=80.2
    )

    # 视频 2: 中等质量
    metrics2 = QualityMetrics(
        sharpness=65.3,
        brightness=68.5,
        contrast=72.1,
        color_balance=70.2,
        audio_loudness=-12.5,
        audio_noise=72.1,
        audio_clarity=75.8,
        resolution=(1280, 720),
        fps=25.0,
        bitrate=5200,
        overall_score=71.5
    )

    # 对比输出
    print(f"{'指标':<20} {'视频1':<15} {'视频2':<15} {'差异':<15}")
    print("-" * 65)
    print(f"{'清晰度':<20} {metrics1.sharpness:<15.1f} {metrics2.sharpness:<15.1f} {metrics1.sharpness - metrics2.sharpness:+.1f}")
    print(f"{'亮度':<20} {metrics1.brightness:<15.1f} {metrics2.brightness:<15.1f} {metrics1.brightness - metrics2.brightness:+.1f}")
    print(f"{'对比度':<20} {metrics1.contrast:<15.1f} {metrics2.contrast:<15.1f} {metrics1.contrast - metrics2.contrast:+.1f}")
    print(f"{'色彩平衡':<20} {metrics1.color_balance:<15.1f} {metrics2.color_balance:<15.1f} {metrics1.color_balance - metrics2.color_balance:+.1f}")
    print("-" * 65)
    print(f"{'音量(dB)':<20} {metrics1.audio_loudness:<15.1f} {metrics2.audio_loudness:<15.1f} {metrics1.audio_loudness - metrics2.audio_loudness:+.1f}")
    print(f"{'噪音':<20} {metrics1.audio_noise:<15.1f} {metrics2.audio_noise:<15.1f} {metrics1.audio_noise - metrics2.audio_noise:+.1f}")
    print(f"{'清晰度':<20} {metrics1.audio_clarity:<15.1f} {metrics2.audio_clarity:<15.1f} {metrics1.audio_clarity - metrics2.audio_clarity:+.1f}")
    print("-" * 65)
    print(f"{'帧率(fps)':<20} {metrics1.fps:<15.1f} {metrics2.fps:<15.1f} {metrics1.fps - metrics2.fps:+.1f}")
    print(f"{'码率(kbps)':<20} {metrics1.bitrate:<15.0f} {metrics2.bitrate:<15.0f} {metrics1.bitrate - metrics2.bitrate:+.0f}")
    print("-" * 65)
    print(f"{'综合评分':<20} {metrics1.overall_score:<15.1f} {metrics2.overall_score:<15.1f} {metrics1.overall_score - metrics2.overall_score:+.1f}")
    print()

    # 确定赢家
    if metrics1.overall_score > metrics2.overall_score:
        diff = metrics1.overall_score - metrics2.overall_score
        print(f"🏆 视频1 质量更优，领先 {diff:.1f} 分")
    elif metrics2.overall_score > metrics1.overall_score:
        diff = metrics2.overall_score - metrics1.overall_score
        print(f"🏆 视频2 质量更优，领先 {diff:.1f} 分")
    else:
        print("🤝 两个视频质量相近")


def demo_json_export():
    """演示：JSON 导出"""
    print("\n" + "=" * 70)
    print("演示 4: 将指标导出为 JSON")
    print("=" * 70 + "\n")

    import json

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

    # 转换为字典
    metrics_dict = metrics.to_dict()

    # 修复分辨率（元组 -> 列表）
    metrics_dict['resolution'] = list(metrics_dict['resolution'])

    # 转换为 JSON
    json_str = json.dumps(metrics_dict, indent=2, ensure_ascii=False)

    print("JSON 格式的质量指标:")
    print(json_str)


def demo_quality_tips():
    """演示：质量优化建议"""
    print("\n" + "=" * 70)
    print("演示 5: 视频质量优化建议")
    print("=" * 70 + "\n")

    tips = {
        "录制前": [
            "✓ 选择充足光线的环境（自然光或专业灯光）",
            "✓ 避免逆光或过度强光",
            "✓ 使用高质量摄像机或手机（1080p+）",
            "✓ 使用专业麦克风而非内置麦克风",
            "✓ 检查音频设备是否正常工作",
        ],
        "录制时": [
            "✓ 确保摄像机焦点清晰（手动对焦）",
            "✓ 使用三脚架保持稳定（避免抖动）",
            "✓ 保持麦克风与口腔 10-20cm 的距离",
            "✓ 在安静的环境中录制（关闭风扇、空调等）",
            "✓ 监听音频并确保音量适中",
        ],
        "后期处理": [
            "✓ 应用锐化滤镜提升清晰度（如果过模糊）",
            "✓ 调整亮度和对比度",
            "✓ 使用色彩校正确保色彩准确",
            "✓ 应用降噪处理去除背景噪音",
            "✓ 规范化音频音量",
        ],
        "输出设置": [
            "✓ 使用 H.264 或 H.265 编码",
            "✓ 分辨率至少 1920x1080（1080p）",
            "✓ 帧率 30fps 或更高",
            "✓ 码率 5000kbps 或更高",
            "✓ 保证色彩空间正确（通常为 BT.709）",
        ],
    }

    for category, tip_list in tips.items():
        print(f"\n【{category}】")
        for tip in tip_list:
            print(f"  {tip}")


def main():
    """主函数"""
    print()
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "  Video-AI 质量分析演示".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "=" * 68 + "╝")

    try:
        demo_excellent_quality()
        demo_poor_quality()
        demo_comparison()
        demo_json_export()
        demo_quality_tips()

        print("\n" + "=" * 70)
        print("✅ 所有演示完成！")
        print("=" * 70)
        print()

        print("📚 更多信息，请查看:")
        print("  - 文档: docs/QUALITY_ANALYSIS.md")
        print("  - 报告示例: docs/QUALITY_REPORT_EXAMPLE.md")
        print("  - 演示脚本: examples/quality_demo.py")
        print()

        return 0

    except Exception as e:
        print(f"\n❌ 演示失败: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
