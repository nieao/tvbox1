"""
API 数据模型

使用 Pydantic 定义请求和响应模型
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime


# ========== 枚举类型 ==========

class OutputLength(str, Enum):
    """输出长度"""
    SHORT = "short"
    MEDIUM = "medium"
    LONG = "long"


class TransitionStyle(str, Enum):
    """过渡效果风格"""
    TEXT = "text"
    FADE = "fade"
    BLUR = "blur"
    ZOOM = "zoom"
    GRADIENT = "gradient"
    NONE = "none"


class TransitionTemplate(str, Enum):
    """文字过渡模板"""
    MINIMAL = "minimal"
    MODERN = "modern"
    CLASSIC = "classic"
    COLORFUL = "colorful"
    INFO_CARD = "info_card"


class VideoQuality(str, Enum):
    """视频质量"""
    QUALITY_480P = "480p"
    QUALITY_720P = "720p"
    QUALITY_1080P = "1080p"
    BEST = "best"


class JobStatus(str, Enum):
    """任务状态"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class FeedbackAction(str, Enum):
    """反馈动作"""
    LIKE = "like"
    DISLIKE = "dislike"
    SKIP = "skip"
    SAVE = "save"
    SHARE = "share"


# ========== 请求模型 ==========

class VideoProcessRequest(BaseModel):
    """视频处理请求"""
    video_url: Optional[str] = Field(None, description="YouTube 视频 URL（与文件上传二选一）")
    user_interests: List[str] = Field(default_factory=list, description="用户兴趣列表")
    output_length: OutputLength = Field(OutputLength.MEDIUM, description="输出长度")
    transition_style: TransitionStyle = Field(TransitionStyle.TEXT, description="过渡效果风格")
    transition_template: TransitionTemplate = Field(TransitionTemplate.MODERN, description="文字过渡模板")
    quality: VideoQuality = Field(VideoQuality.QUALITY_720P, description="YouTube 视频下载质量")
    use_transcript: bool = Field(True, description="是否使用 YouTube 字幕")
    max_segments: int = Field(10, ge=1, le=50, description="最大片段数")

    @validator("video_url")
    def validate_youtube_url(cls, v):
        if v and not any(domain in v for domain in ["youtube.com", "youtu.be"]):
            raise ValueError("必须是有效的 YouTube URL")
        return v


class UserProfileRequest(BaseModel):
    """用户配置请求"""
    user_id: str = Field(..., description="用户ID", min_length=1)
    interests: List[str] = Field(default_factory=list, description="兴趣列表")
    skip_topics: List[str] = Field(default_factory=list, description="跳过的主题")
    preferred_duration: OutputLength = Field(OutputLength.MEDIUM, description="偏好视频长度")
    language: str = Field("zh-CN", description="语言设置")
    age_range: Optional[str] = Field(None, description="年龄段")
    location: Optional[str] = Field(None, description="位置")


class FeedbackRequest(BaseModel):
    """反馈请求"""
    user_id: str = Field(..., description="用户ID")
    video_id: str = Field(..., description="视频ID")
    action: FeedbackAction = Field(..., description="反馈动作")
    rating: Optional[float] = Field(None, ge=0, le=1, description="评分（0-1）")
    watch_time: Optional[float] = Field(None, ge=0, description="观看时长（秒）")
    watch_percentage: Optional[float] = Field(None, ge=0, le=1, description="观看比例（0-1）")
    comment: Optional[str] = Field(None, description="评论")


class LoginRequest(BaseModel):
    """登录请求"""
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


# ========== 响应模型 ==========

class VideoProcessResponse(BaseModel):
    """视频处理响应"""
    job_id: str = Field(..., description="任务ID")
    status: JobStatus = Field(..., description="任务状态")
    message: str = Field(..., description="消息")
    estimated_time: Optional[int] = Field(None, description="预估处理时间（秒）")


class JobStatusResponse(BaseModel):
    """任务状态响应"""
    job_id: str
    status: JobStatus
    progress: float = Field(..., ge=0, le=1, description="进度（0-1）")
    message: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class EditingResultResponse(BaseModel):
    """剪辑结果响应"""
    video_id: str
    output_path: str
    original_duration: float = Field(..., description="原始时长（秒）")
    edited_duration: float = Field(..., description="剪辑后时长（秒）")
    compression_ratio: float = Field(..., description="压缩比例")
    density_improvement: float = Field(..., description="信息密度提升百分比")
    segments_count: int = Field(..., description="片段数量")
    used_strategy: str = Field(..., description="使用的策略")
    download_url: str = Field(..., description="下载链接")


class SegmentInfo(BaseModel):
    """片段信息"""
    start: float
    end: float
    topic: str
    text: str
    relevance: float


class VideoPreviewResponse(BaseModel):
    """视频预览响应"""
    original_duration: float
    estimated_duration: float
    compression_ratio: float
    main_topics: List[str]
    summary: str
    key_segments: List[SegmentInfo]


class UserProfileResponse(BaseModel):
    """用户配置响应"""
    user_id: str
    interests: Dict[str, Any]
    category_interests: Dict[str, float]
    preferences: Dict[str, Any]
    engagement_score: float
    loyalty_score: float
    activity_level: str
    last_active: Optional[datetime]


class RecommendationItem(BaseModel):
    """推荐项目"""
    video_id: str
    score: float = Field(..., ge=0, le=1)
    reason: str
    cf_score: float = Field(0.0, description="协同过滤评分")
    cb_score: float = Field(0.0, description="内容推荐评分")
    popularity_score: float = Field(0.0, description="热度评分")
    thumbnail_url: Optional[str] = None
    title: Optional[str] = None
    duration: Optional[float] = None


class RecommendationsResponse(BaseModel):
    """推荐响应"""
    user_id: str
    recommendations: List[RecommendationItem]
    total: int
    generated_at: datetime


class TrendingResponse(BaseModel):
    """热门内容响应"""
    videos: List[Dict[str, Any]]
    period: str = Field(..., description="时间段（today, week, month）")
    generated_at: datetime


class AnalyticsResponse(BaseModel):
    """系统分析响应"""
    total_users: int
    total_videos: int
    total_jobs: int
    active_jobs: int
    avg_processing_time: float
    avg_compression_ratio: float
    popular_interests: List[tuple]
    system_health: str


class LoginResponse(BaseModel):
    """登录响应"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int = Field(..., description="过期时间（秒）")
    user_id: str


class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str = Field(..., description="健康状态")
    timestamp: datetime
    version: str
    services: Dict[str, bool] = Field(..., description="各服务状态")


class ErrorResponse(BaseModel):
    """错误响应"""
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime


# ========== 其他模型 ==========

class PaginationParams(BaseModel):
    """分页参数"""
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(10, ge=1, le=100, description="每页大小")


class FileInfo(BaseModel):
    """文件信息"""
    filename: str
    filepath: str
    size: int
    content_type: str
    uploaded_at: datetime
