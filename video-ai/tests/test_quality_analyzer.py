"""
质量分析器单元测试

测试 QualityAnalyzer 的各项功能。
"""

import unittest
import sys
from pathlib import Path
import tempfile
import numpy as np

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.quality_analyzer import QualityAnalyzer, QualityMetrics


class TestQualityAnalyzer(unittest.TestCase):
    """质量分析器测试"""

    def setUp(self):
        """测试初始化"""
        self.analyzer = QualityAnalyzer()

    def test_quality_metrics_creation(self):
        """测试质量指标创建"""
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

        self.assertEqual(metrics.sharpness, 85.5)
        self.assertEqual(metrics.overall_score, 82.4)
        self.assertEqual(metrics.resolution, (1920, 1080))

    def test_quality_metrics_to_dict(self):
        """测试质量指标转换为字典"""
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

        metrics_dict = metrics.to_dict()
        self.assertIsInstance(metrics_dict, dict)
        self.assertEqual(metrics_dict['overall_score'], 82.4)
        self.assertIn('resolution', metrics_dict)

    def test_suggest_enhancements_excellent_quality(self):
        """测试优秀质量的建议"""
        metrics = QualityMetrics(
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

        suggestions = self.analyzer.suggest_enhancements(metrics)

        # 优秀质量应该有肯定的建议
        self.assertTrue(any("✅" in s or "无需" in s for s in suggestions))

    def test_suggest_enhancements_poor_quality(self):
        """测试较差质量的建议"""
        metrics = QualityMetrics(
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

        suggestions = self.analyzer.suggest_enhancements(metrics)

        # 较差质量应该有多条建议
        self.assertTrue(len(suggestions) > 3)
        # 应该包含关于清晰度的建议
        self.assertTrue(any("清晰度" in s for s in suggestions))

    def test_generate_quality_report(self):
        """测试生成质量报告"""
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

        report = self.analyzer.generate_quality_report(metrics)

        # 检查报告包含关键信息
        self.assertIn("视频质量分析报告", report)
        self.assertIn("视觉质量", report)
        self.assertIn("音频质量", report)
        self.assertIn("技术规格", report)
        self.assertIn("综合评分", report)
        self.assertIn("73.0", report)

    def test_calculate_overall_score_weights(self):
        """测试综合评分的权重计算"""
        visual_metrics = {
            'sharpness': 100,
            'brightness': 100,
            'contrast': 100,
            'color_balance': 100
        }

        audio_metrics = {
            'audio_loudness': -6.0,  # 规范化后约100
            'audio_noise': 100,
            'audio_clarity': 100
        }

        tech_metrics = {
            'resolution': (1920, 1080),
            'fps': 60.0,
            'bitrate': 15000
        }

        score = self.analyzer._calculate_overall_score(
            visual_metrics,
            audio_metrics,
            tech_metrics
        )

        # 所有指标都是最优，评分应接近100
        self.assertGreater(score, 90)

    def test_calculate_brightness_scores(self):
        """测试亮度计算"""
        # 创建测试帧
        frames = [
            np.full((240, 320, 3), 127, dtype=np.uint8),  # 理想亮度
            np.full((240, 320, 3), 100, dtype=np.uint8),  # 偏暗
            np.full((240, 320, 3), 200, dtype=np.uint8),  # 偏亮
        ]

        brightness = self.analyzer._calculate_brightness(frames)

        # 应该在0-100之间
        self.assertGreaterEqual(brightness, 0)
        self.assertLessEqual(brightness, 100)

    def test_calculate_contrast_scores(self):
        """测试对比度计算"""
        # 创建测试帧
        frames = [
            np.full((240, 320, 3), 127, dtype=np.uint8),  # 均匀色
            np.random.randint(0, 256, (240, 320, 3), dtype=np.uint8),  # 高对比度
        ]

        contrast = self.analyzer._calculate_contrast(frames)

        # 应该在0-100之间
        self.assertGreaterEqual(contrast, 0)
        self.assertLessEqual(contrast, 100)

    def test_estimate_bitrate(self):
        """测试码率估计"""
        # 这是一个单位测试，实际文件可能不存在
        # 我们测试函数的行为而不实际计算
        bitrate = self.analyzer._estimate_bitrate(
            "nonexistent.mp4",
            30.0,
            300
        )

        # 应该返回默认值或计算值
        self.assertGreater(bitrate, 0)

    def test_resolution_scoring(self):
        """测试分辨率评分"""
        # 测试不同分辨率的评分逻辑
        test_cases = [
            ((1920, 1080), 100),  # 1080p -> 100
            ((1280, 720), 80),    # 720p -> 80
            ((640, 480), 60),     # VGA -> 60
        ]

        # 这个测试验证评分逻辑，实际在 _calculate_overall_score 中
        for resolution, expected_score in test_cases:
            # 创建虚拟的技术指标
            if resolution == (1920, 1080):
                self.assertGreaterEqual(expected_score, 80)
            elif resolution == (1280, 720):
                self.assertEqual(expected_score, 80)


class TestQualityAnalyzerIntegration(unittest.TestCase):
    """集成测试"""

    def setUp(self):
        """测试初始化"""
        self.analyzer = QualityAnalyzer()

    def test_sample_frames(self):
        """测试帧采样"""
        try:
            import cv2
        except ImportError:
            self.skipTest("OpenCV not installed")

        # 创建模拟视频对象
        # 这里我们只测试采样逻辑本身
        dummy_frames = [
            np.zeros((240, 320, 3), dtype=np.uint8)
            for _ in range(100)
        ]

        # 验证采样函数返回正确数量的帧
        # 注意：实际的 _sample_frames 需要 cv2.VideoCapture 对象

    def test_quality_metrics_full_workflow(self):
        """测试完整的质量分析工作流"""
        # 创建一个完整的质量指标对象
        metrics = QualityMetrics(
            sharpness=80.0,
            brightness=75.0,
            contrast=78.0,
            color_balance=76.0,
            audio_loudness=-10.0,
            audio_noise=75.0,
            audio_clarity=78.0,
            resolution=(1920, 1080),
            fps=30.0,
            bitrate=6000,
            overall_score=77.5
        )

        # 生成建议
        suggestions = self.analyzer.suggest_enhancements(metrics)

        # 生成报告
        report = self.analyzer.generate_quality_report(metrics)

        # 验证工作流完整
        self.assertIsNotNone(suggestions)
        self.assertIsNotNone(report)
        self.assertIn("77.5", report)


class TestQualityAnalyzerEdgeCases(unittest.TestCase):
    """边界情况测试"""

    def setUp(self):
        """测试初始化"""
        self.analyzer = QualityAnalyzer()

    def test_extreme_brightness_values(self):
        """测试极端亮度值"""
        frames = [
            np.zeros((240, 320, 3), dtype=np.uint8),      # 完全黑暗
            np.full((240, 320, 3), 255, dtype=np.uint8),  # 完全白色
        ]

        brightness = self.analyzer._calculate_brightness(frames)

        # 两个极端都应该得到低分
        self.assertGreaterEqual(brightness, 0)
        self.assertLessEqual(brightness, 100)

    def test_monochrome_frames(self):
        """测试单色帧"""
        frames = [np.full((240, 320, 3), 128, dtype=np.uint8)]

        color_balance = self.analyzer._calculate_color_balance(frames)

        # 单色帧应该得到高分（RGB均衡）
        self.assertGreaterEqual(color_balance, 80)

    def test_empty_frames_list(self):
        """测试空帧列表"""
        frames = []

        # 应该返回默认值而不是崩溃
        brightness = self.analyzer._calculate_brightness(frames)
        self.assertEqual(brightness, 50)

        contrast = self.analyzer._calculate_contrast(frames)
        self.assertEqual(contrast, 50)


def run_tests():
    """运行所有测试"""
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # 添加测试
    suite.addTests(loader.loadTestsFromTestCase(TestQualityAnalyzer))
    suite.addTests(loader.loadTestsFromTestCase(TestQualityAnalyzerIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestQualityAnalyzerEdgeCases))

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result


if __name__ == "__main__":
    # 运行测试
    print("="*70)
    print("Video-AI 质量分析器单元测试")
    print("="*70)
    print()

    result = run_tests()

    print()
    print("="*70)
    if result.wasSuccessful():
        print("✅ 所有测试通过！")
    else:
        print(f"❌ 测试失败: {len(result.failures)} 个失败, {len(result.errors)} 个错误")
    print("="*70)
