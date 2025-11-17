"""
YouTube 视频处理演示

演示如何使用 Video-AI 处理 YouTube 视频。
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.youtube_downloader import YouTubeDownloader, progress_callback_example
from src.core.editor import VideoEditor


def demo_1_download_only():
    """演示1: 仅下载 YouTube 视频"""
    print("\n" + "="*70)
    print("演示 1: 下载 YouTube 视频")
    print("="*70)

    # 创建下载器
    downloader = YouTubeDownloader(
        output_dir="data/input",
        cache_dir="data/cache"
    )

    # 测试 URL（请替换为实际的 YouTube URL）
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

    # 1. 获取元数据
    print("\n1️⃣  获取视频元数据...")
    try:
        metadata = downloader.get_metadata(test_url)
        print(f"\n视频信息:")
        print(f"  标题: {metadata['title']}")
        print(f"  时长: {metadata['duration']} 秒 ({metadata['duration'] / 60:.1f} 分钟)")
        print(f"  上传者: {metadata['uploader']}")
        print(f"  观看次数: {metadata['view_count']:,}")
        print(f"  上传日期: {metadata['upload_date']}")
    except Exception as e:
        print(f"❌ 错误: {e}")
        return

    # 2. 获取字幕
    print("\n2️⃣  获取视频字幕...")
    try:
        transcript = downloader.get_transcript(test_url)
        if transcript:
            print(f"\n✅ 成功获取字幕!")
            print(f"  字幕长度: {len(transcript)} 字符")
            print(f"  前 200 字符预览:")
            print(f"  {transcript[:200]}...")
        else:
            print("⚠️  未找到字幕")
    except Exception as e:
        print(f"⚠️  获取字幕失败: {e}")

    # 3. 下载视频（可选）
    print("\n3️⃣  下载视频...")
    print("⚠️  提示: 下载可能需要一些时间，取决于视频大小和网络速度")

    choice = input("\n是否继续下载？(y/n): ").strip().lower()

    if choice == 'y':
        try:
            result = downloader.download_video(
                test_url,
                quality="480p",  # 使用 480p 以加快下载速度
                progress_callback=progress_callback_example
            )

            print(f"\n\n✅ 下载成功!")
            print(f"  文件路径: {result['filepath']}")
            print(f"  文件大小: {result['filesize'] / 1024 / 1024:.2f} MB")
            print(f"  视频标题: {result['title']}")
            print(f"  视频时长: {result['duration']} 秒")

            return result['filepath']

        except Exception as e:
            print(f"\n❌ 下载失败: {e}")
            return None
    else:
        print("⏭️  跳过下载")
        return None


def demo_2_process_youtube_video():
    """演示2: 完整处理 YouTube 视频（下载 + 智能剪辑）"""
    print("\n" + "="*70)
    print("演示 2: 完整处理 YouTube 视频")
    print("="*70)

    # 配置
    youtube_url = input("\n请输入 YouTube 视频 URL: ").strip()

    if not youtube_url:
        print("❌ URL 不能为空")
        return

    # 用户兴趣
    print("\n请输入你的兴趣关键词（用逗号分隔）:")
    print("例如: 编程,AI,技术")
    interests_input = input("> ").strip()

    if interests_input:
        user_interests = [i.strip() for i in interests_input.split(',')]
    else:
        user_interests = []

    # 创建视频编辑器
    print("\n初始化视频编辑器...")
    editor = VideoEditor(
        user_interests=user_interests,
        output_length="medium",  # short, medium, long
        transition_style="text",
        transition_template="modern"
    )

    # 处理 YouTube 视频
    output_path = "data/output/youtube_edited.mp4"

    try:
        print("\n开始处理...")
        result = editor.process_youtube_video(
            youtube_url=youtube_url,
            output_path=output_path,
            quality="480p",  # 480p 更快
            use_transcript=True  # 尝试使用 YouTube 字幕
        )

        print("\n" + "="*70)
        print("✅ 处理完成!")
        print("="*70)
        print(f"\n输出文件: {result.output_path}")
        print(f"原始时长: {result.original_duration:.1f} 秒")
        print(f"剪辑后时长: {result.edited_duration:.1f} 秒")
        print(f"压缩率: {result.compression_ratio:.1%}")
        print(f"信息密度提升: {result.density_improvement:.1%}")
        print(f"片段数量: {result.segments_count}")

        if hasattr(result, 'youtube_metadata'):
            print(f"\nYouTube 元数据:")
            print(f"  原视频标题: {result.youtube_metadata['title']}")
            print(f"  视频 ID: {result.youtube_metadata['video_id']}")
            print(f"  包含字幕: {'是' if result.youtube_metadata['has_transcript'] else '否'}")

    except Exception as e:
        print(f"\n❌ 处理失败: {e}")
        import traceback
        traceback.print_exc()


def demo_3_batch_download():
    """演示3: 批量下载多个视频"""
    print("\n" + "="*70)
    print("演示 3: 批量下载 YouTube 视频")
    print("="*70)

    # 视频列表
    video_urls = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "https://www.youtube.com/watch?v=9bZkp7q19f0",
        # 添加更多 URL...
    ]

    print(f"\n将下载 {len(video_urls)} 个视频")

    # 创建下载器
    downloader = YouTubeDownloader()

    try:
        results = downloader.batch_download(
            video_urls,
            quality="480p",
            progress_callback=progress_callback_example
        )

        print(f"\n✅ 批量下载完成!")
        print(f"  成功: {len(results)} 个")

        for i, result in enumerate(results, 1):
            print(f"\n{i}. {result['title']}")
            print(f"   文件: {result['filepath']}")
            print(f"   大小: {result['filesize'] / 1024 / 1024:.2f} MB")

    except Exception as e:
        print(f"\n❌ 批量下载失败: {e}")


def demo_4_download_history():
    """演示4: 查看下载历史"""
    print("\n" + "="*70)
    print("演示 4: 查看下载历史")
    print("="*70)

    downloader = YouTubeDownloader()
    history = downloader.get_download_history()

    if not history:
        print("\n📭 暂无下载历史")
        return

    print(f"\n共有 {len(history)} 条下载记录:\n")

    for i, record in enumerate(history, 1):
        print(f"{i}. {record['title']}")
        print(f"   视频 ID: {record['video_id']}")
        print(f"   文件路径: {record['filepath']}")
        print(f"   下载时间: {record['download_date']}")
        print(f"   文件大小: {record['filesize'] / 1024 / 1024:.2f} MB")
        print()


def main():
    """主菜单"""
    print("\n" + "="*70)
    print("Video-AI YouTube 集成功能演示")
    print("="*70)

    while True:
        print("\n请选择演示:")
        print("1. 下载 YouTube 视频（仅下载，不处理）")
        print("2. 完整处理 YouTube 视频（下载 + 智能剪辑）")
        print("3. 批量下载多个视频")
        print("4. 查看下载历史")
        print("0. 退出")

        choice = input("\n请输入选项 (0-4): ").strip()

        if choice == '1':
            demo_1_download_only()
        elif choice == '2':
            demo_2_process_youtube_video()
        elif choice == '3':
            demo_3_batch_download()
        elif choice == '4':
            demo_4_download_history()
        elif choice == '0':
            print("\n👋 再见!")
            break
        else:
            print("\n❌ 无效选项，请重试")


if __name__ == "__main__":
    # 检查依赖
    try:
        import yt_dlp
        print("✅ yt-dlp 已安装")
    except ImportError:
        print("❌ 缺少依赖: yt-dlp")
        print("请运行: pip install yt-dlp")
        sys.exit(1)

    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        print("✅ youtube-transcript-api 已安装")
    except ImportError:
        print("⚠️  youtube-transcript-api 未安装（字幕功能将不可用）")
        print("建议运行: pip install youtube-transcript-api")

    # 运行主程序
    main()
