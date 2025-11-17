"""
视频质量分析模块

自动评估视频片段的视觉和音频质量，并提供增强建议。
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import logging

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    np = None

try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False

try:
    from pydub import AudioSegment
    from pydub.effects import normalize
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class QualityMetrics:
    """质量指标"""
    # 视觉质量
    sharpness: float  # 清晰度 (0-100)
    brightness: float  # 亮度 (0-100)
    contrast: float   # 对比度 (0-100)
    color_balance: float  # 色彩平衡 (0-100)

    # 音频质量
    audio_loudness: float  # 音量 (dB)
    audio_noise: float  # 噪音水平 (0-100)
    audio_clarity: float  # 清晰度 (0-100)

    # 技术质量
    resolution: Tuple[int, int]  # 分辨率
    fps: float  # 帧率
    bitrate: int  # 码率 (kbps)

    # 综合评分
    overall_score: float  # 0-100

    def to_dict(self) -> Dict:
        """转换为字典"""
        return asdict(self)


class QualityAnalyzer:
    """视频质量分析器"""

    def __init__(self):
        """初始化质量分析器"""
        if not OPENCV_AVAILABLE:
            logger.warning("OpenCV 未安装，视觉分析功能将被禁用")
        if not PYDUB_AVAILABLE:
            logger.warning("pydub 未安装，音频分析功能将被禁用")

    def analyze_video(self, video_path: str, sample_count: int = 10) -> QualityMetrics:
        """
        分析视频质量

        Args:
            video_path: 视频文件路径
            sample_count: 采样帧数

        Returns:
            QualityMetrics对象
        """
        if not OPENCV_AVAILABLE:
            raise ImportError("请安装 OpenCV: pip install opencv-python")

        try:
            # 分析视觉质量
            visual_metrics = self._analyze_visual_quality(video_path, sample_count)

            # 分析音频质量
            audio_metrics = self._analyze_audio_quality(video_path)

            # 分析技术质量
            tech_metrics = self._analyze_technical_quality(video_path)

            # 计算综合评分
            overall_score = self._calculate_overall_score(
                visual_metrics,
                audio_metrics,
                tech_metrics
            )

            return QualityMetrics(
                **visual_metrics,
                **audio_metrics,
                **tech_metrics,
                overall_score=overall_score
            )
        except Exception as e:
            logger.error(f"分析视频质量失败: {e}")
            raise

    def _analyze_visual_quality(self, video_path: str, sample_count: int = 10) -> Dict:
        """分析视觉质量"""
        cap = cv2.VideoCapture(video_path)

        if not cap.isOpened():
            raise ValueError(f"无法打开视频文件: {video_path}")

        try:
            # 采样帧进行分析
            frames = self._sample_frames(cap, num_samples=sample_count)

            sharpness = self._calculate_sharpness(frames)
            brightness = self._calculate_brightness(frames)
            contrast = self._calculate_contrast(frames)
            color_balance = self._calculate_color_balance(frames)

            return {
                'sharpness': sharpness,
                'brightness': brightness,
                'contrast': contrast,
                'color_balance': color_balance
            }
        finally:
            cap.release()

    def _sample_frames(self, cap, num_samples: int = 10) -> List:
        """从视频中均匀采样帧"""
        frames = []

        # 获取总帧数
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        if total_frames <= 0:
            # 如果无法获取总帧数，采取备用方案
            total_frames = 300  # 假设30秒，10fps

        # 计算采样间隔
        sample_interval = max(1, total_frames // num_samples)

        frame_count = 0
        while len(frames) < num_samples:
            ret, frame = cap.read()
            if not ret:
                break

            if frame_count % sample_interval == 0:
                # 调整帧大小以加快处理
                resized = cv2.resize(frame, (320, 240))
                frames.append(resized)

            frame_count += 1

        # 如果没有采样到帧，返回黑色占位符
        if not frames and NUMPY_AVAILABLE:
            return [np.zeros((240, 320, 3), dtype=np.uint8)]
        return frames if frames else []

    def _calculate_sharpness(self, frames: List) -> float:
        """计算清晰度（使用Laplacian方差）"""
        if not OPENCV_AVAILABLE or not NUMPY_AVAILABLE:
            return 50.0  # 默认值

        sharpness_scores = []

        for frame in frames:
            # 转换为灰度图
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) if len(frame.shape) == 3 else frame

            # 计算Laplacian
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            variance = np.var(laplacian)

            # 将方差映射到0-100的范围（经验值）
            # 非常清晰的图像方差通常 > 500
            # 模糊的图像方差通常 < 100
            sharpness_score = min(100, max(0, (variance / 5)))
            sharpness_scores.append(sharpness_score)

        return np.mean(sharpness_scores) if sharpness_scores else 0

    def _calculate_brightness(self, frames: List) -> float:
        """计算亮度（相对于理想范围）"""
        if not OPENCV_AVAILABLE or not NUMPY_AVAILABLE:
            return 50.0  # 默认值

        brightness_scores = []
        ideal_brightness = 127  # 0-255范围的中间值
        ideal_range = 30  # 理想范围

        for frame in frames:
            # 转换为灰度图
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) if len(frame.shape) == 3 else frame

            # 计算平均亮度
            avg_brightness = np.mean(gray)

            # 计算与理想亮度的偏差
            deviation = abs(avg_brightness - ideal_brightness)

            # 映射到0-100的评分
            if deviation <= ideal_range:
                score = 100 - (deviation / ideal_range) * 50
            else:
                score = max(0, 100 - (deviation / ideal_range) * 100)

            brightness_scores.append(score)

        return np.mean(brightness_scores) if brightness_scores else 50

    def _calculate_contrast(self, frames: List) -> float:
        """计算对比度"""
        if not OPENCV_AVAILABLE or not NUMPY_AVAILABLE:
            return 50.0  # 默认值

        contrast_scores = []

        for frame in frames:
            # 转换为灰度图
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) if len(frame.shape) == 3 else frame

            # 计算标准差作为对比度的指标
            std_dev = np.std(gray)

            # 将标准差映射到0-100范围
            # 低对比度: std < 30, 高对比度: std > 80
            contrast_score = min(100, max(0, (std_dev / 80) * 100))
            contrast_scores.append(contrast_score)

        return np.mean(contrast_scores) if contrast_scores else 50

    def _calculate_color_balance(self, frames: List) -> float:
        """计算色彩平衡（RGB通道均衡度）"""
        if not OPENCV_AVAILABLE or not NUMPY_AVAILABLE:
            return 50.0  # 默认值

        color_scores = []

        for frame in frames:
            if len(frame.shape) != 3 or frame.shape[2] != 3:
                color_scores.append(50)
                continue

            # 分离RGB通道
            b, g, r = cv2.split(frame)

            # 计算每个通道的均值
            b_mean = np.mean(b)
            g_mean = np.mean(g)
            r_mean = np.mean(r)

            # 计算通道间的差异
            max_diff = max(
                abs(b_mean - g_mean),
                abs(g_mean - r_mean),
                abs(r_mean - b_mean)
            )

            # 将差异映射到0-100的评分
            # 完全平衡: diff = 0, 分数 = 100
            # 严重失衡: diff = 100, 分数 = 0
            color_score = max(0, 100 - max_diff)
            color_scores.append(color_score)

        return np.mean(color_scores) if color_scores else 50

    def _analyze_audio_quality(self, video_path: str) -> Dict:
        """分析音频质量"""
        audio_loudness = 0.0
        audio_noise = 50.0
        audio_clarity = 50.0

        if not PYDUB_AVAILABLE:
            logger.warning("pydub 未安装，使用默认音频质量值")
            return {
                'audio_loudness': audio_loudness,
                'audio_noise': audio_noise,
                'audio_clarity': audio_clarity
            }

        try:
            # 尝试使用ffmpeg提取音频
            audio = AudioSegment.from_file(video_path)

            # 计算音量（dBFS）
            audio_loudness = audio.dBFS

            # 计算噪音水平（基于静音帧比例）
            # 将音频分为小段，计算静音段比例
            frame_length = len(audio) // 100  # 分为100段
            if frame_length > 0:
                silent_count = 0
                for i in range(0, len(audio), frame_length):
                    segment = audio[i:i+frame_length]
                    if segment.dBFS < -40:  # 阈值：-40dBFS视为静音
                        silent_count += 1

                # 噪音分数：静音段越多，噪音越少
                audio_noise = (silent_count / 100) * 50 + 50
                audio_noise = min(100, audio_noise)

            # 计算清晰度（基于频域分析）
            # 简化方法：根据峰值因子来估计
            # 高峰值因子表示更清晰的音频
            rms = audio.rms
            peak = audio.max
            if rms > 0:
                peak_factor = peak / rms
                # 将峰值因子映射到0-100
                audio_clarity = min(100, max(0, (peak_factor - 2) * 10))

            return {
                'audio_loudness': float(audio_loudness),
                'audio_noise': float(audio_noise),
                'audio_clarity': float(audio_clarity)
            }
        except Exception as e:
            logger.warning(f"分析音频质量失败: {e}，使用默认值")
            return {
                'audio_loudness': audio_loudness,
                'audio_noise': audio_noise,
                'audio_clarity': audio_clarity
            }

    def _analyze_technical_quality(self, video_path: str) -> Dict:
        """分析技术质量"""
        cap = cv2.VideoCapture(video_path)

        if not cap.isOpened():
            raise ValueError(f"无法打开视频文件: {video_path}")

        try:
            # 获取分辨率
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            resolution = (width, height)

            # 获取帧率
            fps = cap.get(cv2.CAP_PROP_FPS)
            if fps == 0:
                fps = 30  # 默认值

            # 估计码率（基于文件大小和时长）
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            if total_frames <= 0:
                total_frames = 300

            bitrate = self._estimate_bitrate(video_path, fps, total_frames)

            return {
                'resolution': resolution,
                'fps': float(fps),
                'bitrate': bitrate
            }
        finally:
            cap.release()

    def _estimate_bitrate(self, video_path: str, fps: float, total_frames: int) -> int:
        """估计视频码率"""
        try:
            import os
            file_size = os.path.getsize(video_path)

            # 计算时长（秒）
            duration = total_frames / fps if fps > 0 else 0

            if duration > 0:
                # 码率 = 文件大小 / 时长
                bitrate_kbps = (file_size * 8) / (duration * 1000)
                return int(bitrate_kbps)
            else:
                return 5000  # 默认值
        except Exception as e:
            logger.warning(f"估计码率失败: {e}")
            return 5000

    def _calculate_overall_score(
        self,
        visual_metrics: Dict,
        audio_metrics: Dict,
        tech_metrics: Dict
    ) -> float:
        """计算综合质量评分"""
        # 视觉质量权重
        visual_score = (
            visual_metrics['sharpness'] * 0.35 +
            visual_metrics['brightness'] * 0.20 +
            visual_metrics['contrast'] * 0.25 +
            visual_metrics['color_balance'] * 0.20
        )

        # 音频质量权重
        # 规范化音量到0-100
        loudness_normalized = min(100, max(0, (audio_metrics['audio_loudness'] + 20) * 2.5))
        audio_score = (
            loudness_normalized * 0.40 +
            audio_metrics['audio_noise'] * 0.30 +
            audio_metrics['audio_clarity'] * 0.30
        )

        # 技术质量权重
        # 分辨率评分
        resolution = tech_metrics['resolution']
        if resolution[0] >= 1920 and resolution[1] >= 1080:
            resolution_score = 100
        elif resolution[0] >= 1280 and resolution[1] >= 720:
            resolution_score = 80
        elif resolution[0] >= 720 and resolution[1] >= 480:
            resolution_score = 60
        else:
            resolution_score = 40

        # 帧率评分
        fps = tech_metrics['fps']
        if fps >= 60:
            fps_score = 100
        elif fps >= 30:
            fps_score = 80
        elif fps >= 24:
            fps_score = 60
        else:
            fps_score = 40

        # 码率评分
        bitrate = tech_metrics['bitrate']
        if bitrate >= 10000:
            bitrate_score = 100
        elif bitrate >= 5000:
            bitrate_score = 80
        elif bitrate >= 2000:
            bitrate_score = 60
        else:
            bitrate_score = 40

        tech_score = (
            resolution_score * 0.40 +
            fps_score * 0.35 +
            bitrate_score * 0.25
        )

        # 综合评分：视觉 40%，音频 30%，技术 30%
        overall_score = (
            visual_score * 0.40 +
            audio_score * 0.30 +
            tech_score * 0.30
        )

        return round(overall_score, 1)

    def suggest_enhancements(self, metrics: QualityMetrics) -> List[str]:
        """根据质量指标提供增强建议"""
        suggestions = []

        # 清晰度建议
        if metrics.sharpness < 40:
            suggestions.append("🔍 建议：应用锐化滤镜提升清晰度（当前: {:.1f}/100）".format(metrics.sharpness))
        elif metrics.sharpness < 60:
            suggestions.append("🔍 建议：清晰度一般，可应用轻度锐化")

        # 亮度建议
        if metrics.brightness < 40:
            suggestions.append("☀️ 建议：视频过暗，建议提升亮度（当前: {:.1f}/100）".format(metrics.brightness))
        elif metrics.brightness > 85:
            suggestions.append("☀️ 建议：视频过亮，建议降低亮度以避免过曝（当前: {:.1f}/100）".format(metrics.brightness))

        # 对比度建议
        if metrics.contrast < 40:
            suggestions.append("⚪ 建议：对比度较低，建议增加对比度")
        elif metrics.contrast > 90:
            suggestions.append("⚪ 建议：对比度过高，可能导致信息丢失")

        # 色彩平衡建议
        if metrics.color_balance < 50:
            suggestions.append("🎨 建议：色彩失衡，建议进行色彩校正")

        # 音频建议
        if metrics.audio_loudness < -15:
            suggestions.append("🔊 建议：音量过低，建议提升音量（当前: {:.1f}dB）".format(metrics.audio_loudness))
        elif metrics.audio_loudness > 0:
            suggestions.append("🔊 建议：音量过高，建议降低以避免破音（当前: {:.1f}dB）".format(metrics.audio_loudness))

        if metrics.audio_noise > 60:
            suggestions.append("🎙️ 建议：检测到较多背景噪音，建议进行降噪处理")

        if metrics.audio_clarity < 50:
            suggestions.append("🎙️ 建议：音频清晰度不高，建议改进音频质量")

        # 分辨率建议
        width, height = metrics.resolution
        if width < 1280 or height < 720:
            suggestions.append("📺 建议：分辨率较低（{0}x{1}），建议使用至少720p的源视频".format(width, height))

        # 帧率建议
        if metrics.fps < 24:
            suggestions.append("🎬 建议：帧率过低（{:.1f}fps），可能导致卡顿感".format(metrics.fps))
        elif metrics.fps < 30:
            suggestions.append("🎬 建议：帧率一般（{:.1f}fps），建议提升到30fps或更高".format(metrics.fps))

        # 码率建议
        if metrics.bitrate < 2000:
            suggestions.append("📊 建议：码率较低（{0}kbps），可能影响视频质量".format(metrics.bitrate))

        # 综合评分建议
        if metrics.overall_score < 50:
            suggestions.append("❌ 综合评分较低，建议考虑使用质量更好的源视频")
        elif metrics.overall_score < 70:
            suggestions.append("⚠️ 综合评分一般，建议应用上述增强处理")
        else:
            suggestions.append("✅ 视频质量良好，无需特殊处理")

        return suggestions

    def generate_quality_report(self, metrics: QualityMetrics) -> str:
        """生成质量分析报告"""
        report = []
        report.append("=" * 70)
        report.append("视频质量分析报告")
        report.append("=" * 70)

        report.append("\n【视觉质量】")
        report.append(f"  清晰度:        {metrics.sharpness:6.1f}/100 {'█' * int(metrics.sharpness/5)}")
        report.append(f"  亮度:          {metrics.brightness:6.1f}/100 {'█' * int(metrics.brightness/5)}")
        report.append(f"  对比度:        {metrics.contrast:6.1f}/100 {'█' * int(metrics.contrast/5)}")
        report.append(f"  色彩平衡:      {metrics.color_balance:6.1f}/100 {'█' * int(metrics.color_balance/5)}")

        report.append("\n【音频质量】")
        report.append(f"  音量:          {metrics.audio_loudness:6.1f} dB")
        report.append(f"  噪音水平:      {metrics.audio_noise:6.1f}/100 {'█' * int(metrics.audio_noise/5)}")
        report.append(f"  清晰度:        {metrics.audio_clarity:6.1f}/100 {'█' * int(metrics.audio_clarity/5)}")

        report.append("\n【技术规格】")
        report.append(f"  分辨率:        {metrics.resolution[0]}x{metrics.resolution[1]}")
        report.append(f"  帧率:          {metrics.fps:.1f} fps")
        report.append(f"  码率:          {metrics.bitrate:,} kbps")

        report.append("\n【综合评分】")
        overall = metrics.overall_score
        if overall >= 80:
            level = "优秀 ✅"
        elif overall >= 70:
            level = "良好 ⭐"
        elif overall >= 60:
            level = "一般 ⚠️"
        else:
            level = "较差 ❌"

        report.append(f"  总体评分:      {overall:6.1f}/100 {'█' * int(overall/5)} {level}")

        report.append("\n【改进建议】")
        suggestions = self.suggest_enhancements(metrics)
        for suggestion in suggestions:
            report.append(f"  • {suggestion}")

        report.append("\n" + "=" * 70)

        return "\n".join(report)


if __name__ == "__main__":
    # 简单测试
    print("质量分析器模块已加载")

    # 示例用法
    # analyzer = QualityAnalyzer()
    # metrics = analyzer.analyze_video("video.mp4")
    # print(analyzer.generate_quality_report(metrics))
