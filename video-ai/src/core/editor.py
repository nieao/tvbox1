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
from ..services.personalization import PersonalizationConfig


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
        config: Optional[PersonalizationConfig] = None
    ):
        """
        初始化视频编辑器

        Args:
            user_interests: 用户兴趣列表
            output_length: 输出长度 ('short', 'medium', 'long')
            config: 个性化配置对象
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
        # 加载视频
        video = VideoFileClip(input_path)
        original_duration = video.duration

        # 提取关键片段
        clips = []
        total_edited_duration = 0

        for i, segment in enumerate(analysis.key_segments):
            print(f"  提取片段 {i+1}/{len(analysis.key_segments)}: "
                  f"{segment.start:.1f}s - {segment.end:.1f}s "
                  f"(主题: {segment.topic})")

            # 提取子片段
            subclip = video.subclip(segment.start, segment.end)

            # 如果配置了过渡效果，添加文字卡片
            if self.config.transition_style == "text" and i > 0:
                transition_clip = self._create_text_transition(
                    segment.topic,
                    duration=2.0
                )
                clips.append(transition_clip)
                total_edited_duration += 2.0

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

    def _create_text_transition(
        self,
        text: str,
        duration: float = 2.0
    ) -> CompositeVideoClip:
        """创建文字过渡卡片"""
        try:
            # 创建文字片段
            txt_clip = TextClip(
                text,
                fontsize=48,
                color='white',
                bg_color='black',
                size=(1920, 1080),
                method='caption',
                align='center'
            ).set_duration(duration)

            return txt_clip

        except Exception as e:
            print(f"  警告: 无法创建文字过渡 ({e})，跳过")
            # 如果TextClip失败，返回黑色片段
            from moviepy.editor import ColorClip
            return ColorClip(
                size=(1920, 1080),
                color=(0, 0, 0),
                duration=duration
            )

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
