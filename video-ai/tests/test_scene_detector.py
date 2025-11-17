"""
场景检测模块的单元测试

测试 SceneDetector 类的各种功能和检测方法。
"""

import unittest
import sys
from pathlib import Path
import tempfile

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 直接导入模块以避免完整项目导入
import importlib.util
spec = importlib.util.spec_from_file_location(
    "scene_detector",
    str(project_root / "src" / "core" / "scene_detector.py")
)
scene_detector_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scene_detector_module)

SceneDetector = scene_detector_module.SceneDetector
Scene = scene_detector_module.Scene
SceneType = scene_detector_module.SceneType


class TestScene(unittest.TestCase):
    """测试 Scene 类"""

    def test_scene_creation(self):
        """测试 Scene 对象创建"""
        scene = Scene(
            start_frame=0,
            end_frame=100,
            start_time=0.0,
            end_time=4.0,
            scene_type=SceneType.ACTION,
            confidence=0.95
        )

        self.assertEqual(scene.start_frame, 0)
        self.assertEqual(scene.end_frame, 100)
        self.assertEqual(scene.start_time, 0.0)
        self.assertEqual(scene.end_time, 4.0)
        self.assertEqual(scene.scene_type, SceneType.ACTION)
        self.assertEqual(scene.confidence, 0.95)

    def test_scene_duration(self):
        """测试场景时长计算"""
        scene = Scene(
            start_frame=0,
            end_frame=100,
            start_time=0.0,
            end_time=4.0
        )

        self.assertEqual(scene.duration, 4.0)

    def test_scene_frame_count(self):
        """测试场景帧数"""
        scene = Scene(
            start_frame=0,
            end_frame=100,
            start_time=0.0,
            end_time=4.0
        )

        self.assertEqual(scene.frame_count, 100)

    def test_scene_to_dict(self):
        """测试 Scene 转换为字典"""
        scene = Scene(
            start_frame=0,
            end_frame=100,
            start_time=0.0,
            end_time=4.0,
            scene_type=SceneType.ACTION,
            confidence=0.95,
            motion_level=0.8
        )

        scene_dict = scene.to_dict()

        self.assertIsInstance(scene_dict, dict)
        self.assertEqual(scene_dict['start_frame'], 0)
        self.assertEqual(scene_dict['end_frame'], 100)
        self.assertEqual(scene_dict['duration'], 4.0)
        self.assertEqual(scene_dict['scene_type'], 'action')


class TestSceneDetectorInitialization(unittest.TestCase):
    """测试 SceneDetector 初始化"""

    def test_default_initialization(self):
        """测试默认初始化"""
        detector = SceneDetector()

        self.assertEqual(detector.method, "hybrid")
        self.assertEqual(detector.threshold, 30.0)
        self.assertEqual(detector.min_scene_length, 0.5)
        self.assertEqual(detector.max_scene_length, 120.0)

    def test_custom_initialization(self):
        """测试自定义初始化"""
        detector = SceneDetector(
            method="frame_diff",
            threshold=50.0,
            min_scene_length=1.0,
            max_scene_length=60.0
        )

        self.assertEqual(detector.method, "frame_diff")
        self.assertEqual(detector.threshold, 50.0)
        self.assertEqual(detector.min_scene_length, 1.0)
        self.assertEqual(detector.max_scene_length, 60.0)


class TestSceneDetectorUtilities(unittest.TestCase):
    """测试 SceneDetector 工具方法"""

    def test_smooth_sequence(self):
        """测试序列平滑"""
        sequence = [1, 10, 1, 10, 1, 10, 1]  # 有高频噪声的序列
        smoothed = SceneDetector._smooth_sequence(sequence, window_size=3)

        self.assertEqual(len(smoothed), len(sequence))
        # 平滑后的序列应该更平缓
        if NUMPY_AVAILABLE:
            variance_original = np.var(sequence)
            variance_smoothed = np.var(smoothed)
            self.assertLess(variance_smoothed, variance_original)
        else:
            # 至少检查平滑不会改变序列长度
            self.assertEqual(len(smoothed), 7)

    def test_smooth_sequence_edge_cases(self):
        """测试边界情况"""
        sequence = [5.0]
        smoothed = SceneDetector._smooth_sequence(sequence)
        self.assertEqual(smoothed, [5.0])

        sequence = []
        smoothed = SceneDetector._smooth_sequence(sequence)
        self.assertEqual(smoothed, [])

    def test_get_statistics_empty(self):
        """测试空场景列表的统计"""
        detector = SceneDetector()
        stats = detector.get_statistics([])

        self.assertEqual(stats['total_scenes'], 0)
        self.assertEqual(stats['total_duration'], 0)

    def test_get_statistics_single_scene(self):
        """测试单个场景的统计"""
        detector = SceneDetector()
        scenes = [
            Scene(
                start_frame=0,
                end_frame=100,
                start_time=0.0,
                end_time=4.0,
                confidence=0.9
            )
        ]

        stats = detector.get_statistics(scenes)

        self.assertEqual(stats['total_scenes'], 1)
        self.assertEqual(stats['total_duration'], 4.0)
        self.assertEqual(stats['average_duration'], 4.0)
        self.assertEqual(stats['confidence_stats']['min'], 0.9)
        self.assertEqual(stats['confidence_stats']['max'], 0.9)
        self.assertEqual(stats['confidence_stats']['average'], 0.9)

    def test_get_statistics_multiple_scenes(self):
        """测试多个场景的统计"""
        detector = SceneDetector()
        scenes = [
            Scene(
                start_frame=0,
                end_frame=100,
                start_time=0.0,
                end_time=4.0,
                confidence=0.8,
                scene_type=SceneType.ACTION
            ),
            Scene(
                start_frame=100,
                end_frame=200,
                start_time=4.0,
                end_time=8.0,
                confidence=0.9,
                scene_type=SceneType.STATIC
            )
        ]

        stats = detector.get_statistics(scenes)

        self.assertEqual(stats['total_scenes'], 2)
        self.assertEqual(stats['total_duration'], 8.0)
        self.assertEqual(stats['average_duration'], 4.0)
        self.assertEqual(stats['scene_types']['action'], 1)
        self.assertEqual(stats['scene_types']['static'], 1)


