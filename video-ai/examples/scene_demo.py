"""
场景检测演示

展示如何使用 SceneDetector 进行视频场景检测，
支持多种检测方法和场景分析。
"""

import sys
from pathlib import Path
import json

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.scene_detector import SceneDetector, SceneType


def demo_basic_detection():
    """基础场景检测演示"""
    print("=" * 70)
    print("Video-AI 场景检测演示 - 基础检测")
    print("=" * 70)

    # 需要一个实际的视频文件来演示
    video_path = "data/input/sample.mp4"

    if not Path(video_path).exists():
        print(f"\n错误: 示例视频不存在: {video_path}")
        print("\n使用说明:")
        print("  python scene_demo.py <video_path> [method]")
        print("\n支持的方法:")
        print("  - frame_diff   : 基于帧差的检测")
        print("  - histogram    : 基于直方图的检测")
        print("  - motion       : 基于光流的检测")
        print("  - hybrid       : 混合检测（推荐）")
        return

    # 使用混合检测方法
    detector = SceneDetector(
        method="hybrid",
        threshold=30.0,
        min_scene_length=0.5,
        smooth_window=5
    )

    print(f"\n正在分析视频: {video_path}")
    print(f"检测方法: {detector.method}")
    print(f"阈值: {detector.threshold}")
    print("...")

    try:
        scenes = detector.detect_scenes(video_path, debug=True)

        print(f"\n检测完成！共检测到 {len(scenes)} 个场景\n")

        # 显示场景信息
        print("场景列表:")
        print("-" * 70)

        for i, scene in enumerate(scenes, 1):
            print(f"\n场景 {i}:")
            print(f"  时间范围: {scene.start_time:>8.2f}s - {scene.end_time:>8.2f}s")
            print(f"  时长:    {scene.duration:>8.2f}s")
            print(f"  帧数:    {scene.frame_count:>8} 帧")
            print(f"  类型:    {scene.scene_type.value}")
            print(f"  置信度:  {scene.confidence:>8.1%}")
            print(f"  运动强度: {scene.motion_level:>7.2f}")
            print(f"  颜色变化: {scene.color_change:>7.2f}")

        # 显示统计信息
        print("\n" + "=" * 70)
        print("统计信息:")
        print("-" * 70)

        stats = detector.get_statistics(scenes)
        print(f"总场景数: {stats['total_scenes']}")
        print(f"总时长: {stats['total_duration']:.2f} 秒")
        print(f"平均时长: {stats['average_duration']:.2f} 秒")
        print(f"最短场景: {stats['min_duration']:.2f} 秒")
        print(f"最长场景: {stats['max_duration']:.2f} 秒")

        print(f"\n场景类型分布:")
        for scene_type, count in stats['scene_types'].items():
            print(f"  {scene_type}: {count} 个")

        print(f"\n置信度统计:")
        print(f"  最低: {stats['confidence_stats']['min']:.2%}")
        print(f"  最高: {stats['confidence_stats']['max']:.2%}")
        print(f"  平均: {stats['confidence_stats']['average']:.2%}")

        # 保存结果
        output_path = "data/output/scenes.json"
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        detector.save_scenes(scenes, output_path)
        print(f"\n场景信息已保存: {output_path}")

    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()


def demo_compare_methods():
    """对比不同检测方法"""
    print("=" * 70)
    print("Video-AI 场景检测演示 - 方法对比")
    print("=" * 70)

    video_path = "data/input/sample.mp4"

    if not Path(video_path).exists():
        print(f"\n错误: 示例视频不存在: {video_path}")
        return

    methods = ["frame_diff", "histogram", "motion", "hybrid"]

    results = {}

    for method in methods:
        print(f"\n使用 {method} 方法进行检测...")

        detector = SceneDetector(method=method, threshold=30.0)

        try:
            scenes = detector.detect_scenes(video_path)
            stats = detector.get_statistics(scenes)

            results[method] = {
                'scenes_count': len(scenes),
                'total_duration': stats['total_duration'],
                'avg_duration': stats['average_duration'],
                'avg_confidence': stats['confidence_stats']['average'],
                'scene_types': stats['scene_types']
            }

            print(f"  检测到 {len(scenes)} 个场景")
            print(f"  平均时长: {stats['average_duration']:.2f}s")
            print(f"  平均置信度: {stats['confidence_stats']['average']:.2%}")

        except Exception as e:
            print(f"  错误: {e}")
            results[method] = None

    # 显示对比结果
    print("\n" + "=" * 70)
    print("方法对比结果:")
    print("-" * 70)

    for method, result in results.items():
        if result:
            print(f"\n{method}:")
            print(f"  检测到场景数: {result['scenes_count']}")
            print(f"  总时长: {result['total_duration']:.2f}s")
            print(f"  平均时长: {result['avg_duration']:.2f}s")
            print(f"  平均置信度: {result['avg_confidence']:.2%}")


