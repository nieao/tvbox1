"""
视频质量分析演示

这个示例展示了如何使用 Video-AI 的质量分析功能来评估视频质量。
"""

import sys
from pathlib import Path
import json

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.quality_analyzer import QualityAnalyzer, QualityMetrics


def quality_analysis_example():
    """视频质量分析示例"""
    print("=" * 70)
    print("Video-AI 视频质量分析示例")
    print("=" * 70)

    # 创建质量分析器
    analyzer = QualityAnalyzer()

    # 输入视频路径（需要替换为实际的视频路径）
    video_path = "data/input/sample.mp4"

    print(f"\n输入视频: {video_path}\n")

    # 检查输入文件是否存在
    if not Path(video_path).exists():
        print(f"❌ 错误: 输入视频不存在: {video_path}")
        print("\n请将视频文件放到 data/input/ 目录下")
        print("\n你可以这样测试:")
        print("1. 下载一个测试视频")
        print("2. 放到 data/input/sample.mp4")
        print("3. 再次运行此脚本")
        return

    try:
        # 分析视频质量
        print("正在分析视频质量...")
        metrics = analyzer.analyze_video(video_path, sample_count=10)

        # 打印详细报告
        report = analyzer.generate_quality_report(metrics)
        print(report)

        # 保存为JSON格式
        output_json = "data/output/quality_metrics.json"
        Path("data/output").mkdir(parents=True, exist_ok=True)

        metrics_dict = metrics.to_dict()
        # 转换元组为列表，以便JSON序列化
        metrics_dict['resolution'] = list(metrics_dict['resolution'])

        with open(output_json, 'w', encoding='utf-8') as f:
            json.dump(metrics_dict, f, indent=2, ensure_ascii=False)

        print(f"\n✅ 质量指标已保存到: {output_json}")

    except Exception as e:
        print(f"❌ 分析失败: {e}")
        import traceback
        traceback.print_exc()


def batch_quality_analysis_example():
    """批量视频质量分析示例"""
    print("\n" + "=" * 70)
    print("批量视频质量分析示例")
    print("=" * 70)

    analyzer = QualityAnalyzer()
    input_dir = Path("data/input")

    # 支持的视频格式
    video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.webm'}

    # 查找所有视频文件
    video_files = [
        f for f in input_dir.iterdir()
        if f.suffix.lower() in video_extensions
    ] if input_dir.exists() else []

    if not video_files:
        print(f"未找到视频文件在 {input_dir}")
        print("请在该目录下放置视频文件")
        return

    print(f"\n找到 {len(video_files)} 个视频文件\n")

    results = []
    output_dir = Path("data/output")
    output_dir.mkdir(parents=True, exist_ok=True)

    for i, video_file in enumerate(video_files, 1):
        print(f"[{i}/{len(video_files)}] 分析: {video_file.name}")

        try:
            metrics = analyzer.analyze_video(str(video_file))
            results.append({
                'filename': video_file.name,
                'overall_score': metrics.overall_score,
                'sharpness': metrics.sharpness,
                'brightness': metrics.brightness,
                'contrast': metrics.contrast,
                'color_balance': metrics.color_balance,
                'audio_loudness': metrics.audio_loudness,
                'audio_noise': metrics.audio_noise,
                'audio_clarity': metrics.audio_clarity,
                'resolution': f"{metrics.resolution[0]}x{metrics.resolution[1]}",
                'fps': metrics.fps,
                'bitrate': metrics.bitrate
            })
            print(f"  📊 质量评分: {metrics.overall_score:.1f}/100")

        except Exception as e:
            print(f"  ❌ 分析失败: {e}")
            continue

    # 保存批量结果
    if results:
        output_file = output_dir / "batch_quality_results.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(f"\n✅ 批量分析完成！结果已保存到: {output_file}")

        # 打印统计信息
        scores = [r['overall_score'] for r in results]
        print(f"\n统计信息:")
        print(f"  平均评分: {sum(scores)/len(scores):.1f}/100")
        print(f"  最高评分: {max(scores):.1f}/100")
        print(f"  最低评分: {min(scores):.1f}/100")