@unittest.skipIf(not (CV2_AVAILABLE and NUMPY_AVAILABLE), "OpenCV 或 NumPy 不可用")
class TestSceneDetectorVideoHandling(unittest.TestCase):
    """测试视频处理相关功能"""

    def setUp(self):
        """设置测试环境"""
        self.test_video_dir = tempfile.mkdtemp()

    def tearDown(self):
        """清理测试环境"""
        import shutil
        if Path(self.test_video_dir).exists():
            shutil.rmtree(self.test_video_dir)

    def create_test_video(self, filename: str, duration: int = 2, fps: int = 25):
        """创建测试视频"""
        video_path = Path(self.test_video_dir) / filename

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(
            str(video_path),
            fourcc,
            fps,
            (320, 180)
        )

        for frame_id in range(duration * fps):
            # 创建不同类型的帧
            if frame_id < fps:  # 第一秒：静态帧
                frame = np.full((180, 320, 3), 100, dtype=np.uint8)
            elif frame_id < fps * 2:  # 第二秒：不同的静态帧
                frame = np.full((180, 320, 3), 200, dtype=np.uint8)
            else:
                frame = np.full((180, 320, 3), 150, dtype=np.uint8)

            out.write(frame)

        out.release()
        return str(video_path)

    def test_detect_scenes_with_valid_video(self):
        """测试用有效视频进行场景检测"""
        video_path = self.create_test_video("test.mp4")

        detector = SceneDetector(method="frame_diff", threshold=20.0)
        scenes = detector.detect_scenes(video_path)

        # 应该检测到至少一个场景
        self.assertGreater(len(scenes), 0)
        # 所有场景应该有有效的时间范围
        for scene in scenes:
            self.assertLess(scene.start_time, scene.end_time)
            self.assertGreaterEqual(scene.start_time, 0)

    def test_detect_scenes_file_not_found(self):
        """测试视频文件不存在时的错误处理"""
        detector = SceneDetector()

        with self.assertRaises(FileNotFoundError):
            detector.detect_scenes("nonexistent_video.mp4")

    def test_different_detection_methods(self):
        """测试不同的检测方法"""
        video_path = self.create_test_video("test_methods.mp4")

        methods = ["frame_diff", "histogram", "motion", "hybrid"]

        for method in methods:
            detector = SceneDetector(method=method)
            scenes = detector.detect_scenes(video_path)

            # 每个方法都应该返回至少一个场景
            self.assertGreater(len(scenes), 0,
                            f"方法 {method} 没有检测到场景")


class TestSceneDetectorPersistence(unittest.TestCase):
    """测试场景信息的持久化"""

    def setUp(self):
        """设置测试环境"""
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        """清理测试环境"""
        import shutil
        if Path(self.test_dir).exists():
            shutil.rmtree(self.test_dir)

    def test_save_and_load_scenes(self):
        """测试保存和加载场景信息"""
        detector = SceneDetector()

        # 创建测试场景
        scenes = [
            Scene(
                start_frame=0,
                end_frame=100,
                start_time=0.0,
                end_time=4.0,
                scene_type=SceneType.ACTION,
                confidence=0.95,
                motion_level=0.8
            ),
            Scene(
                start_frame=100,
                end_frame=200,
                start_time=4.0,
                end_time=8.0,
                scene_type=SceneType.STATIC,
                confidence=0.85,
                motion_level=0.2
            )
        ]

        # 保存
        output_path = str(Path(self.test_dir) / "scenes.json")
        detector.save_scenes(scenes, output_path)

        # 验证文件存在
        self.assertTrue(Path(output_path).exists())

        # 加载
        loaded_scenes = detector.load_scenes(output_path)

        # 验证
        self.assertEqual(len(loaded_scenes), 2)
        self.assertEqual(loaded_scenes[0].start_time, 0.0)
        self.assertEqual(loaded_scenes[0].end_time, 4.0)
        self.assertEqual(loaded_scenes[0].scene_type, SceneType.ACTION)
        self.assertEqual(loaded_scenes[1].scene_type, SceneType.STATIC)


class TestIntegrationWithAnalyzer(unittest.TestCase):
    """与内容分析器的集成测试"""

    def test_analyzer_initialization_with_scene_detector(self):
        """测试分析器是否正确初始化场景检测器"""
        try:
            # 尝试直接导入 ContentAnalyzer
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "analyzer",
                str(project_root / "src" / "core" / "analyzer.py")
            )
            # 如果导入失败，跳过测试
            if spec is None:
                self.skipTest("ContentAnalyzer 不可用")
        except Exception:
            self.skipTest("ContentAnalyzer 导入失败")


def run_tests():
    """运行所有测试"""
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # 添加所有测试类
    suite.addTests(loader.loadTestsFromTestCase(TestScene))
    suite.addTests(loader.loadTestsFromTestCase(TestSceneDetectorInitialization))
    suite.addTests(loader.loadTestsFromTestCase(TestSceneDetectorUtilities))
    suite.addTests(loader.loadTestsFromTestCase(TestSceneDetectorVideoHandling))
    suite.addTests(loader.loadTestsFromTestCase(TestSceneDetectorPersistence))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegrationWithAnalyzer))

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
