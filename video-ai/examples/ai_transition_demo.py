#!/usr/bin/env python3
"""
AI 视频过渡演示

演示如何使用 latent blending 技术生成 AI 视频过渡。
包括基准测试、不同配置对比、视觉质量评估等。

使用方法:
    python ai_transition_demo.py --mode basic
    python ai_transition_demo.py --mode benchmark
    python ai_transition_demo.py --mode comparison
"""

import os
import sys
import argparse
import time
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

# 导入模块
try:
    from core.ai_transition import (
        AITransitionGenerator,
        TransitionConfig,
        create_ai_transition,
        TORCH_AVAILABLE,
        DIFFUSERS_AVAILABLE
    )
    print("✓ AI 过渡模块导入成功")
except ImportError as e:
    print(f"✗ 导入失败: {e}")
    print("\n请安装依赖:")
    print("  pip install torch torchvision")
    print("  pip install diffusers transformers accelerate")
    sys.exit(1)

try:
    from PIL import Image
except ImportError:
    print("✗ PIL 未安装: pip install pillow")
    sys.exit(1)


def check_environment():
    """检查运行环境"""
    print("\n=== 环境检查 ===")
    print(f"Torch 可用: {TORCH_AVAILABLE}")
    print(f"Diffusers 可用: {DIFFUSERS_AVAILABLE}")

    if TORCH_AVAILABLE:
        import torch
        print(f"CUDA 可用: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"CUDA 设备: {torch.cuda.get_device_name(0)}")
            print(f"CUDA 内存: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")

    if not (TORCH_AVAILABLE and DIFFUSERS_AVAILABLE):
        print("\n警告: 缺少必要依赖!")
        return False

    return True


def demo_basic(output_dir: str = "./output/ai_transitions"):
    """基础演示: 生成一个简单的 AI 过渡"""
    print("\n=== 基础演示 ===")
    print("生成简单的 AI 过渡...")

    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)

    # 配置 (MVP: 快速模式)
    config = TransitionConfig(
        model_name="stabilityai/sdxl-turbo",
        num_frames=5,  # 少量帧数用于快速测试
        num_inference_steps=2,  # SDXL Turbo 推荐 1-4 步
        height=512,
        width=512,
        device="cuda" if TORCH_AVAILABLE and __import__('torch').cuda.is_available() else "cpu"
    )

    print(f"配置: {config.num_frames} 帧, {config.num_inference_steps} 步, {config.height}x{config.width}")

    # 创建生成器
    generator = AITransitionGenerator(config=config, verbose=True)

    # 定义过渡
    prompt_start = "a peaceful sunset over calm ocean waters"
    prompt_end = "a vibrant starry night sky with milky way"

    print(f"\n起始: {prompt_start}")
    print(f"结束: {prompt_end}")

    # 生成过渡
    start_time = time.time()
    frames = generator.generate_transition(
        prompt_start=prompt_start,
        prompt_end=prompt_end
    )
    elapsed = time.time() - start_time

    print(f"\n✓ 生成完成! 耗时: {elapsed:.2f}s")
    print(f"  平均: {elapsed/len(frames):.2f}s/帧")

    # 保存帧
    generator.save_frames(frames, output_dir, prefix="basic")

    print(f"\n帧已保存到: {output_dir}/")

    # 创建 GIF (如果可能)
    try:
        gif_path = os.path.join(output_dir, "transition.gif")
        frames[0].save(
            gif_path,
            save_all=True,
            append_images=frames[1:],
            duration=200,  # 200ms 每帧
            loop=0
        )
        print(f"GIF 已保存: {gif_path}")
    except Exception as e:
        print(f"GIF 保存失败: {e}")

    # 清理
    generator.cleanup()

    return frames


def demo_benchmark(output_dir: str = "./output/ai_transitions"):
    """性能基准测试"""
    print("\n=== 性能基准测试 ===")

    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)

    # 测试配置
    configs = [
        {
            'name': 'MVP (超快)',
            'config': TransitionConfig(
                num_frames=5,
                num_inference_steps=2,
                height=512,
                width=512
            )
        },
        {
            'name': 'Balanced (平衡)',
            'config': TransitionConfig(
                num_frames=10,
                num_inference_steps=4,
                height=512,
                width=512
            )
        },
        # 注意: 高质量配置需要更多时间和内存
        # {
        #     'name': 'High Quality (高质量)',
        #     'config': TransitionConfig(
        #         num_frames=20,
        #         num_inference_steps=6,
        #         height=768,
        #         width=768
        #     )
        # }
    ]

    results = []

    for test in configs:
        print(f"\n测试: {test['name']}")
        print(f"  配置: {test['config'].num_frames} 帧, {test['config'].num_inference_steps} 步")

        generator = AITransitionGenerator(config=test['config'], verbose=False)

        # 运行基准测试
        benchmark_results = generator.benchmark()
        results.append({
            'name': test['name'],
            'results': benchmark_results
        })

        print(f"  总耗时: {benchmark_results['total_time']:.2f}s")
        print(f"  每帧: {benchmark_results['time_per_frame']:.2f}s")
        print(f"  内存: {benchmark_results['memory_used_gb']:.2f}GB")

        generator.cleanup()

    # 总结
    print("\n=== 基准测试总结 ===")
    print(f"{'配置':<20} {'总耗时':<12} {'每帧':<12} {'内存':<12}")
    print("-" * 60)
    for r in results:
        print(
            f"{r['name']:<20} "
            f"{r['results']['total_time']:<12.2f}s "
            f"{r['results']['time_per_frame']:<12.2f}s "
            f"{r['results']['memory_used_gb']:<12.2f}GB"
        )

    return results


