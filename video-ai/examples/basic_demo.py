"""
基础示例：使用 Video-AI 处理视频

这个示例展示了如何使用 Video-AI 的基本功能来处理视频。
"""

import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.editor import VideoEditor
from src.services.personalization import PersonalizationConfig


def basic_example():
    """基础示例：简单的视频处理"""
    print("=" * 60)
    print("Video-AI 基础示例")
    print("=" * 60)

    # 创建视频编辑器，配置用户兴趣
    editor = VideoEditor(
        user_interests=["编程", "AI", "技术"],
        output_length="medium"  # short, medium, long
    )

    # 处理视频
    # 注意：需要替换为实际的视频路径
    input_video = "data/input/sample.mp4"
    output_video = "data/output/edited_sample.mp4"

    print(f"\n输入视频: {input_video}")
    print(f"输出视频: {output_video}\n")

    # 检查输入文件是否存在
    if not Path(input_video).exists():
        print(f"错误: 输入视频不存在: {input_video}")
        print("\n请将视频文件放到 data/input/ 目录下")
        return

    try:
        result = editor.process_video(input_video, output_video)

        print("\n处理结果:")
        print(f"  原始时长: {result.original_duration:.1f} 秒")
        print(f"  剪辑后时长: {result.edited_duration:.1f} 秒")
        print(f"  压缩率: {result.compression_ratio:.1%}")
        print(f"  信息密度提升: {result.density_improvement:.1%}")
        print(f"  片段数量: {result.segments_count}")

    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()


def advanced_example():
    """高级示例：使用个性化配置"""
    print("\n" + "=" * 60)
    print("Video-AI 高级示例 - 个性化配置")
    print("=" * 60)

    # 创建个性化配置
    config = PersonalizationConfig(
        interests=["深度学习", "计算机视觉", "自然语言处理"],
        skip_topics=["广告", "闲聊", "推广"],
        pace="fast",
        transition_style="text",
        language="zh-CN",
        output_length="short"
    )

    print("\n个性化配置:")
    print(f"  兴趣标签: {', '.join(config.interests)}")
    print(f"  跳过主题: {', '.join(config.skip_topics)}")
    print(f"  播放速度: {config.pace}")
    print(f"  过渡风格: {config.transition_style}")
    print(f"  输出长度: {config.output_length}")

    # 使用配置创建编辑器
    editor = VideoEditor(config=config)

    input_video = "data/input/lecture.mp4"
    output_video = "data/output/edited_lecture.mp4"

    if not Path(input_video).exists():
        print(f"\n错误: 输入视频不存在: {input_video}")
        return

    try:
        result = editor.process_video(input_video, output_video)
        print("\n处理完成！")

    except Exception as e:
        print(f"错误: {e}")


def preview_example():
    """预览示例：不实际剪辑，只显示预览信息"""
    print("\n" + "=" * 60)
    print("Video-AI 预览示例")
    print("=" * 60)

    editor = VideoEditor(
        user_interests=["Python", "编程教程"],
        output_length="medium"
    )

    input_video = "data/input/tutorial.mp4"

    if not Path(input_video).exists():
        print(f"\n错误: 输入视频不存在: {input_video}")
        return

    try:
        # 获取预览信息（不实际剪辑）
        preview = editor.get_preview(input_video, num_segments=5)

        print("\n视频预览:")
        print(f"  原始时长: {preview['original_duration']:.1f} 秒")
        print(f"  预计剪辑后时长: {preview['estimated_duration']:.1f} 秒")
        print(f"  预计压缩率: {preview['compression_ratio']:.1%}")
        print(f"\n主要主题:")
        for topic in preview['main_topics']:
            print(f"    - {topic}")

        print(f"\n内容摘要:")
        print(f"  {preview['summary']}")

        print(f"\n关键片段预览:")
        for i, segment in enumerate(preview['key_segments'], 1):
            print(f"  {i}. [{segment['start']:.1f}s - {segment['end']:.1f}s] "
                  f"{segment['topic']}")
            print(f"     相关性: {segment['relevance']:.2f}")
            print(f"     内容: {segment['text']}")
            print()

    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()


def batch_processing_example():
    """批量处理示例"""
    print("\n" + "=" * 60)
    print("Video-AI 批量处理示例")
    print("=" * 60)

    editor = VideoEditor(
        user_interests=["教育", "学习"],
        output_length="medium"
    )

    input_dir = "data/input"
    output_dir = "data/output/batch"

    print(f"\n输入目录: {input_dir}")
    print(f"输出目录: {output_dir}")

    try:
        results = editor.batch_process(input_dir, output_dir)

        print("\n批量处理完成！")
        print(f"共处理 {len(results)} 个视频")

        total_original = sum(r.original_duration for r in results)
        total_edited = sum(r.edited_duration for r in results)

        print(f"\n总计:")
        print(f"  原始总时长: {total_original/60:.1f} 分钟")
        print(f"  剪辑后总时长: {total_edited/60:.1f} 分钟")
        print(f"  节省时间: {(total_original - total_edited)/60:.1f} 分钟")

    except Exception as e:
        print(f"错误: {e}")


if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║             Video-AI 示例程序                            ║
    ║                                                          ║
    ║     个性化智能视频编辑系统                                ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """)

    print("\n请选择要运行的示例:")
    print("  1. 基础示例 - 简单视频处理")
    print("  2. 高级示例 - 个性化配置")
    print("  3. 预览示例 - 查看预览信息")
    print("  4. 批量处理示例")
    print("  0. 退出")

    choice = input("\n请输入选项 (0-4): ").strip()

    examples = {
        "1": basic_example,
        "2": advanced_example,
        "3": preview_example,
        "4": batch_processing_example
    }

    if choice in examples:
        examples[choice]()
    elif choice == "0":
        print("再见！")
    else:
        print("无效选项")
