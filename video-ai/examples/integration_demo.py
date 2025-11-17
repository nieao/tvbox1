"""
场景检测与内容分析的集成演示

展示如何在视频编辑流程中集成场景检测功能。
"""

import sys
from pathlib import Path
import json
from datetime import datetime

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.scene_detector import SceneDetector, SceneType


def demo_scene_detection_workflow():
    """完整的场景检测工作流演示"""
    print("=" * 80)
    print("Video-AI 场景检测与内容分析集成演示")
    print("=" * 80)

    # 配置
    video_path = "data/input/sample.mp4"
    output_dir = Path("data/output")
    output_dir.mkdir(parents=True, exist_ok=True)

    if not Path(video_path).exists():
        print(f"\n错误: 视频文件不存在 {video_path}")
        print("\n使用说明:")
        print("  将视频放在 data/input/ 目录下")
        print("  视频文件名应为 sample.mp4")
        return

    # ========== 步骤1: 场景检测 ==========
    print("\n[步骤1] 运行场景检测...")
    print("-" * 80)

    detector = SceneDetector(method="hybrid", threshold=30.0)

    try:
        scenes = detector.detect_scenes(video_path, debug=True)
        print(f"\n成功检测到 {len(scenes)} 个场景\n")
    except Exception as e:
        print(f"错误: {e}")
        return

    # ========== 步骤2: 场景分析 ==========
    print("\n[步骤2] 分析场景特征...")
    print("-" * 80)

    stats = detector.get_statistics(scenes)

    print(f"\n总体统计:")
    print(f"  总场景数: {stats['total_scenes']}")
    print(f"  总时长: {stats['total_duration']:.2f} 秒")
    print(f"  平均时长: {stats['average_duration']:.2f} 秒")
    print(f"  最短: {stats['min_duration']:.2f} 秒")
    print(f"  最长: {stats['max_duration']:.2f} 秒")

    print(f"\n场景类型分布:")
    for scene_type, count in stats['scene_types'].items():
        percentage = (count / len(scenes)) * 100
        print(f"  {scene_type}: {count} ({percentage:.1f}%)")

    print(f"\n置信度统计:")
    print(f"  最低: {stats['confidence_stats']['min']:.1%}")
    print(f"  最高: {stats['confidence_stats']['max']:.1%}")
    print(f"  平均: {stats['confidence_stats']['average']:.1%}")

    # ========== 步骤3: 详细的场景信息 ==========
    print("\n[步骤3] 详细的场景信息...")
    print("-" * 80)

    # 按时长分类
    short_scenes = [s for s in scenes if s.duration < 2.0]
    medium_scenes = [s for s in scenes if 2.0 <= s.duration < 10.0]
    long_scenes = [s for s in scenes if s.duration >= 10.0]

    print(f"\n按时长分类:")
    print(f"  短场景 (<2s): {len(short_scenes)} ({len(short_scenes)/len(scenes)*100:.1f}%)")
    print(f"  中场景 (2-10s): {len(medium_scenes)} ({len(medium_scenes)/len(scenes)*100:.1f}%)")
    print(f"  长场景 (>10s): {len(long_scenes)} ({len(long_scenes)/len(scenes)*100:.1f}%)")

    # 按运动强度分类
    static_scenes = [s for s in scenes if s.motion_level < 0.3]
    dynamic_scenes = [s for s in scenes if s.motion_level >= 0.3]

    print(f"\n按运动强度分类:")
    print(f"  静态场景: {len(static_scenes)} ({len(static_scenes)/len(scenes)*100:.1f}%)")
    print(f"  动态场景: {len(dynamic_scenes)} ({len(dynamic_scenes)/len(scenes)*100:.1f}%)")

    # 按高置信度分类
    high_confidence = [s for s in scenes if s.confidence >= 0.8]
    medium_confidence = [s for s in scenes if 0.5 <= s.confidence < 0.8]
    low_confidence = [s for s in scenes if s.confidence < 0.5]

    print(f"\n按置信度分类:")
    print(f"  高 (>=0.8): {len(high_confidence)} ({len(high_confidence)/len(scenes)*100:.1f}%)")
    print(f"  中 (0.5-0.8): {len(medium_confidence)} ({len(medium_confidence)/len(scenes)*100:.1f}%)")
    print(f"  低 (<0.5): {len(low_confidence)} ({len(low_confidence)/len(scenes)*100:.1f}%)")

    # ========== 步骤4: 保存结果 ==========
    print("\n[步骤4] 保存检测结果...")
    print("-" * 80)

    # 保存场景 JSON
    scenes_json_path = output_dir / "scenes_detailed.json"
    detector.save_scenes(scenes, str(scenes_json_path))
    print(f"\n场景数据已保存: {scenes_json_path}")

    # 生成详细报告
    report_path = output_dir / "scene_detection_report.txt"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("场景检测详细报告\n")
        f.write("=" * 80 + "\n\n")

        f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"视频文件: {video_path}\n")
        f.write(f"检测方法: {detector.method}\n")
        f.write(f"阈值: {detector.threshold}\n\n")

        f.write("=" * 80 + "\n")
        f.write("统计信息\n")
        f.write("=" * 80 + "\n\n")

        f.write(f"总场景数: {stats['total_scenes']}\n")
        f.write(f"总时长: {stats['total_duration']:.2f} 秒\n")
        f.write(f"平均时长: {stats['average_duration']:.2f} 秒\n")
        f.write(f"最短: {stats['min_duration']:.2f} 秒\n")
        f.write(f"最长: {stats['max_duration']:.2f} 秒\n\n")

        f.write("场景类型分布:\n")
        for scene_type, count in stats['scene_types'].items():
            percentage = (count / len(scenes)) * 100
            f.write(f"  {scene_type}: {count} ({percentage:.1f}%)\n")

        f.write(f"\n置信度统计:\n")
        f.write(f"  最低: {stats['confidence_stats']['min']:.1%}\n")
        f.write(f"  最高: {stats['confidence_stats']['max']:.1%}\n")
        f.write(f"  平均: {stats['confidence_stats']['average']:.1%}\n")

        f.write("\n" + "=" * 80 + "\n")
        f.write("详细场景列表\n")
        f.write("=" * 80 + "\n\n")

        for i, scene in enumerate(scenes, 1):
            f.write(f"场景 {i}:\n")
            f.write(f"  时间范围: {scene.start_time:.2f}s - {scene.end_time:.2f}s\n")
            f.write(f"  时长: {scene.duration:.2f}s\n")
            f.write(f"  帧数: {scene.frame_count} 帧\n")
            f.write(f"  类型: {scene.scene_type.value}\n")
            f.write(f"  置信度: {scene.confidence:.1%}\n")
            f.write(f"  运动强度: {scene.motion_level:.2f}\n")
            f.write(f"  颜色变化: {scene.color_change:.2f}\n")
            f.write(f"  亮度变化: {scene.brightness_change:.2f}\n")
            f.write("\n")

    print(f"详细报告已保存: {report_path}")

    # ========== 步骤5: 生成可视化数据 ==========
    print("\n[步骤5] 生成可视化数据...")
    print("-" * 80)

    # 生成时间轴数据（CSV格式）
    timeline_path = output_dir / "scene_timeline.csv"
    with open(timeline_path, 'w', encoding='utf-8') as f:
        f.write("scene_id,start_time,end_time,duration,type,confidence,motion,color_change\n")
        for i, scene in enumerate(scenes):
            f.write(f"{i+1},{scene.start_time:.2f},{scene.end_time:.2f},{scene.duration:.2f},"
                   f"{scene.scene_type.value},{scene.confidence:.3f},"
                   f"{scene.motion_level:.3f},{scene.color_change:.3f}\n")

    print(f"时间轴数据已保存: {timeline_path}")

    # ========== 步骤6: 建议的切割点 ==========
    print("\n[步骤6] 建议的视频切割点...")
    print("-" * 80)

    print(f"\n推荐的关键帧位置（用于视频编辑）:\n")
    for i, scene in enumerate(scenes):
        if scene.confidence >= 0.7:  # 只显示高置信度的切割点
            print(f"  {scene.start_time:.2f}s (置信度: {scene.confidence:.1%})")

    # ========== 总结 ==========
    print("\n" + "=" * 80)
    print("场景检测完成总结")
    print("=" * 80)
    print(f"\n✓ 检测到 {len(scenes)} 个场景")
    print(f"✓ 生成的文件:")
    print(f"  - {scenes_json_path}")
    print(f"  - {report_path}")
    print(f"  - {timeline_path}")
    print(f"\n推荐下一步:")
    print(f"  1. 在视频编辑器中使用检测到的场景边界")
    print(f"  2. 根据置信度和运动强度调整编辑策略")
    print(f"  3. 对于低置信度的场景，考虑手动审核")


