"""
API 配置文件
"""

import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置"""

    # 基础配置
    APP_NAME: str = "Video-AI API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # API 配置
    API_V1_PREFIX: str = "/api/v1"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 4

    # 安全配置
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS 配置
    CORS_ORIGINS: list = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list = ["*"]
    CORS_ALLOW_HEADERS: list = ["*"]

    # 速率限制
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000

    # 文件上传配置
    UPLOAD_DIR: Path = Path("/tmp/video-ai/uploads")
    OUTPUT_DIR: Path = Path("/tmp/video-ai/outputs")
    MAX_UPLOAD_SIZE: int = 500 * 1024 * 1024  # 500MB
    ALLOWED_VIDEO_EXTENSIONS: set = {".mp4", ".avi", ".mov", ".mkv", ".webm"}

    # 处理配置
    MAX_CONCURRENT_JOBS: int = 5
    JOB_TIMEOUT: int = 3600  # 1小时
    CLEANUP_AFTER_DAYS: int = 7

    # 数据库配置（可选，用于持久化）
    DATABASE_URL: Optional[str] = None

    # Redis 配置（可选，用于任务队列）
    REDIS_URL: Optional[str] = None

    # 视频处理配置
    DEFAULT_OUTPUT_LENGTH: str = "medium"
    DEFAULT_TRANSITION_STYLE: str = "text"
    DEFAULT_TRANSITION_TEMPLATE: str = "modern"
    DEFAULT_VIDEO_QUALITY: str = "720p"

    # LLM 配置
    LLM_PROVIDER: str = "openai"
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_API_BASE: Optional[str] = None

    # Whisper 配置
    WHISPER_MODEL: str = "base"
    WHISPER_DEVICE: str = "cpu"

    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FILE: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = True


# 创建全局配置实例
settings = Settings()


# 确保必要的目录存在
def initialize_directories():
    """初始化必要的目录"""
    settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    settings.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# 在模块加载时初始化
initialize_directories()
