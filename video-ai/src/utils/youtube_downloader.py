"""
YouTube 视频下载器

支持从 YouTube 下载视频、获取元数据和字幕。
"""

import os
import re
import logging
from typing import Optional, Callable, Dict, List
from pathlib import Path
from datetime import datetime
import json

try:
    import yt_dlp
    YT_DLP_AVAILABLE = True
except ImportError:
    YT_DLP_AVAILABLE = False

try:
    from youtube_transcript_api import YouTubeTranscriptApi
    from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
    TRANSCRIPT_API_AVAILABLE = True
except ImportError:
    TRANSCRIPT_API_AVAILABLE = False


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class YouTubeDownloader:
    """YouTube 视频下载器"""

    # 质量映射
    QUALITY_MAP = {
        '480p': 'bestvideo[height<=480]+bestaudio/best[height<=480]',
        '720p': 'bestvideo[height<=720]+bestaudio/best[height<=720]',
        '1080p': 'bestvideo[height<=1080]+bestaudio/best[height<=1080]',
        'best': 'bestvideo+bestaudio/best'
    }

    def __init__(self, output_dir: str = "data/input", cache_dir: str = "data/cache"):
        """
        初始化下载器

        Args:
            output_dir: 视频输出目录
            cache_dir: 缓存目录（用于存储下载历史）
        """
        if not YT_DLP_AVAILABLE:
            raise ImportError(
                "请安装 yt-dlp: pip install yt-dlp"
            )

        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.history_file = self.cache_dir / "youtube_history.json"
        self._load_history()

        logger.info(f"YouTube 下载器初始化完成，输出目录: {self.output_dir}")

    def _load_history(self):
        """加载下载历史"""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self.history = json.load(f)
            except Exception as e:
                logger.warning(f"加载历史记录失败: {e}")
                self.history = {}
        else:
            self.history = {}

    def _save_history(self):
        """保存下载历史"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.warning(f"保存历史记录失败: {e}")

    def extract_video_id(self, url: str) -> str:
        """
        从 URL 提取视频 ID

        Args:
            url: YouTube 视频 URL

        Returns:
            视频 ID

        Raises:
            ValueError: 如果无法提取视频 ID
        """
        # 支持的 URL 格式:
        # - https://www.youtube.com/watch?v=VIDEO_ID
        # - https://youtu.be/VIDEO_ID
        # - https://www.youtube.com/embed/VIDEO_ID
        # - https://m.youtube.com/watch?v=VIDEO_ID

        patterns = [
            r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
            r'(?:embed\/)([0-9A-Za-z_-]{11})',
            r'^([0-9A-Za-z_-]{11})$'  # 直接输入 ID
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                video_id = match.group(1)
                logger.debug(f"提取到视频 ID: {video_id}")
                return video_id

        raise ValueError(f"无法从 URL 提取视频 ID: {url}")

    def get_metadata(self, url: str, retry_count: int = 3) -> Dict:
        """
        获取视频元数据

        Args:
            url: YouTube 视频 URL
            retry_count: 重试次数

        Returns:
            包含元数据的字典

        Raises:
            Exception: 如果获取失败
        """
        logger.info(f"获取视频元数据: {url}")

        video_id = self.extract_video_id(url)

        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
        }

        for attempt in range(retry_count):
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)

                    metadata = {
                        'video_id': video_id,
                        'title': info.get('title', '未知标题'),
                        'description': info.get('description', ''),
                        'duration': info.get('duration', 0),  # 秒
                        'uploader': info.get('uploader', ''),
                        'upload_date': info.get('upload_date', ''),
                        'view_count': info.get('view_count', 0),
                        'like_count': info.get('like_count', 0),
                        'thumbnail': info.get('thumbnail', ''),
                        'tags': info.get('tags', []),
                        'categories': info.get('categories', []),
                        'url': url,
                        'webpage_url': info.get('webpage_url', url),
                    }

                    logger.info(f"元数据获取成功: {metadata['title']} ({metadata['duration']}秒)")
                    return metadata

            except Exception as e:
                logger.warning(f"获取元数据失败 (尝试 {attempt + 1}/{retry_count}): {e}")
                if attempt == retry_count - 1:
                    raise Exception(f"获取元数据失败: {e}")

    def get_transcript(
        self,
        url: str,
        languages: List[str] = ['zh', 'zh-CN', 'zh-TW', 'en']
    ) -> Optional[str]:
        """
        获取视频字幕/转录

        Args:
            url: YouTube 视频 URL
            languages: 语言优先级列表

        Returns:
            字幕文本，如果没有则返回 None
        """
        if not TRANSCRIPT_API_AVAILABLE:
            logger.warning("youtube-transcript-api 未安装，无法获取字幕")
            return None

        try:
            video_id = self.extract_video_id(url)
            logger.info(f"尝试获取字幕，视频 ID: {video_id}")

            # 获取字幕列表
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

            # 按优先级尝试获取字幕
            transcript = None
            for lang in languages:
                try:
                    transcript = transcript_list.find_transcript([lang])
                    logger.info(f"找到字幕: {lang}")
                    break
                except NoTranscriptFound:
                    continue

            # 如果没有找到，尝试获取自动生成的字幕
            if not transcript:
                try:
                    transcript = transcript_list.find_generated_transcript(languages)
                    logger.info(f"使用自动生成的字幕")
                except NoTranscriptFound:
                    logger.warning("未找到任何字幕")
                    return None

            # 获取字幕内容
            if transcript:
                transcript_data = transcript.fetch()

                # 合并所有文本
                full_text = ' '.join([item['text'] for item in transcript_data])

                logger.info(f"字幕获取成功，共 {len(full_text)} 字符")
                return full_text

        except TranscriptsDisabled:
            logger.warning("该视频已禁用字幕")
        except Exception as e:
            logger.error(f"获取字幕失败: {e}")

        return None

    def download_video(
        self,
        url: str,
        quality: str = "720p",
        progress_callback: Optional[Callable] = None,
        filename: Optional[str] = None,
        force_download: bool = False
    ) -> Dict:
        """
        下载 YouTube 视频

        Args:
            url: YouTube 视频 URL
            quality: 视频质量 (480p, 720p, 1080p, best)
            progress_callback: 进度回调函数 callback(d)
            filename: 自定义文件名（不包含扩展名）
            force_download: 强制下载（忽略缓存）

        Returns:
            包含文件路径和元数据的字典

        Raises:
            Exception: 如果下载失败
        """
        logger.info(f"开始下载视频: {url}, 质量: {quality}")

        # 提取视频 ID
        video_id = self.extract_video_id(url)

        # 检查缓存
        if not force_download and video_id in self.history:
            cached = self.history[video_id]
            cached_path = Path(cached['filepath'])

            if cached_path.exists():
                logger.info(f"使用缓存的视频: {cached_path}")
                return cached

        # 获取元数据
        metadata = self.get_metadata(url)

        # 确定文件名
        if filename:
            safe_filename = self._sanitize_filename(filename)
        else:
            safe_filename = self._sanitize_filename(metadata['title'])

        # 构建输出路径
        output_template = str(self.output_dir / f"{safe_filename}.%(ext)s")

        # 配置下载选项
        format_string = self.QUALITY_MAP.get(quality, self.QUALITY_MAP['720p'])

        ydl_opts = {
            'format': format_string,
            'outtmpl': output_template,
            'merge_output_format': 'mp4',  # 统一输出为 mp4
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',
            }],
            'quiet': False,
            'no_warnings': False,
        }

        # 添加进度回调
        if progress_callback:
            def progress_hook(d):
                if d['status'] == 'downloading':
                    progress_callback(d)
                elif d['status'] == 'finished':
                    logger.info('下载完成，正在转换...')

            ydl_opts['progress_hooks'] = [progress_hook]

        # 下载视频
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                logger.info("开始下载...")
                ydl.download([url])

            # 查找下载的文件
            output_path = self.output_dir / f"{safe_filename}.mp4"

            if not output_path.exists():
                # 尝试查找其他扩展名
                possible_files = list(self.output_dir.glob(f"{safe_filename}.*"))
                if possible_files:
                    output_path = possible_files[0]
                else:
                    raise FileNotFoundError(f"下载完成但找不到文件: {output_path}")

            logger.info(f"视频下载成功: {output_path}")

            # 构建结果
            result = {
                'video_id': video_id,
                'filepath': str(output_path),
                'filename': output_path.name,
                'title': metadata['title'],
                'duration': metadata['duration'],
                'quality': quality,
                'filesize': output_path.stat().st_size,
                'download_date': datetime.now().isoformat(),
                'metadata': metadata
            }

            # 保存到历史
            self.history[video_id] = result
            self._save_history()

            return result

        except Exception as e:
            logger.error(f"下载失败: {e}")
            raise Exception(f"下载视频失败: {e}")

    def _sanitize_filename(self, filename: str) -> str:
        """
        清理文件名，移除非法字符

        Args:
            filename: 原始文件名

        Returns:
            清理后的文件名
        """
        # 移除非法字符
        filename = re.sub(r'[<>:"/\\|?*]', '', filename)

        # 限制长度
        if len(filename) > 200:
            filename = filename[:200]

        # 移除前后空格
        filename = filename.strip()

        # 如果为空，使用默认名称
        if not filename:
            filename = f"video_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        return filename

    def batch_download(
        self,
        urls: List[str],
        quality: str = "720p",
        progress_callback: Optional[Callable] = None
    ) -> List[Dict]:
        """
        批量下载视频

        Args:
            urls: YouTube 视频 URL 列表
            quality: 视频质量
            progress_callback: 进度回调函数

        Returns:
            下载结果列表
        """
        logger.info(f"开始批量下载 {len(urls)} 个视频")

        results = []
        failed = []

        for i, url in enumerate(urls, 1):
            logger.info(f"\n下载进度: {i}/{len(urls)}")

            try:
                result = self.download_video(
                    url,
                    quality=quality,
                    progress_callback=progress_callback
                )
                results.append(result)

            except Exception as e:
                logger.error(f"下载失败 ({url}): {e}")
                failed.append({'url': url, 'error': str(e)})

        logger.info(f"\n批量下载完成！成功: {len(results)}, 失败: {len(failed)}")

        if failed:
            logger.warning("失败列表:")
            for item in failed:
                logger.warning(f"  - {item['url']}: {item['error']}")

        return results

    def download_playlist(
        self,
        playlist_url: str,
        quality: str = "720p",
        max_videos: Optional[int] = None,
        progress_callback: Optional[Callable] = None
    ) -> List[Dict]:
        """
        下载播放列表

        Args:
            playlist_url: 播放列表 URL
            quality: 视频质量
            max_videos: 最大下载数量
            progress_callback: 进度回调函数

        Returns:
            下载结果列表
        """
        logger.info(f"开始下载播放列表: {playlist_url}")

        try:
            # 获取播放列表信息
            ydl_opts = {
                'quiet': True,
                'extract_flat': True,
                'force_generic_extractor': False,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                playlist_info = ydl.extract_info(playlist_url, download=False)

                if 'entries' not in playlist_info:
                    raise ValueError("无效的播放列表 URL")

                entries = playlist_info['entries']

                # 限制数量
                if max_videos:
                    entries = entries[:max_videos]

                logger.info(f"播放列表包含 {len(entries)} 个视频")

                # 提取视频 URL
                video_urls = [
                    f"https://www.youtube.com/watch?v={entry['id']}"
                    for entry in entries
                    if entry.get('id')
                ]

                # 批量下载
                return self.batch_download(
                    video_urls,
                    quality=quality,
                    progress_callback=progress_callback
                )

        except Exception as e:
            logger.error(f"下载播放列表失败: {e}")
            raise Exception(f"下载播放列表失败: {e}")

    def get_download_history(self) -> List[Dict]:
        """
        获取下载历史

        Returns:
            历史记录列表
        """
        return list(self.history.values())

    def clear_cache(self, keep_files: bool = True):
        """
        清理缓存

        Args:
            keep_files: 是否保留已下载的文件
        """
        logger.info(f"清理缓存（保留文件: {keep_files}）")

        if not keep_files:
            # 删除所有下载的文件
            for video_id, info in self.history.items():
                filepath = Path(info['filepath'])
                if filepath.exists():
                    try:
                        filepath.unlink()
                        logger.info(f"删除文件: {filepath}")
                    except Exception as e:
                        logger.warning(f"删除文件失败 ({filepath}): {e}")

        # 清空历史记录
        self.history = {}
        self._save_history()

        logger.info("缓存清理完成")


def progress_callback_example(d):
    """进度回调示例"""
    if d['status'] == 'downloading':
        percent = d.get('_percent_str', 'N/A')
        speed = d.get('_speed_str', 'N/A')
        eta = d.get('_eta_str', 'N/A')
        print(f"\r下载进度: {percent} | 速度: {speed} | 剩余时间: {eta}", end='')


if __name__ == "__main__":
    # 使用示例
    print("=" * 60)
    print("YouTube 视频下载器 - 使用示例")
    print("=" * 60)

    # 创建下载器
    downloader = YouTubeDownloader()

    # 测试 URL
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

    print(f"\n1. 获取视频元数据")
    try:
        metadata = downloader.get_metadata(test_url)
        print(f"标题: {metadata['title']}")
        print(f"时长: {metadata['duration']} 秒")
        print(f"上传者: {metadata['uploader']}")
    except Exception as e:
        print(f"错误: {e}")

    print(f"\n2. 获取视频字幕")
    try:
        transcript = downloader.get_transcript(test_url)
        if transcript:
            print(f"字幕长度: {len(transcript)} 字符")
            print(f"前 100 字符: {transcript[:100]}...")
        else:
            print("未找到字幕")
    except Exception as e:
        print(f"错误: {e}")

    print(f"\n3. 下载视频 (请取消注释以下代码来测试)")
    print("""
    # result = downloader.download_video(
    #     test_url,
    #     quality="480p",
    #     progress_callback=progress_callback_example
    # )
    # print(f"\\n下载完成: {result['filepath']}")
    # print(f"文件大小: {result['filesize'] / 1024 / 1024:.2f} MB")
    """)

    print("\n" + "=" * 60)
    print("示例完成！")
    print("=" * 60)
