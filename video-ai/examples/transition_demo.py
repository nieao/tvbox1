"""
视频过渡效果演示脚本

展示 TransitionGenerator 的各种过渡效果和文字模板。
"""

import os
import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.generator import TransitionGenerator


def demo_text_transitions():
    """演示文字过渡效果"""
    print("\n" + "=" * 60)
    print("演示 1: 文字过渡 - 各种模板")
    print("=" * 60)

    generator = TransitionGenerator(
        transition_style="text",
        duration=2.0
    )

    templates = ["minimal", "modern", "classic", "colorful", "info_card"]
    size = (1920, 1080)

    for template in templates:
        print(f"\n创建 '{template}' 模板的过渡...")
        try:
            transition = generator.create_transition(
                text=f"第二部分：深度学习",
                size=size,
                template=template
            )
            print(f"  ✓ 成功创建 {template} 过渡")
            print(f"    时长: {transition.duration}秒")
            print(f"    尺寸: {transition.size}")

            # 保存预览帧（如果需要）
            # transition.save_frame("frame.png", t=1.0)

        except Exception as e:
            print(f"  ✗ 创建失败: {e}")


def demo_other_transitions():
    """演示其他类型的过渡"""
    print("\n" + "=" * 60)
    print("演示 2: 其他过渡类型")
    print("=" * 60)

    styles = ["fade", "blur", "zoom", "gradient"]
    size = (1920, 1080)

    for style in styles:
        print(f"\n创建 '{style}' 过渡...")
        try:
            generator = TransitionGenerator(
                transition_style=style,
                duration=1.5
            )

            transition = generator.create_transition(size=size)
            print(f"  ✓ 成功创建 {style} 过渡")
            print(f"    时长: {transition.duration}秒")
            print(f"    尺寸: {transition.size}")

        except Exception as e:
            print(f"  ✗ 创建失败: {e}")


def demo_apply_to_clips():
    """演示将过渡应用于多个片段"""
    print("\n" + "=" * 60)
    print("演示 3: 为多个片段添加过渡")
    print("=" * 60)

    generator = TransitionGenerator(
        transition_style="text",
        duration=2.0
    )

    # 模拟视频片段
    class MockClip:
        def __init__(self, name, duration=5.0):
            self.name = name
            self.duration = duration
            self.size = (1920, 1080)

        def __repr__(self):
            return f"<Clip: {self.name} ({self.duration}s)>"

    clips = [
        MockClip("介绍部分", 5.0),
        MockClip("第一部分：基础概念", 8.0),
        MockClip("第二部分：深度学习", 10.0),
        MockClip("总结部分", 5.0),
    ]

    topics = ["基础概念", "深度学习", "实践应用"]

    print(f"\n原始片段数: {len(clips)}")
    for clip in clips:
        print(f"  - {clip}")

    try:
        # 应用过渡（注意：这会返回包含过渡的片段列表）
        result_clips = generator.apply_to_clips(clips, topics)

        print(f"\n添加过渡后的片段数: {len(result_clips)}")
        print("\n预期片段结构:")
        for i, clip in enumerate(result_clips):
            if isinstance(clip, MockClip):
                print(f"  {i+1}. {clip}")
            else:
                print(f"  {i+1}. <过渡片段>")

    except Exception as e:
        print(f"应用过渡失败: {e}")


def demo_custom_parameters():
    """演示自定义参数"""
    print("\n" + "=" * 60)
    print("演示 4: 自定义参数")
    print("=" * 60)

    # 不同的过渡时长
    durations = [1.0, 2.0, 3.0]

    for duration in durations:
        print(f"\n创建时长 {duration}s 的文字过渡...")
        try:
            generator = TransitionGenerator(
                transition_style="text",
                duration=duration
            )

            transition = generator.create_transition(
                text=f"过渡时长: {duration}秒",
                template="modern"
            )
            print(f"  ✓ 成功创建")
            print(f"    实际时长: {transition.duration}秒")

        except Exception as e:
            print(f"  ✗ 创建失败: {e}")


def demo_error_handling():
    """演示错误处理"""
    print("\n" + "=" * 60)
    print("演示 5: 错误处理")
    print("=" * 60)

    # 无效的过渡类型
    print("\n1. 测试无效的过渡类型...")
    try:
        generator = TransitionGenerator(
            transition_style="invalid_style"
        )
        print("  ✗ 应该抛出异常但没有")
    except ValueError as e:
        print(f"  ✓ 正确抛出异常: {e}")

    # 无效的模板
    print("\n2. 测试无效的模板...")
    try:
        generator = TransitionGenerator(
            transition_style="text",
            duration=2.0
        )
        transition = generator.create_transition(
            text="测试",
            template="invalid_template"
        )
        print("  ✓ 自动使用默认模板")

    except Exception as e:
        print(f"  ✗ 异常: {e}")

    # 缺少文字参数
    print("\n3. 测试文字过渡但不提供文字...")
    try:
        generator = TransitionGenerator(
            transition_style="text",
            duration=2.0
        )
        transition = generator.create_transition()
        print(f"  ✓ 使用默认文字: '继续'")

    except Exception as e:
        print(f"  ✗ 异常: {e}")


def print_summary():
    """打印总结信息"""
    print("\n" + "=" * 60)
    print("过渡生成器功能总结")
    print("=" * 60)

    print("\n支持的过渡类型:")
    print("  - text: 文字过渡（支持 5 种模板）")
    print("  - fade: 淡入淡出过渡")
    print("  - blur: 模糊过渡")
    print("  - zoom: 缩放过渡")
    print("  - gradient: 渐变过渡")

    print("\n支持的文字模板:")
    print("  - minimal: 简约风格（白底黑字）")
    print("  - modern: 现代风格（渐变背景）")
    print("  - classic: 经典风格（黑底白字）")
    print("  - colorful: 彩色风格（彩虹渐变）")
    print("  - info_card: 信息卡片风格")

    print("\n主要方法:")
    print("  - create_transition(): 创建单个过渡")
    print("  - apply_to_clips(): 为多个片段添加过渡")

    print("\n集成方式:")
    print("  VideoEditor 已集成 TransitionGenerator")
    print("  可通过 transition_style 和 transition_template 参数配置")

    print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":
    print("\n开始演示 TransitionGenerator")
    print("=" * 60)

    # 运行各个演示
    try:
        demo_text_transitions()
    except Exception as e:
        print(f"演示 1 失败: {e}")

    try:
        demo_other_transitions()
    except Exception as e:
        print(f"演示 2 失败: {e}")

    try:
        demo_apply_to_clips()
    except Exception as e:
        print(f"演示 3 失败: {e}")

    try:
        demo_custom_parameters()
    except Exception as e:
        print(f"演示 4 失败: {e}")

    try:
        demo_error_handling()
    except Exception as e:
        print(f"演示 5 失败: {e}")

    # 打印总结
    print_summary()

    print("演示完成！")
