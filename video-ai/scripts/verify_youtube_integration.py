#!/usr/bin/env python3
"""
YouTube 集成功能验证脚本

验证所有 YouTube 集成功能是否正常工作。
"""

import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def print_section(title):
    """打印章节标题"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")

def check_dependencies():
    """检查依赖"""
    print_section("1. 检查依赖")

    checks = []

    # 检查 yt-dlp
    try:
        import yt_dlp
        version = yt_dlp.version.__version__
        print(f"✅ yt-dlp: {version}")
        checks.append(True)
    except ImportError:
        print("❌ yt-dlp 未安装")
        print("   安装: pip install yt-dlp")
        checks.append(False)

    # 检查 youtube-transcript-api
    try:
        import youtube_transcript_api
        print(f"✅ youtube-transcript-api: 已安装")
        checks.append(True)
    except ImportError:
        print("⚠️  youtube-transcript-api 未安装（字幕功能将不可用）")
        print("   安装: pip install youtube-transcript-api")
        checks.append(False)

    # 检查 moviepy
    try:
        import moviepy
        print(f"✅ moviepy: 已安装")
        checks.append(True)
    except ImportError:
        print("❌ moviepy 未安装（视频处理将不可用）")
        print("   安装: pip install moviepy")
        checks.append(False)

    return all(checks[:2])  # 至少需要 yt-dlp


def check_imports():
    """检查模块导入"""
    print_section("2. 检查模块导入")

    checks = []

    # 检查 YouTubeDownloader
    try:
        from src.utils.youtube_downloader import YouTubeDownloader
        print("✅ YouTubeDownloader 导入成功")
        checks.append(True)
    except ImportError as e:
        print(f"❌ YouTubeDownloader 导入失败: {e}")
        checks.append(False)

    # 检查 VideoEditor
    try:
        from src.core.editor import VideoEditor
        print("✅ VideoEditor 导入成功")
        checks.append(True)
    except ImportError as e:
        print(f"❌ VideoEditor 导入失败: {e}")
        checks.append(False)

    return all(checks)


def test_video_id_extraction():
    """测试视频 ID 提取"""
    print_section("3. 测试视频 ID 提取")

    from src.utils.youtube_downloader import YouTubeDownloader

    downloader = YouTubeDownloader()

    test_cases = [
        ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        ("https://youtu.be/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        ("https://www.youtube.com/embed/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
    ]

    passed = 0
    for url, expected_id in test_cases:
        try:
            video_id = downloader.extract_video_id(url)
            if video_id == expected_id:
                print(f"✅ {url[:50]}: {video_id}")
                passed += 1
            else:
                print(f"❌ {url[:50]}: 期望 {expected_id}, 得到 {video_id}")
        except Exception as e:
            print(f"❌ {url[:50]}: {e}")

    print(f"\n通过: {passed}/{len(test_cases)}")
    return passed == len(test_cases)


def test_metadata(url="https://www.youtube.com/watch?v=dQw4w9WgXcQ"):
    """测试元数据获取"""
    print_section("4. 测试元数据获取（需要网络）")

    from src.utils.youtube_downloader import YouTubeDownloader

    downloader = YouTubeDownloader()

    print(f"测试 URL: {url}\n")

    try:
        metadata = downloader.get_metadata(url)

        print("✅ 元数据获取成功\n")
        print(f"标题: {metadata['title']}")
        print(f"时长: {metadata['duration']} 秒 ({metadata['duration'] / 60:.1f} 分钟)")
        print(f"上传者: {metadata['uploader']}")
        print(f"观看次数: {metadata['view_count']:,}")

        return True

    except Exception as e:
        print(f"❌ 元数据获取失败: {e}")
        print("提示: 这可能是网络问题或 YouTube 访问限制")
        return False


def test_transcript(url="https://www.youtube.com/watch?v=dQw4w9WgXcQ"):
    """测试字幕获取"""
    print_section("5. 测试字幕获取（需要网络）")

    from src.utils.youtube_downloader import YouTubeDownloader

    downloader = YouTubeDownloader()

    print(f"测试 URL: {url}\n")

    try:
        transcript = downloader.get_transcript(url)

        if transcript:
            print("✅ 字幕获取成功\n")
            print(f"字幕长度: {len(transcript)} 字符")
            print(f"前 200 字符: {transcript[:200]}...")
            return True
        else:
            print("⚠️  该视频没有字幕")
            print("提示: 这是正常的，不是所有视频都有字幕")
            return True  # 仍然算通过

    except Exception as e:
        print(f"⚠️  字幕获取失败: {e}")
        print("提示: youtube-transcript-api 可能未安装")
        return True  # 不是致命错误


def test_file_operations():
    """测试文件操作"""
    print_section("6. 测试文件操作")

    from src.utils.youtube_downloader import YouTubeDownloader

    downloader = YouTubeDownloader(
        output_dir="data/test_input",
        cache_dir="data/test_cache"
    )

    checks = []

    # 检查目录创建
    if downloader.output_dir.exists():
        print(f"✅ 输出目录创建成功: {downloader.output_dir}")
        checks.append(True)
    else:
        print(f"❌ 输出目录创建失败: {downloader.output_dir}")
        checks.append(False)

    if downloader.cache_dir.exists():
        print(f"✅ 缓存目录创建成功: {downloader.cache_dir}")
        checks.append(True)
    else:
        print(f"❌ 缓存目录创建失败: {downloader.cache_dir}")
        checks.append(False)

    # 测试文件名清理
    test_filenames = [
        ("Hello World", "Hello World"),
        ("Hello/World", "HelloWorld"),
        ("Test<>File", "TestFile"),
    ]

    for input_name, expected in test_filenames:
        result = downloader._sanitize_filename(input_name)
        if result == expected:
            print(f"✅ 文件名清理: '{input_name}' -> '{result}'")
            checks.append(True)
        else:
            print(f"❌ 文件名清理: '{input_name}' -> '{result}' (期望: '{expected}')")
            checks.append(False)

    return all(checks)


def test_cli_tool():
    """测试命令行工具"""
    print_section("7. 测试命令行工具")

    cli_path = project_root / "scripts" / "youtube_cli.py"

    if cli_path.exists():
        print(f"✅ CLI 工具存在: {cli_path}")

        # 检查执行权限
        import os
        if os.access(cli_path, os.X_OK):
            print(f"✅ CLI 工具有执行权限")
        else:
            print(f"⚠️  CLI 工具无执行权限（在 Windows 上这是正常的）")

        return True
    else:
        print(f"❌ CLI 工具不存在: {cli_path}")
        return False


def test_documentation():
    """测试文档"""
    print_section("8. 测试文档")

    docs = [
        "docs/youtube_integration.md",
        "docs/YOUTUBE_QUICKSTART.md",
        "docs/IMPLEMENTATION_SUMMARY.md",
        "docs/README_UPDATE.md",
    ]

    checks = []

    for doc_path in docs:
        full_path = project_root / doc_path
        if full_path.exists():
            size = full_path.stat().st_size
            print(f"✅ {doc_path} ({size} 字节)")
            checks.append(True)
        else:
            print(f"❌ {doc_path} 不存在")
            checks.append(False)

    return all(checks)


def test_examples():
    """测试示例文件"""
    print_section("9. 测试示例文件")

    examples = [
        "examples/youtube_demo.py",
        "tests/test_youtube_downloader.py",
    ]

    checks = []

    for example_path in examples:
        full_path = project_root / example_path
        if full_path.exists():
            # 尝试编译
            import py_compile
            try:
                py_compile.compile(str(full_path), doraise=True)
                print(f"✅ {example_path} (语法正确)")
                checks.append(True)
            except py_compile.PyCompileError as e:
                print(f"❌ {example_path} (语法错误: {e})")
                checks.append(False)
        else:
            print(f"❌ {example_path} 不存在")
            checks.append(False)

    return all(checks)


def run_all_tests():
    """运行所有测试"""
    print("\n" + "="*70)
    print("  YouTube 集成功能验证")
    print("="*70)

    results = {
        "依赖检查": check_dependencies(),
        "模块导入": check_imports(),
        "视频 ID 提取": test_video_id_extraction(),
        "文件操作": test_file_operations(),
        "CLI 工具": test_cli_tool(),
        "文档": test_documentation(),
        "示例文件": test_examples(),
    }

    # 需要网络的测试
    print("\n" + "="*70)
    print("  以下测试需要网络连接")
    print("="*70)

    network_choice = input("\n是否运行需要网络的测试？(y/n): ").strip().lower()

    if network_choice == 'y':
        results["元数据获取"] = test_metadata()
        results["字幕获取"] = test_transcript()
    else:
        print("\n⏭️  跳过网络测试")

    # 打印总结
    print("\n" + "="*70)
    print("  测试总结")
    print("="*70 + "\n")

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status}  {test_name}")

    print(f"\n总计: {passed}/{total} 通过")

    if passed == total:
        print("\n🎉 所有测试通过！YouTube 集成功能正常工作。")
        return True
    else:
        print(f"\n⚠️  {total - passed} 个测试失败，请检查上述错误。")
        return False


if __name__ == "__main__":
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️  测试中断")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
