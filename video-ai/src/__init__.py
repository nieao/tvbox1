"""
Video-AI: 个性化智能视频编辑系统

一个革命性的AI视频编辑产品，根据用户喜好智能剪辑视频，
使用AI技术补充画面内容来衔接不连贯的信息。
"""

__version__ = "0.1.0"
__author__ = "Video-AI Team"

from .core.editor import VideoEditor
from .core.transcriber import VideoTranscriber
from .core.analyzer import ContentAnalyzer
from .services.personalization import PersonalizationConfig

__all__ = [
    "VideoEditor",
    "VideoTranscriber",
    "ContentAnalyzer",
    "PersonalizationConfig",
]