def demo_method_comparison():
    """对比不同检测方法的性能"""
    print("=" * 80)
    print("场景检测方法性能对比")
    print("=" * 80)

    video_path = "data/input/sample.mp4"

    if not Path(video_path).exists():
        print(f"\n错误: 视频文件不存在 {video_path}")
        return

    methods = ["frame_diff", "histogram", "motion", "hybrid"]
    results = {}

    print(f"\n分析视频: {video_path}\n")

    for method in methods:
        print(f"测试 {method} 方法...", end=" ", flush=True)
        try:
            detector = SceneDetector(method=method, threshold=30.0)
            scenes = detector.detect_scenes(video_path)
            stats = detector.get_statistics(scenes)

            results[method] = {
                'scenes': len(scenes),
                'avg_duration': stats['average_duration'],
                'confidence': stats['confidence_stats']['average'],
                'types': stats['scene_types']
            }
            print("完成")
        except Exception as e:
            print(f"失败: {e}")

    # 显示对比结果
    print("\n" + "=" * 80)
    print("对比结果")
    print("=" * 80)
    print(f"\n{'方法':<15} {'场景数':<10} {'平均时长':<12} {'平均置信度':<12}")
    print("-" * 50)

    for method, result in results.items():
        if result:
            print(f"{method:<15} {result['scenes']:<10} "
                  f"{result['avg_duration']:<12.2f} {result['confidence']:<12.1%}")

    # 详细分析
    print("\n\n场景类型分布对比:\n")
    all_types = set()
    for result in results.values():
        if result:
            all_types.update(result['types'].keys())

    for scene_type in sorted(all_types):
        print(f"{scene_type}:")
        for method, result in results.items():
            if result:
                count = result['types'].get(scene_type, 0)
                print(f"  {method}: {count}")
        print()

    # 推荐
    print("=" * 80)
    print("推荐")
    print("=" * 80)
    print("""
对于不同的使用场景：
  - 快速处理：使用 frame_diff (最快)
  - 颜色敏感：使用 histogram (对颜色变化敏感)
  - 运动分析：使用 motion (检测运动变化)
  - 最佳精度：使用 hybrid (综合性能最好)
    """)


def main():
    """主函数"""
    if len(sys.argv) > 1:
        if sys.argv[1] == "compare":
            demo_method_comparison()
        else:
            print("未知命令")
    else:
        demo_scene_detection_workflow()


if __name__ == "__main__":
    main()