def demo_comparison(output_dir: str = "./output/ai_transitions"):
    """对比不同插值方法"""
    print("\n=== 插值方法对比 ===")

    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)

    # 测试场景
    scenarios = [
        {
            'name': '自然场景',
            'start': 'a lush green forest in spring',
            'end': 'a snowy winter wonderland'
        },
        {
            'name': '城市景观',
            'start': 'a bustling city street at day',
            'end': 'the same street at night with neon lights'
        },
        {
            'name': '抽象艺术',
            'start': 'abstract geometric shapes in warm colors',
            'end': 'abstract flowing patterns in cool colors'
        }
    ]

    # 插值方法
    methods = ['linear', 'slerp']

    for scenario in scenarios[:1]:  # 只测试第一个场景以节省时间
        print(f"\n场景: {scenario['name']}")
        print(f"  起始: {scenario['start']}")
        print(f"  结束: {scenario['end']}")

        for method in methods:
            print(f"\n  方法: {method.upper()}")

            config = TransitionConfig(
                num_frames=5,
                num_inference_steps=2,
                interpolation_method=method,
                height=512,
                width=512
            )

            generator = AITransitionGenerator(config=config, verbose=False)

            start_time = time.time()
            frames = generator.generate_transition(
                prompt_start=scenario['start'],
                prompt_end=scenario['end']
            )
            elapsed = time.time() - start_time

            # 保存
            method_dir = os.path.join(output_dir, f"comparison_{method}")
            generator.save_frames(frames, method_dir, prefix=scenario['name'].replace(' ', '_'))

            print(f"    耗时: {elapsed:.2f}s")
            print(f"    保存至: {method_dir}/")

            generator.cleanup()


def demo_video_integration(output_dir: str = "./output/ai_transitions"):
    """演示与视频编辑的集成"""
    print("\n=== 视频集成演示 ===")

    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)

    try:
        from core.generator import TransitionGenerator
        print("✓ TransitionGenerator 导入成功")
    except ImportError as e:
        print(f"✗ 导入失败: {e}")
        return

    # 测试 AI 过渡是否已集成
    print("\n测试 AI 过渡集成...")

    try:
        # 创建 AI 过渡生成器
        gen = TransitionGenerator(
            transition_style="ai_generated",
            duration=1.0,
            enable_ai=True
        )

        if gen.ai_available:
            print("✓ AI 过渡已启用")

            # 测试生成
            print("\n生成测试过渡...")
            # 注意: 这需要 moviepy 支持
            # transition_clip = gen.create_transition(
            #     prompt_start="a beautiful beach",
            #     prompt_end="a mountain landscape",
            #     size=(512, 512)
            # )
            # print("✓ 过渡生成成功")

        else:
            print("✗ AI 过渡不可用")

    except Exception as e:
        print(f"集成测试失败: {e}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="AI 视频过渡演示")
    parser.add_argument(
        '--mode',
        choices=['basic', 'benchmark', 'comparison', 'integration', 'all'],
        default='basic',
        help='演示模式'
    )
    parser.add_argument(
        '--output',
        default='./output/ai_transitions',
        help='输出目录'
    )

    args = parser.parse_args()

    # 欢迎信息
    print("=" * 60)
    print("AI 视频过渡演示 - Latent Blending")
    print("=" * 60)

    # 检查环境
    if not check_environment():
        print("\n环境检查失败，退出")
        sys.exit(1)

    # 运行演示
    if args.mode == 'basic' or args.mode == 'all':
        demo_basic(args.output)

    if args.mode == 'benchmark' or args.mode == 'all':
        demo_benchmark(args.output)

    if args.mode == 'comparison' or args.mode == 'all':
        demo_comparison(args.output)

    if args.mode == 'integration' or args.mode == 'all':
        demo_video_integration(args.output)

    print("\n" + "=" * 60)
    print("演示完成!")
    print("=" * 60)


if __name__ == "__main__":
    main()
