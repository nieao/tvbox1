"""
Video-AI API 模块

RESTful API for Video-AI project
"""

from .main import app
from .config import settings

__version__ = "1.0.0"
__all__ = ["app", "settings"]
