#!/usr/bin/env python3
"""
YouTube 视频下载命令行工具

快速下载和处理 YouTube 视频。
"""

import argparse
import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.youtube_downloader import YouTubeDownloader, progress_callback_example
from src.core.editor import VideoEditor


def cmd_download(args):
    """下载视频命令"""
    print(f"下载视频: {args.url}")

    downloader = YouTubeDownloader(
        output_dir=args.output_dir,
        cache_dir=args.cache_dir
    )

    try:
        result = downloader.download_video(
            url=args.url,
            quality=args.quality,
            progress_callback=progress_callback_example if not args.quiet else None,
            force_download=args.force
        )

        print(f"\n✅ 下载成功!")
        print(f"文件: {result['filepath']}")
        print(f"标题: {result['title']}")
        print(f"时长: {result['duration']} 秒")
        print(f"大小: {result['filesize'] / 1024 / 1024:.2f} MB")

    except Exception as e:
        print(f"\n❌ 下载失败: {e}")
        sys.exit(1)


def cmd_metadata(args):
    """获取元数据命令"""
    print(f"获取元数据: {args.url}")

    downloader = YouTubeDownloader()

    try:
        metadata = downloader.get_metadata(args.url)

        print("\n视频信息:")
        print(f"  标题: {metadata['title']}")
        print(f"  时长: {metadata['duration']} 秒 ({metadata['duration'] / 60:.1f} 分钟)")
        print(f"  上传者: {metadata['uploader']}")
        print(f"  观看次数: {metadata['view_count']:,}")
        print(f"  上传日期: {metadata['upload_date']}")

        if metadata['description']:
            print(f"\n  描述: {metadata['description'][:200]}...")

        if metadata['tags']:
            print(f"\n  标签: {', '.join(metadata['tags'][:5])}")

    except Exception as e:
        print(f"\n❌ 获取失败: {e}")
        sys.exit(1)


def cmd_transcript(args):
    """获取字幕命令"""
    print(f"获取字幕: {args.url}")

    downloader = YouTubeDownloader()

    try:
        transcript = downloader.get_transcript(
            args.url,
            languages=args.languages.split(',') if args.languages else None
        )

        if transcript:
            print(f"\n✅ 成功获取字幕 ({len(transcript)} 字符)")

            if args.output:
                # 保存到文件
                output_path = Path(args.output)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                output_path.write_text(transcript, encoding='utf-8')
                print(f"已保存到: {output_path}")
            else:
                # 打印预览
                print("\n字幕预览:")
                print(transcript[:500])
                if len(transcript) > 500:
                    print("...")
        else:
            print("\n⚠️  未找到字幕")

    except Exception as e:
        print(f"\n❌ 获取失败: {e}")
        sys.exit(1)


