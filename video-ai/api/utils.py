"""
API 工具函数
"""

import os
import uuid
import hashlib
from typing import Optional
from datetime import datetime, timedelta
from pathlib import Path

from fastapi import UploadFile
from .config import settings


def generate_job_id() -> str:
    """生成任务ID"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_str = uuid.uuid4().hex[:8]
    return f"job_{timestamp}_{random_str}"


def generate_video_id(filename: str) -> str:
    """生成视频ID"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    file_hash = hashlib.md5(filename.encode()).hexdigest()[:8]
    return f"video_{timestamp}_{file_hash}"


async def save_uploaded_file(file: UploadFile) -> tuple[str, str]:
    """
    保存上传的文件

    Args:
        file: 上传的文件

    Returns:
        (文件路径, 视频ID)
    """
    # 验证文件扩展名
    file_extension = Path(file.filename).suffix.lower()
    if file_extension not in settings.ALLOWED_VIDEO_EXTENSIONS:
        raise ValueError(f"不支持的文件格式: {file_extension}")

    # 生成唯一文件名
    video_id = generate_video_id(file.filename)
    filename = f"{video_id}{file_extension}"
    filepath = settings.UPLOAD_DIR / filename

    # 保存文件
    content = await file.read()

    # 检查文件大小
    if len(content) > settings.MAX_UPLOAD_SIZE:
        raise ValueError(f"文件太大，最大允许 {settings.MAX_UPLOAD_SIZE / 1024 / 1024:.0f}MB")

    with open(filepath, "wb") as f:
        f.write(content)

    return str(filepath), video_id


def get_video_filepath(video_id: str) -> Optional[str]:
    """
    获取视频文件路径

    Args:
        video_id: 视频ID

    Returns:
        文件路径或 None
    """
    # 在输出目录中查找
    for ext in settings.ALLOWED_VIDEO_EXTENSIONS:
        filepath = settings.OUTPUT_DIR / f"edited_{video_id}{ext}"
        if filepath.exists():
            return str(filepath)

    return None


def cleanup_old_files(days: int = None):
    """
    清理旧文件

    Args:
        days: 清理多少天前的文件
    """
    if days is None:
        days = settings.CLEANUP_AFTER_DAYS

    cutoff_time = datetime.now() - timedelta(days=days)

    # 清理上传目录
    for filepath in settings.UPLOAD_DIR.iterdir():
        if filepath.is_file():
            file_time = datetime.fromtimestamp(filepath.stat().st_mtime)
            if file_time < cutoff_time:
                filepath.unlink()
                print(f"清理文件: {filepath}")

    # 清理输出目录
    for filepath in settings.OUTPUT_DIR.iterdir():
        if filepath.is_file():
            file_time = datetime.fromtimestamp(filepath.stat().st_mtime)
            if file_time < cutoff_time:
                filepath.unlink()
                print(f"清理文件: {filepath}")


def format_duration(seconds: float) -> str:
    """
    格式化时长

    Args:
        seconds: 秒数

    Returns:
        格式化的时长字符串
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)

    if hours > 0:
        return f"{hours}h {minutes}m {secs}s"
    elif minutes > 0:
        return f"{minutes}m {secs}s"
    else:
        return f"{secs}s"


def calculate_file_hash(filepath: str) -> str:
    """
    计算文件的 MD5 哈希

    Args:
        filepath: 文件路径

    Returns:
        MD5 哈希值
    """
    hash_md5 = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def get_file_size(filepath: str) -> int:
    """
    获取文件大小

    Args:
        filepath: 文件路径

    Returns:
        文件大小（字节）
    """
    return os.path.getsize(filepath)


def format_file_size(size_bytes: int) -> str:
    """
    格式化文件大小

    Args:
        size_bytes: 字节数

    Returns:
        格式化的文件大小字符串
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"