def demo_with_custom_threshold():
    """使用自定义阈值进行检测"""
    print("=" * 70)
    print("Video-AI 场景检测演示 - 自定义阈值")
    print("=" * 70)

    video_path = "data/input/sample.mp4"

    if not Path(video_path).exists():
        print(f"\n错误: 示例视频不存在: {video_path}")
        return

    thresholds = [10.0, 20.0, 30.0, 50.0]

    print(f"\n分析视频: {video_path}")
    print("测试不同的检测阈值...\n")

    for threshold in thresholds:
        detector = SceneDetector(method="hybrid", threshold=threshold)

        try:
            scenes = detector.detect_scenes(video_path)
            print(f"阈值 {threshold:>5.1f}: 检测到 {len(scenes):>3} 个场景, "
                  f"平均时长 {sum(s.duration for s in scenes) / len(scenes) if scenes else 0:>6.2f}s")

        except Exception as e:
            print(f"阈值 {threshold:>5.1f}: 错误 - {e}")


def demo_scene_boundary_optimization():
    """场景边界优化演示"""
    print("=" * 70)
    print("Video-AI 场景检测演示 - 边界优化")
    print("=" * 70)

    video_path = "data/input/sample.mp4"

    if not Path(video_path).exists():
        print(f"\n错误: 示例视频不存在: {video_path}")
        return

    detector = SceneDetector(method="hybrid")

    print(f"\n分析视频: {video_path}")
    print("检测场景...")

    try:
        scenes = detector.detect_scenes(video_path)

        # 创建模拟的转录段落（演示用）
        mock_segments = []
        current_time = 0.0
        for i in range(len(scenes)):
            # 每个段落长度为5秒
            segment = type('obj', (object,), {
                'start': current_time,
                'end': current_time + 5.0,
                'text': f'这是第{i+1}个转录段落'
            })()
            mock_segments.append(segment)
            current_time += 5.0

        print(f"优化前: {len(scenes)} 个场景")

        # 优化边界
        optimized_scenes = detector.optimize_scene_boundaries(scenes, mock_segments)

        print(f"优化后: {len(optimized_scenes)} 个场景")

        print("\n场景时间对比:")
        print("-" * 70)
        for i, (original, optimized) in enumerate(zip(scenes, optimized_scenes)):
            print(f"\n场景 {i+1}:")
            print(f"  优化前: {original.start_time:.2f}s - {original.end_time:.2f}s")
            print(f"  优化后: {optimized.start_time:.2f}s - {optimized.end_time:.2f}s")

    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()


def main():
    """主函数"""
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║             Video-AI 场景检测演示                         ║
    ║                                                          ║
    ║        智能识别视频中的场景变化                            ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """)

    # 如果提供了命令行参数，运行自定义演示
    if len(sys.argv) > 1:
        video_path = sys.argv[1]
        method = sys.argv[2] if len(sys.argv) > 2 else "hybrid"

        print(f"\n正在分析视频: {video_path}")
        print(f"检测方法: {method}\n")

        detector = SceneDetector(method=method, threshold=30.0)

        try:
            scenes = detector.detect_scenes(video_path, debug=True)

            print(f"\n检测完成！共 {len(scenes)} 个场景\n")

            for i, scene in enumerate(scenes, 1):
                print(f"场景 {i}: {scene.start_time:.2f}s - {scene.end_time:.2f}s "
                      f"({scene.duration:.2f}s) [{scene.scene_type.value}] "
                      f"置信度: {scene.confidence:.1%}")

            # 保存结果
            output_path = "data/output/scenes_custom.json"
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            detector.save_scenes(scenes, output_path)
            print(f"\n结果已保存: {output_path}")

        except Exception as e:
            print(f"错误: {e}")
            import traceback
            traceback.print_exc()

        return

    # 否则显示交互菜单
    print("\n请选择要运行的演示:")
    print("  1. 基础场景检测")
    print("  2. 对比不同检测方法")
    print("  3. 测试不同阈值")
    print("  4. 场景边界优化")
    print("  0. 退出")

    choice = input("\n请输入选项 (0-4): ").strip()

    demos = {
        "1": demo_basic_detection,
        "2": demo_compare_methods,
        "3": demo_with_custom_threshold,
        "4": demo_scene_boundary_optimization
    }

    if choice in demos:
        demos[choice]()
    elif choice == "0":
        print("再见！")
    else:
        print("无效选项")


if __name__ == "__main__":
    main()
