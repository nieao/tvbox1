"""
场景检测模块

智能识别视频中的场景变化，确保片段切割点更自然。
支持多种检测方法：帧差法、直方图法、深度学习法、混合法。
"""

from typing import List, Tuple, Optional, Dict
from dataclasses import dataclass, field
import logging
from pathlib import Path
from enum import Enum
import json
from datetime import datetime

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

logger = logging.getLogger(__name__)


class SceneType(Enum):
    """场景类型"""
    STATIC = "static"          # 静态场景
    ACTION = "action"          # 动作场景
    DIALOG = "dialog"          # 对话场景
    TRANSITION = "transition"  # 过渡/切换
    TEXT_HEAVY = "text_heavy"  # 文字密集
    SCENE_CHANGE = "scene_change"  # 场景变化
    UNKNOWN = "unknown"        # 未知


@dataclass
class Scene:
    """场景信息"""
    start_frame: int
    end_frame: int
    start_time: float
    end_time: float
    scene_type: SceneType = SceneType.UNKNOWN
    confidence: float = 0.5

    # 额外的场景分析信息
    motion_level: float = 0.0      # 运动强度 (0-1)
    color_change: float = 0.0      # 颜色变化程度 (0-1)
    brightness_change: float = 0.0  # 亮度变化 (0-1)
    edge_density: float = 0.0       # 边缘密度 (0-1)

    metadata: Dict = field(default_factory=dict)

    @property
    def duration(self) -> float:
        """返回场景时长（秒）"""
        return self.end_time - self.start_time

    @property
    def frame_count(self) -> int:
        """返回场景帧数"""
        return self.end_frame - self.start_frame

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'start_frame': self.start_frame,
            'end_frame': self.end_frame,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'duration': self.duration,
            'scene_type': self.scene_type.value,
            'confidence': self.confidence,
            'motion_level': self.motion_level,
            'color_change': self.color_change,
            'brightness_change': self.brightness_change,
            'edge_density': self.edge_density,
            'metadata': self.metadata
        }