def compare_videos_example():
    """视频对比分析示例"""
    print("\n" + "=" * 70)
    print("视频对比分析示例")
    print("=" * 70)

    analyzer = QualityAnalyzer()

    # 两个视频路径
    video1 = "data/input/video1.mp4"
    video2 = "data/input/video2.mp4"

    print(f"\n视频1: {video1}")
    print(f"视频2: {video2}\n")

    # 检查文件是否存在
    if not Path(video1).exists() or not Path(video2).exists():
        print("❌ 错误: 某个视频文件不存在")
        print("请确保两个视频都存在于 data/input/ 目录")
        return

    try:
        # 分析两个视频
        print("正在分析视频1...")
        metrics1 = analyzer.analyze_video(video1)

        print("正在分析视频2...")
        metrics2 = analyzer.analyze_video(video2)

        # 对比结果
        print("\n" + "=" * 70)
        print("对比结果")
        print("=" * 70)

        print(f"\n{'指标':<20} {'视频1':<15} {'视频2':<15} {'差异':<15}")
        print("-" * 65)

        def compare_metric(name, val1, val2, format_str="{:.1f}"):
            diff = val2 - val1
            diff_str = format_str.format(diff)
            if diff > 0:
                diff_display = f"(+{diff_str})"
            else:
                diff_display = f"({diff_str})"

            print(f"{name:<20} {format_str.format(val1):<15} "
                  f"{format_str.format(val2):<15} {diff_display:<15}")

        print("\n【视觉质量】")
        compare_metric("清晰度", metrics1.sharpness, metrics2.sharpness)
        compare_metric("亮度", metrics1.brightness, metrics2.brightness)
        compare_metric("对比度", metrics1.contrast, metrics2.contrast)
        compare_metric("色彩平衡", metrics1.color_balance, metrics2.color_balance)

        print("\n【音频质量】")
        compare_metric("音量", metrics1.audio_loudness, metrics2.audio_loudness)
        compare_metric("噪音", metrics1.audio_noise, metrics2.audio_noise)
        compare_metric("清晰度", metrics1.audio_clarity, metrics2.audio_clarity)

        print("\n【技术规格】")
        compare_metric("帧率", metrics1.fps, metrics2.fps)
        compare_metric("码率", metrics1.bitrate, metrics2.bitrate, "{:.0f}")

        print("\n【综合评分】")
        compare_metric("总体评分", metrics1.overall_score, metrics2.overall_score)

        # 确定赢家
        if metrics1.overall_score > metrics2.overall_score:
            print(f"\n🏆 视频1 质量更优 (差异: {metrics1.overall_score - metrics2.overall_score:.1f}分)")
        elif metrics2.overall_score > metrics1.overall_score:
            print(f"\n🏆 视频2 质量更优 (差异: {metrics2.overall_score - metrics1.overall_score:.1f}分)")
        else:
            print("\n🤝 两个视频质量相近")

    except Exception as e:
        print(f"❌ 分析失败: {e}")
        import traceback
        traceback.print_exc()


def quality_tips_example():
    """视频质量优化建议示例"""
    print("\n" + "=" * 70)
    print("视频质量优化建议")
    print("=" * 70)

    tips = {
        "清晰度": [
            "使用高分辨率摄像头",
            "确保适当的焦点和对焦",
            "避免强烈的动作模糊",
            "应用锐化滤镜（如果过度模糊）"
        ],
        "亮度": [
            "在充足光线下录制",
            "避免逆光或反差过大",
            "使用合适的曝光补偿",
            "后期调整亮度和对比度"
        ],
        "音频": [
            "使用专业麦克风",
            "在安静的环境中录制",
            "避免背景噪音和风声",
            "后期进行降噪处理"
        ],
        "技术参数": [
            "至少使用1080p分辨率",
            "帧率不低于24fps（推荐30fps或更高）",
            "码率至少5000kbps以上",
            "使用H.264或H.265编码"
        ]
    }

    for category, tip_list in tips.items():
        print(f"\n【{category}】")
        for tip in tip_list:
            print(f"  • {tip}")


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="视频质量分析演示")
    parser.add_argument(
        "--mode",
        choices=["single", "batch", "compare", "tips"],
        default="single",
        help="运行模式: single(单个), batch(批量), compare(对比), tips(建议)"
    )
    parser.add_argument(
        "--video",
        help="指定视频文件路径"
    )

    args = parser.parse_args()

    if args.mode == "single":
        quality_analysis_example()
    elif args.mode == "batch":
        batch_quality_analysis_example()
    elif args.mode == "compare":
        compare_videos_example()
    elif args.mode == "tips":
        quality_tips_example()

    print("\n" + "=" * 70)
    print("演示完成！")
    print("=" * 70)


if __name__ == "__main__":
    main()