def cmd_process(args):
    """完整处理命令（下载 + 剪辑）"""
    print(f"处理 YouTube 视频: {args.url}")

    # 创建编辑器
    editor = VideoEditor(
        user_interests=args.interests.split(',') if args.interests else [],
        output_length=args.length,
        transition_style=args.transition
    )

    try:
        result = editor.process_youtube_video(
            youtube_url=args.url,
            output_path=args.output,
            quality=args.quality,
            use_transcript=not args.no_transcript
        )

        print(f"\n✅ 处理完成!")
        print(f"输出: {result.output_path}")
        print(f"原始时长: {result.original_duration:.1f} 秒")
        print(f"剪辑后时长: {result.edited_duration:.1f} 秒")
        print(f"压缩率: {result.compression_ratio:.1%}")

    except Exception as e:
        print(f"\n❌ 处理失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def cmd_batch(args):
    """批量下载命令"""
    # 读取 URL 列表
    if args.file:
        with open(args.file, 'r') as f:
            urls = [line.strip() for line in f if line.strip()]
    else:
        urls = args.urls

    print(f"批量下载 {len(urls)} 个视频")

    downloader = YouTubeDownloader(
        output_dir=args.output_dir,
        cache_dir=args.cache_dir
    )

    try:
        results = downloader.batch_download(
            urls,
            quality=args.quality,
            progress_callback=progress_callback_example if not args.quiet else None
        )

        print(f"\n✅ 批量下载完成!")
        print(f"成功: {len(results)} 个")

    except Exception as e:
        print(f"\n❌ 批量下载失败: {e}")
        sys.exit(1)


def cmd_history(args):
    """查看历史命令"""
    downloader = YouTubeDownloader(cache_dir=args.cache_dir)
    history = downloader.get_download_history()

    if not history:
        print("📭 暂无下载历史")
        return

    print(f"\n下载历史 ({len(history)} 条记录):\n")

    for i, record in enumerate(history, 1):
        print(f"{i}. {record['title']}")
        print(f"   视频 ID: {record['video_id']}")
        print(f"   文件: {record['filepath']}")
        print(f"   下载时间: {record['download_date']}")
        print(f"   大小: {record['filesize'] / 1024 / 1024:.2f} MB")
        print()


def cmd_clear(args):
    """清理缓存命令"""
    downloader = YouTubeDownloader(cache_dir=args.cache_dir)

    if args.force:
        confirm = 'y'
    else:
        confirm = input("确认清理缓存？(y/n): ").strip().lower()

    if confirm == 'y':
        downloader.clear_cache(keep_files=not args.delete_files)
        print("✅ 缓存已清理")
    else:
        print("❌ 已取消")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="YouTube 视频下载和处理工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 下载视频
  %(prog)s download https://www.youtube.com/watch?v=VIDEO_ID

  # 获取元数据
  %(prog)s metadata https://www.youtube.com/watch?v=VIDEO_ID

  # 获取字幕
  %(prog)s transcript https://www.youtube.com/watch?v=VIDEO_ID

  # 完整处理（下载 + 剪辑）
  %(prog)s process https://www.youtube.com/watch?v=VIDEO_ID -o output.mp4 -i "编程,AI"

  # 批量下载
  %(prog)s batch URL1 URL2 URL3

  # 查看历史
  %(prog)s history

  # 清理缓存
  %(prog)s clear
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='可用命令')

    # download 命令
    parser_download = subparsers.add_parser('download', help='下载视频')
    parser_download.add_argument('url', help='YouTube 视频 URL')
    parser_download.add_argument('-q', '--quality', default='720p',
                                 choices=['480p', '720p', '1080p', 'best'],
                                 help='视频质量 (默认: 720p)')
    parser_download.add_argument('-o', '--output-dir', default='data/input',
                                 help='输出目录 (默认: data/input)')
    parser_download.add_argument('-c', '--cache-dir', default='data/cache',
                                 help='缓存目录 (默认: data/cache)')
    parser_download.add_argument('-f', '--force', action='store_true',
                                 help='强制下载（忽略缓存）')
    parser_download.add_argument('--quiet', action='store_true',
                                 help='安静模式（不显示进度）')
    parser_download.set_defaults(func=cmd_download)

    # metadata 命令
    parser_metadata = subparsers.add_parser('metadata', help='获取视频元数据')
    parser_metadata.add_argument('url', help='YouTube 视频 URL')
    parser_metadata.set_defaults(func=cmd_metadata)

    # transcript 命令
    parser_transcript = subparsers.add_parser('transcript', help='获取视频字幕')
    parser_transcript.add_argument('url', help='YouTube 视频 URL')
    parser_transcript.add_argument('-l', '--languages', default='zh,zh-CN,en',
                                   help='语言列表（逗号分隔，默认: zh,zh-CN,en）')
    parser_transcript.add_argument('-o', '--output', help='保存到文件')
    parser_transcript.set_defaults(func=cmd_transcript)

    # process 命令
    parser_process = subparsers.add_parser('process', help='完整处理（下载 + 剪辑）')
    parser_process.add_argument('url', help='YouTube 视频 URL')
    parser_process.add_argument('-o', '--output', required=True,
                                help='输出文件路径')
    parser_process.add_argument('-q', '--quality', default='720p',
                                choices=['480p', '720p', '1080p', 'best'],
                                help='视频质量 (默认: 720p)')
    parser_process.add_argument('-i', '--interests',
                                help='用户兴趣（逗号分隔）')
    parser_process.add_argument('-l', '--length', default='medium',
                                choices=['short', 'medium', 'long'],
                                help='输出长度 (默认: medium)')
    parser_process.add_argument('-t', '--transition', default='text',
                                choices=['none', 'text', 'fade', 'blur'],
                                help='过渡风格 (默认: text)')
    parser_process.add_argument('--no-transcript', action='store_true',
                                help='不使用 YouTube 字幕')
    parser_process.set_defaults(func=cmd_process)

    # batch 命令
    parser_batch = subparsers.add_parser('batch', help='批量下载')
    parser_batch.add_argument('urls', nargs='*', help='YouTube 视频 URL 列表')
    parser_batch.add_argument('-f', '--file', help='从文件读取 URL 列表')
    parser_batch.add_argument('-q', '--quality', default='720p',
                              choices=['480p', '720p', '1080p', 'best'],
                              help='视频质量 (默认: 720p)')
    parser_batch.add_argument('-o', '--output-dir', default='data/input',
                              help='输出目录 (默认: data/input)')
    parser_batch.add_argument('-c', '--cache-dir', default='data/cache',
                              help='缓存目录 (默认: data/cache)')
    parser_batch.add_argument('--quiet', action='store_true',
                              help='安静模式（不显示进度）')
    parser_batch.set_defaults(func=cmd_batch)

    # history 命令
    parser_history = subparsers.add_parser('history', help='查看下载历史')
    parser_history.add_argument('-c', '--cache-dir', default='data/cache',
                                help='缓存目录 (默认: data/cache)')
    parser_history.set_defaults(func=cmd_history)

    # clear 命令
    parser_clear = subparsers.add_parser('clear', help='清理缓存')
    parser_clear.add_argument('-c', '--cache-dir', default='data/cache',
                              help='缓存目录 (默认: data/cache)')
    parser_clear.add_argument('--delete-files', action='store_true',
                              help='同时删除已下载的文件')
    parser_clear.add_argument('-f', '--force', action='store_true',
                              help='强制清理（不询问）')
    parser_clear.set_defaults(func=cmd_clear)

    # 解析参数
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    # 执行命令
    args.func(args)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  已中断")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        sys.exit(1)
