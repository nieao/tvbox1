"""
视频转录模块

使用 Whisper 等模型将视频转换为文本，支持多语言和时间戳。
"""

import os
from typing import Optional, Dict, List
from dataclasses import dataclass
from pathlib import Path

try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False

try:
    from faster_whisper import WhisperModel
    FASTER_WHISPER_AVAILABLE = True
except ImportError:
    FASTER_WHISPER_AVAILABLE = False


@dataclass
class TranscriptSegment:
    """转录片段数据类"""
    start: float  # 开始时间（秒）
    end: float    # 结束时间（秒）
    text: str     # 文本内容
    confidence: float = 1.0  # 置信度


@dataclass
class Transcript:
    """完整转录结果"""
    segments: List[TranscriptSegment]
    language: str
    duration: float
    full_text: str


class VideoTranscriber:
    """视频转录器"""

    def __init__(
        self,
        model_name: str = "base",
        device: str = "cuda",
        compute_type: str = "float16",
        use_faster_whisper: bool = True
    ):
        """
        初始化转录器

        Args:
            model_name: Whisper模型名称 (tiny, base, small, medium, large)
            device: 计算设备 (cuda, cpu)
            compute_type: 计算类型 (float16, int8)
            use_faster_whisper: 是否使用faster-whisper（更快）
        """
        self.model_name = model_name
        self.device = device
        self.compute_type = compute_type
        self.use_faster_whisper = use_faster_whisper

        # 加载模型
        self.model = self._load_model()

    def _load_model(self):
        """加载Whisper模型"""
        if self.use_faster_whisper and FASTER_WHISPER_AVAILABLE:
            print(f"加载 Faster-Whisper 模型: {self.model_name}")
            return WhisperModel(
                self.model_name,
                device=self.device,
                compute_type=self.compute_type
            )
        elif WHISPER_AVAILABLE:
            print(f"加载 Whisper 模型: {self.model_name}")
            return whisper.load_model(self.model_name, device=self.device)
        else:
            raise ImportError(
                "请安装 whisper 或 faster-whisper:\n"
                "pip install openai-whisper\n"
                "或\n"
                "pip install faster-whisper"
            )

    def transcribe(
        self,
        video_path: str,
        language: Optional[str] = None,
        **kwargs
    ) -> Transcript:
        """
        转录视频

        Args:
            video_path: 视频文件路径
            language: 语言代码 (如 'zh', 'en')，None表示自动检测
            **kwargs: 其他Whisper参数

        Returns:
            Transcript对象
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"视频文件不存在: {video_path}")

        print(f"开始转录视频: {video_path}")

        # 提取音频
        audio_path = self._extract_audio(video_path)

        try:
            # 执行转录
            if self.use_faster_whisper and FASTER_WHISPER_AVAILABLE:
                result = self._transcribe_faster_whisper(
                    audio_path, language, **kwargs
                )
            else:
                result = self._transcribe_whisper(
                    audio_path, language, **kwargs
                )

            print(f"转录完成！检测到语言: {result.language}")
            return result

        finally:
            # 清理临时音频文件
            if os.path.exists(audio_path):
                os.remove(audio_path)

    def _extract_audio(self, video_path: str) -> str:
        """从视频中提取音频"""
        import subprocess

        audio_path = video_path.rsplit('.', 1)[0] + '_temp_audio.wav'

        cmd = [
            'ffmpeg', '-i', video_path,
            '-vn',  # 不包含视频
            '-acodec', 'pcm_s16le',  # 音频编码
            '-ar', '16000',  # 采样率
            '-ac', '1',  # 单声道
            '-y',  # 覆盖已存在文件
            audio_path
        ]

        print("提取音频...")
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

        return audio_path

    def _transcribe_faster_whisper(
        self,
        audio_path: str,
        language: Optional[str],
        **kwargs
    ) -> Transcript:
        """使用faster-whisper转录"""
        segments, info = self.model.transcribe(
            audio_path,
            language=language,
            beam_size=kwargs.get('beam_size', 5),
            **kwargs
        )

        transcript_segments = []
        full_text_parts = []

        for segment in segments:
            transcript_segments.append(TranscriptSegment(
                start=segment.start,
                end=segment.end,
                text=segment.text.strip(),
                confidence=getattr(segment, 'avg_logprob', 1.0)
            ))
            full_text_parts.append(segment.text.strip())

        return Transcript(
            segments=transcript_segments,
            language=info.language,
            duration=info.duration,
            full_text=' '.join(full_text_parts)
        )

    def _transcribe_whisper(
        self,
        audio_path: str,
        language: Optional[str],
        **kwargs
    ) -> Transcript:
        """使用标准whisper转录"""
        result = self.model.transcribe(
            audio_path,
            language=language,
            **kwargs
        )

        transcript_segments = []
        for segment in result['segments']:
            transcript_segments.append(TranscriptSegment(
                start=segment['start'],
                end=segment['end'],
                text=segment['text'].strip()
            ))

        return Transcript(
            segments=transcript_segments,
            language=result.get('language', language or 'unknown'),
            duration=result['segments'][-1]['end'] if result['segments'] else 0,
            full_text=result['text'].strip()
        )

    def save_transcript(self, transcript: Transcript, output_path: str):
        """
        保存转录结果

        Args:
            transcript: 转录结果
            output_path: 输出文件路径（支持 .txt, .srt, .json）
        """
        output_path = Path(output_path)
        ext = output_path.suffix.lower()

        if ext == '.txt':
            self._save_as_txt(transcript, output_path)
        elif ext == '.srt':
            self._save_as_srt(transcript, output_path)
        elif ext == '.json':
            self._save_as_json(transcript, output_path)
        else:
            raise ValueError(f"不支持的输出格式: {ext}")

        print(f"转录结果已保存: {output_path}")

    def _save_as_txt(self, transcript: Transcript, output_path: Path):
        """保存为纯文本"""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(transcript.full_text)

    def _save_as_srt(self, transcript: Transcript, output_path: Path):
        """保存为SRT字幕格式"""
        with open(output_path, 'w', encoding='utf-8') as f:
            for i, segment in enumerate(transcript.segments, 1):
                # SRT格式：序号、时间范围、文本、空行
                f.write(f"{i}\n")
                f.write(f"{self._format_timestamp(segment.start)} --> "
                       f"{self._format_timestamp(segment.end)}\n")
                f.write(f"{segment.text}\n\n")

    def _save_as_json(self, transcript: Transcript, output_path: Path):
        """保存为JSON格式"""
        import json

        data = {
            'language': transcript.language,
            'duration': transcript.duration,
            'full_text': transcript.full_text,
            'segments': [
                {
                    'start': seg.start,
                    'end': seg.end,
                    'text': seg.text,
                    'confidence': seg.confidence
                }
                for seg in transcript.segments
            ]
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    @staticmethod
    def _format_timestamp(seconds: float) -> str:
        """格式化时间戳为SRT格式 (HH:MM:SS,mmm)"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


if __name__ == "__main__":
    # 测试代码
    transcriber = VideoTranscriber(model_name="base", device="cpu")

    # 示例：转录视频
    # transcript = transcriber.transcribe("data/input/video.mp4", language="zh")
    # print(f"转录文本: {transcript.full_text[:200]}...")
    # transcriber.save_transcript(transcript, "data/output/transcript.srt")

    print("VideoTranscriber 模块已加载")
