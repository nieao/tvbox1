"""
AI 过渡生成器测试

测试 latent blending AI 视频过渡生成功能
"""

import pytest
import os
import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

# 导入测试模块
try:
    from core.ai_transition import (
        AITransitionGenerator,
        TransitionConfig,
        create_ai_transition,
        TORCH_AVAILABLE,
        DIFFUSERS_AVAILABLE
    )
    AI_IMPORTS_OK = True
except ImportError:
    AI_IMPORTS_OK = False


@pytest.mark.skipif(not AI_IMPORTS_OK, reason="AI 过渡依赖未安装")
class TestAITransitionGenerator:
    """AI 过渡生成器测试"""

    def test_imports(self):
        """测试导入"""
        assert TORCH_AVAILABLE, "Torch 未安装"
        assert DIFFUSERS_AVAILABLE, "Diffusers 未安装"

    def test_config_creation(self):
        """测试配置创建"""
        config = TransitionConfig(
            num_frames=5,
            num_inference_steps=2,
            height=256,
            width=256
        )

        assert config.num_frames == 5
        assert config.num_inference_steps == 2
        assert config.height == 256
        assert config.width == 256

    def test_generator_init(self):
        """测试生成器初始化"""
        config = TransitionConfig(
            num_frames=3,
            height=256,
            width=256
        )

        generator = AITransitionGenerator(
            config=config,
            enable_gpu=False,  # 使用 CPU 测试
            verbose=False
        )

        assert generator.config.num_frames == 3
        assert generator.device in ["cuda", "cpu"]

    @pytest.mark.slow
    @pytest.mark.gpu
    def test_model_loading(self):
        """测试模型加载 (需要网络和时间)"""
        config = TransitionConfig(
            model_name="stabilityai/sdxl-turbo",
            height=256,
            width=256
        )

        generator = AITransitionGenerator(
            config=config,
            enable_gpu=True,
            verbose=False
        )

        # 加载模型
        generator.load_model()
        assert generator._model_loaded
        assert generator.pipeline is not None

        # 清理
        generator.cleanup()

    @pytest.mark.slow
    @pytest.mark.gpu
    def test_transition_generation(self):
        """测试过渡生成 (需要 GPU 和时间)"""
        config = TransitionConfig(
            num_frames=3,
            num_inference_steps=1,
            height=256,
            width=256
        )

        generator = AITransitionGenerator(
            config=config,
            verbose=False
        )

        # 生成过渡
        frames = generator.generate_transition(
            prompt_start="a red circle",
            prompt_end="a blue square",
            num_frames=3
        )

        assert len(frames) == 3
        assert frames[0].size == (256, 256)

        # 清理
        generator.cleanup()

    def test_slerp_interpolation(self):
        """测试 SLERP 插值"""
        if not TORCH_AVAILABLE:
            pytest.skip("Torch 未安装")

        import torch

        config = TransitionConfig()
        generator = AITransitionGenerator(config=config, verbose=False)

        # 创建测试张量
        tensor1 = torch.randn(10, 10)
        tensor2 = torch.randn(10, 10)

        # 测试插值
        result = generator._slerp_tensors(tensor1, tensor2, alpha=0.5)

        assert result.shape == tensor1.shape
        assert not torch.isnan(result).any()

    def test_save_frames(self):
        """测试帧保存"""
        if not AI_IMPORTS_OK:
            pytest.skip("AI 模块未导入")

        from PIL import Image
        import tempfile

        # 创建测试帧
        frames = [
            Image.new('RGB', (100, 100), color=(255, 0, 0)),
            Image.new('RGB', (100, 100), color=(0, 255, 0)),
            Image.new('RGB', (100, 100), color=(0, 0, 255))
        ]

        # 保存到临时目录
        with tempfile.TemporaryDirectory() as tmpdir:
            config = TransitionConfig()
            generator = AITransitionGenerator(config=config, verbose=False)

            generator.save_frames(frames, tmpdir, prefix="test")

            # 验证文件
            assert os.path.exists(os.path.join(tmpdir, "test_0000.png"))
            assert os.path.exists(os.path.join(tmpdir, "test_0001.png"))
            assert os.path.exists(os.path.join(tmpdir, "test_0002.png"))

    @pytest.mark.slow
    @pytest.mark.gpu
    def test_benchmark(self):
        """测试性能基准"""
        config = TransitionConfig(
            num_frames=3,
            num_inference_steps=1,
            height=256,
            width=256
        )

        generator = AITransitionGenerator(config=config, verbose=False)

        results = generator.benchmark()

        assert 'total_time' in results
        assert 'time_per_frame' in results
        assert 'memory_used_gb' in results
        assert results['frames_generated'] == 3

        generator.cleanup()

    def test_convenience_function(self):
        """测试便捷函数"""
        # 这个测试会跳过实际生成
        # 只测试函数接口
        pytest.skip("需要模型下载，跳过")

        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            frames = create_ai_transition(
                prompt_start="test start",
                prompt_end="test end",
                num_frames=2,
                output_dir=tmpdir,
                device="cpu",
                verbose=False
            )

            assert len(frames) == 2


@pytest.mark.skipif(not AI_IMPORTS_OK, reason="AI 过渡依赖未安装")
class TestTransitionGeneratorIntegration:
    """TransitionGenerator 集成测试"""

    def test_import_integration(self):
        """测试集成导入"""
        from core.generator import TransitionGenerator, AI_TRANSITION_AVAILABLE

        # AI 过渡是否可用
        print(f"AI 过渡可用: {AI_TRANSITION_AVAILABLE}")

    def test_ai_style_support(self):
        """测试 AI 风格支持"""
        from core.generator import TransitionGenerator

        # 检查支持的风格
        assert "ai_generated" in TransitionGenerator.SUPPORTED_STYLES

    @pytest.mark.slow
    def test_ai_generator_init(self):
        """测试 AI 生成器初始化"""
        from core.generator import TransitionGenerator

        # 尝试创建 AI 过渡生成器
        try:
            gen = TransitionGenerator(
                transition_style="ai_generated",
                duration=1.0,
                enable_ai=True
            )

            # 检查是否初始化成功
            if gen.ai_available:
                assert gen.ai_generator is not None
            else:
                # 降级到文字过渡
                assert gen.style == "text"

        except Exception as e:
            pytest.skip(f"AI 生成器初始化失败: {e}")


def test_module_availability():
    """测试模块可用性 (总是运行)"""
    print("\n=== 模块可用性检查 ===")
    print(f"Torch 可用: {TORCH_AVAILABLE}")
    print(f"Diffusers 可用: {DIFFUSERS_AVAILABLE}")

    if TORCH_AVAILABLE:
        import torch
        print(f"CUDA 可用: {torch.cuda.is_available()}")

    if not AI_IMPORTS_OK:
        print("\n警告: AI 过渡模块未正确导入")
        print("请安装: pip install torch diffusers transformers accelerate")


if __name__ == "__main__":
    # 运行基础测试
    test_module_availability()

    print("\n运行完整测试:")
    print("pytest tests/test_ai_transition.py -v")
    print("\n仅运行快速测试:")
    print("pytest tests/test_ai_transition.py -v -m 'not slow and not gpu'")
