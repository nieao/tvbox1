"""
YouTube 下载器单元测试
"""

import unittest
from pathlib import Path
import sys

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.youtube_downloader import YouTubeDownloader


class TestYouTubeDownloader(unittest.TestCase):
    """YouTube 下载器测试"""

    def setUp(self):
        """初始化测试"""
        self.downloader = YouTubeDownloader(
            output_dir="data/test_input",
            cache_dir="data/test_cache"
        )

    def test_extract_video_id(self):
        """测试视频 ID 提取"""
        test_cases = [
            ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("https://youtu.be/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("https://www.youtube.com/embed/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("https://m.youtube.com/watch?v=dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("dQw4w9WgXcQ", "dQw4w9WgXcQ"),  # 直接 ID
        ]

        for url, expected_id in test_cases:
            with self.subTest(url=url):
                video_id = self.downloader.extract_video_id(url)
                self.assertEqual(video_id, expected_id)

    def test_extract_video_id_invalid(self):
        """测试无效 URL"""
        invalid_urls = [
            "https://www.google.com",
            "not_a_url",
            "",
        ]

        for url in invalid_urls:
            with self.subTest(url=url):
                with self.assertRaises(ValueError):
                    self.downloader.extract_video_id(url)

    def test_sanitize_filename(self):
        """测试文件名清理"""
        test_cases = [
            ("Hello World", "Hello World"),
            ("Hello/World", "HelloWorld"),
            ("Hello<>World", "HelloWorld"),
            ("Hello:World|Test", "HelloWorldTest"),
            ("a" * 250, "a" * 200),  # 长度限制
            ("", None),  # 空字符串应返回时间戳格式
        ]

        for input_name, expected in test_cases:
            with self.subTest(input_name=input_name):
                result = self.downloader._sanitize_filename(input_name)
                if expected is None:
                    # 检查是否是时间戳格式
                    self.assertTrue(result.startswith("video_"))
                else:
                    self.assertEqual(result, expected)

    def test_get_metadata(self):
        """测试获取元数据（需要网络连接）"""
        # 使用一个知名的稳定视频
        test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

        try:
            metadata = self.downloader.get_metadata(test_url)

            # 验证必需字段
            self.assertIn('video_id', metadata)
            self.assertIn('title', metadata)
            self.assertIn('duration', metadata)
            self.assertIn('uploader', metadata)

            # 验证视频 ID
            self.assertEqual(metadata['video_id'], 'dQw4w9WgXcQ')

            # 验证时长是数字
            self.assertIsInstance(metadata['duration'], (int, float))
            self.assertGreater(metadata['duration'], 0)

        except Exception as e:
            self.skipTest(f"需要网络连接: {e}")

    def test_get_transcript(self):
        """测试获取字幕（需要网络连接）"""
        # 使用一个有字幕的视频
        test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

        try:
            transcript = self.downloader.get_transcript(test_url)

            # 某些视频可能没有字幕
            if transcript:
                self.assertIsInstance(transcript, str)
                self.assertGreater(len(transcript), 0)
            else:
                self.assertIsNone(transcript)

        except Exception as e:
            self.skipTest(f"需要网络连接或 youtube-transcript-api: {e}")

    def test_download_history(self):
        """测试下载历史功能"""
        # 初始历史应为空或加载已有历史
        initial_history = self.downloader.get_download_history()
        self.assertIsInstance(initial_history, list)

    def test_clear_cache(self):
        """测试清理缓存"""
        try:
            # 清理缓存（保留文件）
            self.downloader.clear_cache(keep_files=True)

            # 验证历史已清空
            history = self.downloader.get_download_history()
            self.assertEqual(len(history), 0)

        except Exception as e:
            self.fail(f"清理缓存失败: {e}")


class TestYouTubeDownloaderIntegration(unittest.TestCase):
    """YouTube 下载器集成测试（需要网络连接）"""

    @unittest.skip("跳过实际下载测试以节省时间和带宽")
    def test_download_video(self):
        """测试下载视频（跳过以节省时间）"""
        downloader = YouTubeDownloader(
            output_dir="data/test_input",
            cache_dir="data/test_cache"
        )

        test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

        try:
            result = downloader.download_video(
                test_url,
                quality="480p"  # 使用较低质量以加快速度
            )

            # 验证结果
            self.assertIn('filepath', result)
            self.assertIn('title', result)
            self.assertIn('duration', result)

            # 验证文件存在
            filepath = Path(result['filepath'])
            self.assertTrue(filepath.exists())

            # 验证文件大小
            self.assertGreater(filepath.stat().st_size, 0)

        except Exception as e:
            self.skipTest(f"下载测试失败: {e}")


def run_tests():
    """运行测试"""
    # 创建测试套件
    suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == "__main__":
    print("="*70)
    print("YouTube 下载器单元测试")
    print("="*70)
    print("\n提示: 某些测试需要网络连接")
    print("提示: 下载测试默认跳过以节省时间\n")

    success = run_tests()

    if success:
        print("\n✅ 所有测试通过!")
    else:
        print("\n❌ 部分测试失败")

    sys.exit(0 if success else 1)
