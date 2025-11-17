"""
视频编辑模块

根据分析结果智能剪辑视频，生成个性化短视频。
"""

import os
from typing import List, Optional, Dict
from dataclasses import dataclass
from pathlib import Path

try:
    from moviepy.editor import VideoFileClip, concatenate_videoclips, TextClip, CompositeVideoClip
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False

from .transcriber import VideoTranscriber, Transcript
from .analyzer import ContentAnalyzer, AnalysisResult, KeySegment
from .generator import TransitionGenerator
from .quality_analyzer import QualityAnalyzer, QualityMetrics
from .narrative_sorter import NarrativeSorter
from ..services.personalization import PersonalizationConfig
from ..utils.youtube_downloader import YouTubeDownloader


@dataclass
class EditingResult:
    """剪辑结果"""
    output_path: str
    original_duration: float  # 原始时长（秒）
    edited_duration: float    # 剪辑后时长（秒）
    compression_ratio: float  # 压缩比例
    density_improvement: float  # 信息密度提升百分比
    segments_count: int       # 片段数量


class VideoEditor:
    """视频编辑器 - 主入口类"""

    def __init__(
        self,
        user_interests: Optional[List[str]] = None,
        output_length: str = "medium",
        config: Optional[PersonalizationConfig] = None,
        transition_style: str = "text",
        transition_template: str = "modern"
    ):
        """
        初始化视频编辑器

        Args:
            user_interests: 用户兴趣列表
            output_length: 输出长度 ('short', 'medium', 'long')
            config: 个性化配置对象
            transition_style: 过渡效果风格 ('text', 'fade', 'blur', 'zoom', 'gradient')
            transition_template: 文字过渡模板 ('minimal', 'modern', 'classic', 'colorful', 'info_card')
        """
        if not MOVIEPY_AVAILABLE:
            raise ImportError(
                "请安装 moviepy: pip install moviepy"
            )

        if config:
            self.config = config
        else:
            self.config = PersonalizationConfig(
                interests=user_interests or [],
                output_length=output_length
            )

        # 初始化组件
        self.transcriber = VideoTranscriber(
            model_name="base",
            device="cpu"  # TODO: 从配置读取
        )

        self.analyzer = ContentAnalyzer(
            api_provider="openai"  # TODO: 从配置读取
        )

        # 初始化过渡生成器
        self.transition_generator = TransitionGenerator(
            transition_style=transition_style,
            duration=2.0
        )
        self.transition_template = transition_template

        # 初始化质量分析器
        self.quality_analyzer = QualityAnalyzer()

        # 初始化叙事排序器
        self.narrative_sorter = NarrativeSorter(strategy="hybrid")

    def process_video(
        self,
        input_path: str,
        output_path: str,
        **kwargs
    ) -> EditingResult:
        """
        处理视频（主流程）

        Args:
            input_path: 输入视频路径
            output_path: 输出视频路径
            **kwargs: 其他参数

        Returns:
            EditingResult对象
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"输入视频不存在: {input_path}")

        print(f"\n{'='*60}")
        print(f"开始处理视频: {input_path}")
        print(f"{'='*60}\n")

        # 步骤1: 转录视频
        print("步骤 1/4: 转录视频...")
        transcript = self.transcriber.transcribe(
            input_path,
            language=self.config.language.split('-')[0]  # zh-CN -> zh
        )

        # 步骤2: 分析内容
        print("\n步骤 2/4: 分析内容...")
        analysis = self.analyzer.analyze(
            transcript,
            user_interests=self.config.interests,
            max_segments=kwargs.get('max_segments', 10)
        )

        # 步骤3: 剪辑视频
        print("\n步骤 3/4: 剪辑视频...")
        result = self._edit_video(
            input_path,
            output_path,
            analysis,
            transcript
        )

        print(f"\n{'='*60}")
        print("处理完成！")
        print(f"原始时长: {result.original_duration:.1f}秒")
        print(f"剪辑后时长: {result.edited_duration:.1f}秒")
        print(f"压缩率: {result.compression_ratio:.1%}")
        print(f"信息密度提升: {result.density_improvement:.1%}")
        print(f"{'='*60}\n")

        return result

    def _edit_video(
        self,
        input_path: str,
        output_path: str,
        analysis: AnalysisResult,
        transcript: Transcript
    ) -> EditingResult:
        """执行视频剪辑"""
        # 分析视频质量
        print("  分析视频质量...")
        try:
            quality_metrics = self.quality_analyzer.analyze_video(input_path)
            print(f"  视频综合质量评分: {quality_metrics.overall_score:.1f}/100")
            print(f"  分辨率: {quality_metrics.resolution[0]}x{quality_metrics.resolution[1]} "
                  f"| 帧率: {quality_metrics.fps:.1f}fps "
                  f"| 码率: {quality_metrics.bitrate}kbps")

            # 如果质量太低，提示改进建议
            if quality_metrics.overall_score < 70:
                print("\n  质量改进建议:")
                suggestions = self.quality_analyzer.suggest_enhancements(quality_metrics)
                for suggestion in suggestions[:3]:  # 显示前3条建议
                    print(f"    {suggestion}")
        except Exception as e:
            print(f"  警告: 质量分析失败 ({e})，继续处理...")

        # 加载视频
        video = VideoFileClip(input_path)
        original_duration = video.duration

        # 智能排序片段（叙事排序）
        print("  智能排序片段...")
        original_coherence = self.narrative_sorter.evaluate_coherence(analysis.key_segments)
        print(f"    排序前连贯性: {original_coherence:.3f}")

        analysis.key_segments = self.narrative_sorter.sort_segments(
            analysis.key_segments,
            preserve_order=False
        )

        sorted_coherence = self.narrative_sorter.evaluate_coherence(analysis.key_segments)
        print(f"    排序后连贯性: {sorted_coherence:.3f}")
        improvement = ((sorted_coherence - original_coherence) / max(original_coherence, 0.01)) * 100
        print(f"    连贯性提升: {improvement:+.1f}%")

        # 提取关键片段
        clips = []
        total_edited_duration = 0

        for i, segment in enumerate(analysis.key_segments):
            print(f"  提取片段 {i+1}/{len(analysis.key_segments)}: "
                  f"{segment.start:.1f}s - {segment.end:.1f}s "
                  f"(主题: {segment.topic})")

            # 提取子片段
            subclip = video.subclip(segment.start, segment.end)

            # 如果配置了过渡效果，添加过渡片段
            if self.config.transition_style != "none" and i > 0:
                try:
                    transition_clip = self.transition_generator.create_transition(
                        text=segment.topic,
                        size=video.size if hasattr(video, 'size') else (1920, 1080),
                        template=self.transition_template
                    )
                    clips.append(transition_clip)
                    total_edited_duration += self.transition_generator.duration
                except Exception as e:
                    print(f"  警告: 创建过渡效果失败 ({e})，跳过")
                    continue

            clips.append(subclip)
            total_edited_duration += (segment.end - segment.start)

        # 拼接所有片段
        print("  拼接片段...")
        final_video = concatenate_videoclips(clips, method="compose")

        # 导出视频
        print("  导出视频...")
        final_video.write_videofile(
            output_path,
            codec='libx264',
            audio_codec='aac',
            temp_audiofile='temp-audio.m4a',
            remove_temp=True,
            fps=video.fps
        )

        # 清理资源
        video.close()
        final_video.close()

        # 计算结果
        compression_ratio = 1 - (total_edited_duration / original_duration)
        density_improvement = 1 / (1 - compression_ratio) - 1 if compression_ratio < 1 else 0

        return EditingResult(
            output_path=output_path,
            original_duration=original_duration,
            edited_duration=total_edited_duration,
            compression_ratio=compression_ratio,
            density_improvement=density_improvement,
            segments_count=len(analysis.key_segments)
        )

    # 注意：_create_text_transition 已废弃，使用 TransitionGenerator 替代
    # 参见 transition_generator.create_transition()

    def batch_process(
        self,
        input_dir: str,
        output_dir: str,
        **kwargs
    ) -> List[EditingResult]:
        """
        批量处理视频

        Args:
            input_dir: 输入目录
            output_dir: 输出目录
            **kwargs: 其他参数

        Returns:
            EditingResult列表
        """
        input_path = Path(input_dir)
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # 支持的视频格式
        video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.webm'}

        # 查找所有视频文件
        video_files = [
            f for f in input_path.iterdir()
            if f.suffix.lower() in video_extensions
        ]

        print(f"找到 {len(video_files)} 个视频文件")

        results = []
        for i, video_file in enumerate(video_files, 1):
            print(f"\n处理第 {i}/{len(video_files)} 个视频...")

            output_file = output_path / f"edited_{video_file.name}"

            try:
                result = self.process_video(
                    str(video_file),
                    str(output_file),
                    **kwargs
                )
                results.append(result)

            except Exception as e:
                print(f"错误: 处理 {video_file.name} 失败: {e}")
                continue

        print(f"\n批量处理完成！成功处理 {len(results)} 个视频")
        return results

    def get_preview(
        self,
        input_path: str,
        num_segments: int = 3
    ) -> Dict:
        """
        获取视频预览信息（不实际剪辑）

        Args:
            input_path: 输入视频路径
            num_segments: 预览片段数

        Returns:
            预览信息字典
        """
        # 转录
        transcript = self.transcriber.transcribe(input_path)

        # 分析
        analysis = self.analyzer.analyze(
            transcript,
            user_interests=self.config.interests,
            max_segments=num_segments
        )

        # 计算预估时长
        estimated_duration = sum(
            seg.end - seg.start
            for seg in analysis.key_segments
        )

        # 添加过渡时长
        if self.config.transition_style == "text":
            estimated_duration += (len(analysis.key_segments) - 1) * 2.0

        return {
            'original_duration': transcript.duration,
            'estimated_duration': estimated_duration,
            'compression_ratio': 1 - (estimated_duration / transcript.duration),
            'main_topics': analysis.main_topics,
            'summary': analysis.summary,
            'key_segments': [
                {
                    'start': seg.start,
                    'end': seg.end,
                    'topic': seg.topic,
                    'text': seg.text[:100] + '...',
                    'relevance': seg.relevance_score
                }
                for seg in analysis.key_segments
            ]
        }

    def process_youtube_video(
        self,
        youtube_url: str,
        output_path: str,
        quality: str = "720p",
        use_transcript: bool = True,
        **kwargs
    ) -> EditingResult:
        """
        处理 YouTube 视频

        Args:
            youtube_url: YouTube 视频 URL
            output_path: 输出路径
            quality: 下载质量 (480p, 720p, 1080p, best)
            use_transcript: 是否尝试使用 YouTube 字幕（如果可用）
            **kwargs: 其他参数

        Returns:
            EditingResult 对象
        """
        print(f"\n{'='*60}")
        print(f"处理 YouTube 视频: {youtube_url}")
        print(f"{'='*60}\n")

        # 步骤1: 下载视频
        print("步骤 1/5: 下载 YouTube 视频...")
        downloader = YouTubeDownloader()

        def progress_callback(d):
            if d['status'] == 'downloading':
                percent = d.get('_percent_str', 'N/A')
                speed = d.get('_speed_str', 'N/A')
                print(f"\r  下载进度: {percent} | 速度: {speed}", end='')

        try:
            video_info = downloader.download_video(
                youtube_url,
                quality=quality,
                progress_callback=progress_callback
            )
            print(f"\n  下载成功: {video_info['title']}")
        except Exception as e:
            raise Exception(f"下载 YouTube 视频失败: {e}")

        # 步骤2: 尝试获取字幕
        transcript_text = None
        if use_transcript:
            print("\n步骤 2/5: 尝试获取 YouTube 字幕...")
            try:
                transcript_text = downloader.get_transcript(
                    youtube_url,
                    languages=self.config.language.split('-')  # ['zh', 'CN'] 或 ['en']
                )
                if transcript_text:
                    print(f"  成功获取字幕（{len(transcript_text)} 字符）")
                    print("  提示: 使用 YouTube 字幕可以跳过语音识别，加快处理速度")
                else:
                    print("  未找到字幕，将使用语音识别")
            except Exception as e:
                print(f"  获取字幕失败: {e}")
                print("  将使用语音识别")

        # 步骤3: 处理下载的视频
        print("\n步骤 3/5: 处理视频...")

        # 如果有字幕，可以选择直接使用（需要转换为 Transcript 对象）
        # 或者仍然使用语音识别来获取时间戳
        # 这里我们仍然使用 process_video，它会进行完整的转录和分析

        result = self.process_video(
            video_info['filepath'],
            output_path,
            **kwargs
        )

        # 步骤4: 添加元数据
        print("\n步骤 4/5: 添加元数据...")
        result.youtube_metadata = {
            'url': youtube_url,
            'video_id': video_info['video_id'],
            'title': video_info['title'],
            'original_duration': video_info['duration'],
            'quality': quality,
            'has_transcript': transcript_text is not None
        }

        print(f"\n{'='*60}")
        print("YouTube 视频处理完成！")
        print(f"原始视频: {video_info['title']}")
        print(f"原始时长: {result.original_duration:.1f}秒")
        print(f"剪辑后时长: {result.edited_duration:.1f}秒")
        print(f"压缩率: {result.compression_ratio:.1%}")
        print(f"{'='*60}\n")

        return result

    def batch_process_youtube(
        self,
        youtube_urls: List[str],
        output_dir: str,
        quality: str = "720p",
        **kwargs
    ) -> List[EditingResult]:
        """
        批量处理 YouTube 视频

        Args:
            youtube_urls: YouTube 视频 URL 列表
            output_dir: 输出目录
            quality: 视频质量
            **kwargs: 其他参数

        Returns:
            EditingResult 列表
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        print(f"开始批量处理 {len(youtube_urls)} 个 YouTube 视频")

        results = []
        failed = []

        for i, url in enumerate(youtube_urls, 1):
            print(f"\n{'='*60}")
            print(f"处理第 {i}/{len(youtube_urls)} 个视频")
            print(f"{'='*60}")

            try:
                # 生成输出文件名
                downloader = YouTubeDownloader()
                video_id = downloader.extract_video_id(url)
                output_file = output_path / f"edited_{video_id}.mp4"

                # 处理视频
                result = self.process_youtube_video(
                    url,
                    str(output_file),
                    quality=quality,
                    **kwargs
                )
                results.append(result)

            except Exception as e:
                print(f"\n错误: 处理视频失败 ({url}): {e}")
                failed.append({'url': url, 'error': str(e)})
                continue

        print(f"\n{'='*60}")
        print(f"批量处理完成！成功: {len(results)}, 失败: {len(failed)}")
        print(f"{'='*60}")

        if failed:
            print("\n失败列表:")
            for item in failed:
                print(f"  - {item['url']}")
                print(f"    错误: {item['error']}")

        return results


if __name__ == "__main__":
    # 测试代码
    print("VideoEditor 模块已加载")

    # 示例用法
    # editor = VideoEditor(
    #     user_interests=["编程", "AI", "技术"],
    #     output_length="short"
    # )
    # result = editor.process_video(
    #     "data/input/video.mp4",
    #     "data/output/edited.mp4"
    # )