class SceneDetector:
    """场景检测器

    支持多种检测方法：
    - frame_diff: 基于帧差的检测
    - histogram: 基于直方图的检测
    - motion: 基于光流的检测检测
    - hybrid: 混合检测方法
    """

    # 检测方法常数
    METHOD_FRAME_DIFF = "frame_diff"
    METHOD_HISTOGRAM = "histogram"
    METHOD_MOTION = "motion"
    METHOD_HYBRID = "hybrid"

    def __init__(
        self,
        method: str = "hybrid",
        threshold: float = 30.0,
        min_scene_length: float = 0.5,  # 最小场景长度（秒）
        max_scene_length: float = 120.0,  # 最大场景长度（秒）
        smooth_window: int = 5,  # 平滑窗口大小
        frame_sampling: int = 1  # 帧采样率（每N帧采样一次）
    ):
        """
        初始化场景检测器

        Args:
            method: 检测方法
            threshold: 检测阈值
            min_scene_length: 最小场景长度(秒)
            max_scene_length: 最大场景长度(秒)
            smooth_window: 平滑窗口大小
            frame_sampling: 帧采样率
        """
        self.method = method
        self.threshold = threshold
        self.min_scene_length = min_scene_length
        self.max_scene_length = max_scene_length
        self.smooth_window = smooth_window
        self.frame_sampling = frame_sampling

        logger.info(f"初始化场景检测器: method={method}, threshold={threshold}")

    def detect_scenes(self, video_path: str, debug: bool = False) -> List[Scene]:
        """
        检测视频中的场景

        Args:
            video_path: 视频文件路径
            debug: 是否输出调试信息

        Returns:
            Scene列表，按时间排序
        """
        logger.info(f"开始检测场景: {video_path}")

        # 检查依赖性
        if not CV2_AVAILABLE or not NUMPY_AVAILABLE:
            logger.error("场景检测需要 OpenCV 和 NumPy")
            raise ImportError("场景检测需要安装 opencv-python 和 numpy")

        if not Path(video_path).exists():
            raise FileNotFoundError(f"视频文件不存在: {video_path}")

        # 根据选择的方法进行检测
        if self.method == self.METHOD_FRAME_DIFF:
            scenes = self._detect_by_frame_diff(video_path, debug)
        elif self.method == self.METHOD_HISTOGRAM:
            scenes = self._detect_by_histogram(video_path, debug)
        elif self.method == self.METHOD_MOTION:
            scenes = self._detect_by_motion(video_path, debug)
        else:  # hybrid
            scenes = self._detect_hybrid(video_path, debug)

        # 后处理：合并短的场景和优化边界
        scenes = self._postprocess_scenes(scenes, video_path)

        logger.info(f"检测完成: 共 {len(scenes)} 个场景")

        return scenes

    def _detect_by_frame_diff(self, video_path: str, debug: bool = False) -> List[Scene]:
        """基于帧差的场景检测"""
        logger.info("使用帧差法进行场景检测...")

        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        if fps == 0:
            raise ValueError(f"无效的视频: {video_path}")

        scenes = []
        frame_diffs = []
        prev_frame = None
        frame_idx = 0

        logger.info(f"视频参数: FPS={fps:.1f}, 总帧数={total_frames}")

        # 逐帧处理
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            if frame_idx % self.frame_sampling != 0:
                frame_idx += 1
                continue

            # 缩小图像以加速处理
            small_frame = cv2.resize(frame, (320, 180))

            if prev_frame is not None:
                # 计算帧差（使用绝对差值）
                diff = cv2.absdiff(small_frame, prev_frame)
                diff_score = np.mean(diff)
                frame_diffs.append(diff_score)
            else:
                frame_diffs.append(0.0)

            prev_frame = small_frame
            frame_idx += 1

        cap.release()

        # 平滑帧差序列
        smoothed_diffs = self._smooth_sequence(frame_diffs, self.smooth_window)

        # 检测场景切换点
        scene_changes = []
        for i in range(1, len(smoothed_diffs)):
            if smoothed_diffs[i] > self.threshold:
                # 使用原始采样帧号
                actual_frame = i * self.frame_sampling
                scene_changes.append((actual_frame, smoothed_diffs[i]))

        # 将切换点转换为场景
        if scene_changes:
            prev_frame = 0
            for change_frame, diff_score in scene_changes:
                confidence = min(diff_score / 100, 1.0)
                scenes.append(Scene(
                    start_frame=prev_frame,
                    end_frame=change_frame,
                    start_time=prev_frame / fps,
                    end_time=change_frame / fps,
                    scene_type=SceneType.SCENE_CHANGE,
                    confidence=confidence,
                    color_change=confidence,
                    metadata={'method': 'frame_diff', 'diff_score': float(diff_score)}
                ))
                prev_frame = change_frame

            # 添加最后一个场景
            if prev_frame < total_frames:
                scenes.append(Scene(
                    start_frame=prev_frame,
                    end_frame=total_frames,
                    start_time=prev_frame / fps,
                    end_time=total_frames / fps,
                    scene_type=SceneType.UNKNOWN,
                    confidence=0.5,
                    metadata={'method': 'frame_diff'}
                ))
        else:
            # 如果没有检测到切换，整个视频作为一个场景
            scenes.append(Scene(
                start_frame=0,
                end_frame=total_frames,
                start_time=0.0,
                end_time=total_frames / fps,
                scene_type=SceneType.UNKNOWN,
                confidence=0.5,
                metadata={'method': 'frame_diff'}
            ))

        if debug:
            logger.debug(f"帧差法: 检测到 {len(scenes)} 个场景")

        return scenes

    def _detect_by_histogram(self, video_path: str, debug: bool = False) -> List[Scene]:
        """基于直方图的场景检测"""
        logger.info("使用直方图法进行场景检测...")

        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        if fps == 0:
            raise ValueError(f"无效的视频: {video_path}")

        scenes = []
        hist_diffs = []
        prev_hist = None
        frame_idx = 0

        # 逐帧处理
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            if frame_idx % self.frame_sampling != 0:
                frame_idx += 1
                continue

            # 转换为HSV以更好地捕捉颜色变化
            hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

            # 计算直方图（只用H通道表示颜色）
            hist = cv2.calcHist(
                [hsv_frame],
                [0],  # H通道
                None,
                [64],  # 64个bin
                [0, 180]
            )
            hist = cv2.normalize(hist, hist).flatten()

            if prev_hist is not None:
                # 计算直方图相似度（使用Bhattacharyya距离）
                diff = cv2.compareHist(hist, prev_hist, cv2.HISTCMP_BHATTACHARYYA)
                hist_diffs.append(diff)
            else:
                hist_diffs.append(0.0)

            prev_hist = hist
            frame_idx += 1

        cap.release()

        # 平滑直方图差异序列
        smoothed_diffs = self._smooth_sequence(hist_diffs, self.smooth_window)

        # 检测场景切换点
        scene_changes = []
        threshold = self.threshold / 100  # 将阈值转换为合适的范围

        for i in range(1, len(smoothed_diffs)):
            if smoothed_diffs[i] > threshold:
                actual_frame = i * self.frame_sampling
                scene_changes.append((actual_frame, smoothed_diffs[i]))

        # 将切换点转换为场景
        if scene_changes:
            prev_frame = 0
            for change_frame, diff_score in scene_changes:
                confidence = min(diff_score * 10, 1.0)  # 缩放到0-1
                scenes.append(Scene(
                    start_frame=prev_frame,
                    end_frame=change_frame,
                    start_time=prev_frame / fps,
                    end_time=change_frame / fps,
                    scene_type=SceneType.SCENE_CHANGE,
                    confidence=confidence,
                    color_change=confidence,
                    metadata={'method': 'histogram', 'hist_diff': float(diff_score)}
                ))
                prev_frame = change_frame

            # 添加最后一个场景
            if prev_frame < total_frames:
                scenes.append(Scene(
                    start_frame=prev_frame,
                    end_frame=total_frames,
                    start_time=prev_frame / fps,
                    end_time=total_frames / fps,
                    scene_type=SceneType.UNKNOWN,
                    confidence=0.5,
                    metadata={'method': 'histogram'}
                ))
        else:
            # 如果没有检测到切换，整个视频作为一个场景
            scenes.append(Scene(
                start_frame=0,
                end_frame=total_frames,
                start_time=0.0,
                end_time=total_frames / fps,
                scene_type=SceneType.UNKNOWN,
                confidence=0.5,
                metadata={'method': 'histogram'}
            ))

        if debug:
            logger.debug(f"直方图法: 检测到 {len(scenes)} 个场景")

        return scenes

    def _detect_by_motion(self, video_path: str, debug: bool = False) -> List[Scene]:
        """基于光流的运动检测"""
        logger.info("使用光流法进行场景检测...")

        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        if fps == 0:
            raise ValueError(f"无效的视频: {video_path}")

        scenes = []
        motion_scores = []
        prev_gray = None
        frame_idx = 0

        # 初始化光流计算器
        flow = None

        # 逐帧处理
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            if frame_idx % (self.frame_sampling * 2) != 0:  # 每2帧采样一次（加快速度）
                frame_idx += 1
                continue

            # 缩小图像
            small_frame = cv2.resize(frame, (320, 180))
            gray = cv2.cvtColor(small_frame, cv2.COLOR_BGR2GRAY)

            if prev_gray is not None:
                # 计算光流
                flow = cv2.calcOpticalFlowFarneback(
                    prev_gray, gray, None, 0.5, 3, 15, 3, 5, 1.2, 0
                )

                # 计算运动幅度
                mag, ang = cv2.cartToPolar(flow[..., 0], flow[..., 1])
                motion_score = np.mean(mag)
                motion_scores.append(motion_score)
            else:
                motion_scores.append(0.0)

            prev_gray = gray
            frame_idx += 1

        cap.release()

        # 平滑运动分数
        smoothed_scores = self._smooth_sequence(motion_scores, self.smooth_window)

        # 检测运动变化（高运动到低运动或反之）
        scene_changes = []
        threshold = self.threshold / 50  # 调整阈值

        for i in range(1, len(smoothed_scores) - 1):
            # 检测运动强度的显著变化
            if abs(smoothed_scores[i] - smoothed_scores[i-1]) > threshold:
                actual_frame = i * self.frame_sampling * 2
                scene_changes.append((actual_frame, abs(smoothed_scores[i] - smoothed_scores[i-1])))

        # 将切换点转换为场景
        if scene_changes:
            prev_frame = 0
            for change_frame, diff_score in scene_changes:
                confidence = min(diff_score, 1.0)
                motion_level = min(smoothed_scores[change_frame // (self.frame_sampling * 2)] if change_frame < len(smoothed_scores) * self.frame_sampling * 2 else 0.5, 1.0)

                scenes.append(Scene(
                    start_frame=prev_frame,
                    end_frame=change_frame,
                    start_time=prev_frame / fps,
                    end_time=change_frame / fps,
                    scene_type=SceneType.ACTION if motion_level > 0.5 else SceneType.STATIC,
                    confidence=confidence,
                    motion_level=motion_level,
                    metadata={'method': 'motion', 'motion_change': float(diff_score)}
                ))
                prev_frame = change_frame

            # 添加最后一个场景
            if prev_frame < total_frames:
                scenes.append(Scene(
                    start_frame=prev_frame,
                    end_frame=total_frames,
                    start_time=prev_frame / fps,
                    end_time=total_frames / fps,
                    scene_type=SceneType.UNKNOWN,
                    confidence=0.5,
                    metadata={'method': 'motion'}
                ))
        else:
            # 没有检测到变化
            scenes.append(Scene(
                start_frame=0,
                end_frame=total_frames,
                start_time=0.0,
                end_time=total_frames / fps,
                scene_type=SceneType.UNKNOWN,
                confidence=0.5,
                metadata={'method': 'motion'}
            ))

        if debug:
            logger.debug(f"光流法: 检测到 {len(scenes)} 个场景")

        return scenes

    def _detect_hybrid(self, video_path: str, debug: bool = False) -> List[Scene]:
        """混合检测方法 - 结合帧差法和直方图法"""
        logger.info("使用混合法进行场景检测...")

        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        if fps == 0:
            raise ValueError(f"无效的视频: {video_path}")

        scenes = []
        frame_diffs = []
        hist_diffs = []
        motion_scores = []
        prev_frame = None
        prev_gray = None
        prev_hist = None
        frame_idx = 0

        # 逐帧处理
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            if frame_idx % self.frame_sampling != 0:
                frame_idx += 1
                continue

            small_frame = cv2.resize(frame, (320, 180))
            gray = cv2.cvtColor(small_frame, cv2.COLOR_BGR2GRAY)
            hsv_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2HSV)

            if prev_frame is not None:
                # 帧差
                diff = cv2.absdiff(small_frame, prev_frame)
                diff_score = np.mean(diff)
                frame_diffs.append(diff_score)

                # 直方图
                hist = cv2.calcHist([hsv_frame], [0], None, [64], [0, 180])
                hist = cv2.normalize(hist, hist).flatten()
                if prev_hist is not None:
                    hist_diff = cv2.compareHist(hist, prev_hist, cv2.HISTCMP_BHATTACHARYYA)
                    hist_diffs.append(hist_diff)
                else:
                    hist_diffs.append(0.0)
                prev_hist = hist

                # 运动
                if prev_gray is not None:
                    flow = cv2.calcOpticalFlowFarneback(
                        prev_gray, gray, None, 0.5, 3, 15, 3, 5, 1.2, 0
                    )
                    mag, _ = cv2.cartToPolar(flow[..., 0], flow[..., 1])
                    motion_scores.append(np.mean(mag))
                else:
                    motion_scores.append(0.0)
            else:
                frame_diffs.append(0.0)
                hist_diffs.append(0.0)
                motion_scores.append(0.0)
                prev_hist = cv2.calcHist([hsv_frame], [0], None, [64], [0, 180])
                prev_hist = cv2.normalize(prev_hist, prev_hist).flatten()

            prev_frame = small_frame
            prev_gray = gray
            frame_idx += 1

        cap.release()

        # 平滑所有分数
        smoothed_diffs = self._smooth_sequence(frame_diffs, self.smooth_window)
        smoothed_hists = self._smooth_sequence([h * 100 for h in hist_diffs], self.smooth_window)
        smoothed_motion = self._smooth_sequence(motion_scores, self.smooth_window)

        # 融合多个信号 - 加权组合
        combined_scores = []
        for i in range(len(smoothed_diffs)):
            # 权重配置
            score = (
                smoothed_diffs[i] * 0.4 +          # 40% 帧差
                smoothed_hists[i] * 0.3 +          # 30% 直方图
                (smoothed_motion[i] if i < len(smoothed_motion) else 0) * 0.3  # 30% 运动
            )
            combined_scores.append(score)

        # 检测场景变化
        scene_changes = []
        for i in range(1, len(combined_scores)):
            if combined_scores[i] > self.threshold:
                actual_frame = i * self.frame_sampling
                scene_changes.append((actual_frame, combined_scores[i]))

        # 转换为场景
        if scene_changes:
            prev_frame = 0
            for change_frame, score in scene_changes:
                confidence = min(score / 100, 1.0)

                # 根据各个信号判断场景类型
                idx = change_frame // self.frame_sampling
                motion_level = smoothed_motion[idx] if idx < len(smoothed_motion) else 0
                color_change = smoothed_hists[idx] if idx < len(smoothed_hists) else 0

                if motion_level > 0.5:
                    scene_type = SceneType.ACTION
                elif color_change > 20:
                    scene_type = SceneType.TRANSITION
                else:
                    scene_type = SceneType.SCENE_CHANGE

                scenes.append(Scene(
                    start_frame=prev_frame,
                    end_frame=change_frame,
                    start_time=prev_frame / fps,
                    end_time=change_frame / fps,
                    scene_type=scene_type,
                    confidence=confidence,
                    motion_level=motion_level,
                    color_change=color_change / 100,
                    metadata={
                        'method': 'hybrid',
                        'combined_score': float(score),
                        'frame_diff': float(smoothed_diffs[idx] if idx < len(smoothed_diffs) else 0),
                        'hist_diff': float(smoothed_hists[idx] if idx < len(smoothed_hists) else 0),
                        'motion': float(motion_level)
                    }
                ))
                prev_frame = change_frame

            # 添加最后一个场景
            if prev_frame < total_frames:
                scenes.append(Scene(
                    start_frame=prev_frame,
                    end_frame=total_frames,
                    start_time=prev_frame / fps,
                    end_time=total_frames / fps,
                    scene_type=SceneType.UNKNOWN,
                    confidence=0.5,
                    metadata={'method': 'hybrid'}
                ))
        else:
            # 没有检测到变化
            scenes.append(Scene(
                start_frame=0,
                end_frame=total_frames,
                start_time=0.0,
                end_time=total_frames / fps,
                scene_type=SceneType.UNKNOWN,
                confidence=0.5,
                metadata={'method': 'hybrid'}
            ))

        if debug:
            logger.debug(f"混合法: 检测到 {len(scenes)} 个场景")

        return scenes

    def _postprocess_scenes(self, scenes: List[Scene], video_path: str) -> List[Scene]:
        """后处理：合并短场景、优化边界、分类场景类型"""
        if not scenes:
            return scenes

        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        cap.release()

        # 步骤1：合并过短的场景
        merged_scenes = []
        for scene in scenes:
            if scene.duration >= self.min_scene_length or len(merged_scenes) == 0:
                merged_scenes.append(scene)
            else:
                # 将其合并到前一个场景
                if merged_scenes:
                    merged_scenes[-1].end_frame = scene.end_frame
                    merged_scenes[-1].end_time = scene.end_time

        # 步骤2：分割过长的场景（仅作为标记）
        final_scenes = []
        for scene in merged_scenes:
            if scene.duration > self.max_scene_length:
                # 添加标记但不分割
                scene.metadata['too_long'] = True
            final_scenes.append(scene)

        # 步骤3：分析场景类型
        for i, scene in enumerate(final_scenes):
            # 根据运动和颜色变化推断场景类型
            if scene.motion_level > 0.6:
                if scene.scene_type == SceneType.UNKNOWN:
                    scene.scene_type = SceneType.ACTION
            elif scene.color_change > 0.3:
                if scene.scene_type == SceneType.UNKNOWN:
                    scene.scene_type = SceneType.TRANSITION

        return final_scenes

    @staticmethod
    def _smooth_sequence(sequence: List[float], window_size: int = 5) -> List[float]:
        """使用移动平均法平滑序列"""
        if window_size <= 1:
            return sequence

        smoothed = []
        for i in range(len(sequence)):
            start = max(0, i - window_size // 2)
            end = min(len(sequence), i + window_size // 2 + 1)
            window = sequence[start:end]

            # 计算平均值
            if NUMPY_AVAILABLE:
                smoothed.append(np.mean(window))
            else:
                # 手动计算平均值
                smoothed.append(sum(window) / len(window) if window else 0)

        return smoothed

    def optimize_scene_boundaries(
        self,
        scenes: List[Scene],
        transcript_segments: Optional[List] = None
    ) -> List[Scene]:
        """
        优化场景边界，确保不在句子/单词中间切断

        Args:
            scenes: 检测到的场景列表
            transcript_segments: 转录文本段，用于对齐边界

        Returns:
            优化后的场景列表
        """
        if not transcript_segments:
            # 如果没有转录信息，直接返回
            return scenes

        logger.info("优化场景边界...")

        optimized_scenes = []
        for scene in scenes:
            # 找到与场景边界最接近的转录段边界

            # 优化开始时间
            start_time = scene.start_time
            for seg in transcript_segments:
                if seg.start <= start_time < seg.end:
                    # 如果在段中间，向后移动到段的开始
                    if start_time - seg.start > seg.end - start_time:
                        start_time = seg.end
                    else:
                        start_time = seg.start
                    break

            # 优化结束时间
            end_time = scene.end_time
            for seg in transcript_segments:
                if seg.start < end_time <= seg.end:
                    # 如果在段中间，向前移动到段的结束
                    if end_time - seg.start > seg.end - end_time:
                        end_time = seg.end
                    else:
                        end_time = seg.start
                    break

            # 如果优化后的时间有效，更新场景
            if start_time < end_time:
                scene.start_time = start_time
                scene.end_time = end_time

            optimized_scenes.append(scene)

        logger.info("场景边界优化完成")
        return optimized_scenes

    def get_statistics(self, scenes: List[Scene]) -> Dict:
        """获取场景检测统计信息"""
        if not scenes:
            return {
                'total_scenes': 0,
                'total_duration': 0,
                'average_duration': 0,
                'scene_types': {},
                'confidence_stats': {}
            }

        # 按类型分组
        scene_types = {}
        for scene in scenes:
            scene_type = scene.scene_type.value
            scene_types[scene_type] = scene_types.get(scene_type, 0) + 1

        # 置信度统计
        confidences = [scene.confidence for scene in scenes]

        return {
            'total_scenes': len(scenes),
            'total_duration': sum(s.duration for s in scenes),
            'average_duration': sum(s.duration for s in scenes) / len(scenes) if scenes else 0,
            'min_duration': min(s.duration for s in scenes) if scenes else 0,
            'max_duration': max(s.duration for s in scenes) if scenes else 0,
            'scene_types': scene_types,
            'confidence_stats': {
                'min': min(confidences) if confidences else 0,
                'max': max(confidences) if confidences else 0,
                'average': sum(confidences) / len(confidences) if confidences else 0
            }
        }

    def save_scenes(self, scenes: List[Scene], output_path: str):
        """将场景信息保存为JSON文件"""
        data = {
            'detection_method': self.method,
            'timestamp': datetime.now().isoformat(),
            'threshold': self.threshold,
            'scenes': [scene.to_dict() for scene in scenes],
            'statistics': self.get_statistics(scenes)
        }

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        logger.info(f"场景信息已保存: {output_path}")

    def load_scenes(self, json_path: str) -> List[Scene]:
        """从JSON文件加载场景信息"""
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        scenes = []
        for scene_data in data.get('scenes', []):
            scene = Scene(
                start_frame=scene_data['start_frame'],
                end_frame=scene_data['end_frame'],
                start_time=scene_data['start_time'],
                end_time=scene_data['end_time'],
                scene_type=SceneType(scene_data.get('scene_type', 'unknown')),
                confidence=scene_data.get('confidence', 0.5),
                motion_level=scene_data.get('motion_level', 0.0),
                color_change=scene_data.get('color_change', 0.0),
                brightness_change=scene_data.get('brightness_change', 0.0),
                edge_density=scene_data.get('edge_density', 0.0),
                metadata=scene_data.get('metadata', {})
            )
            scenes.append(scene)

        logger.info(f"已加载 {len(scenes)} 个场景")
        return scenes


if __name__ == "__main__":
    # 测试代码
    import sys
    logging.basicConfig(level=logging.INFO)

    if len(sys.argv) < 2:
        print("使用方法: python scene_detector.py <video_path> [method]")
        print("  method: frame_diff, histogram, motion, hybrid (default)")
        sys.exit(1)

    video_path = sys.argv[1]
    method = sys.argv[2] if len(sys.argv) > 2 else "hybrid"

    detector = SceneDetector(method=method)
    scenes = detector.detect_scenes(video_path, debug=True)

    print(f"\n检测到 {len(scenes)} 个场景:")
    for i, scene in enumerate(scenes):
        print(f"\n场景 {i+1}:")
        print(f"  时间: {scene.start_time:.2f}s - {scene.end_time:.2f}s (时长: {scene.duration:.2f}s)")
        print(f"  类型: {scene.scene_type.value}")
        print(f"  置信度: {scene.confidence:.2%}")
        print(f"  运动强度: {scene.motion_level:.2f}")
        print(f"  颜色变化: {scene.color_change:.2f}")
