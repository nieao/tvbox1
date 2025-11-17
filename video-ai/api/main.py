"""
Video-AI API 主文件

个性化智能视频编辑 RESTful API
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import (
    FastAPI,
    File,
    UploadFile,
    BackgroundTasks,
    HTTPException,
    Depends,
    Query,
    status,
)
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
import uvicorn

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from .config import settings
from .models import *
from .services import video_service, user_service, recommendation_service
from .auth import (
    authenticate_user,
    create_access_token,
    get_current_user,
    get_optional_user,
)
from .utils import (
    generate_job_id,
    save_uploaded_file,
    get_video_filepath,
    cleanup_old_files,
)
from .middleware import (
    limiter,
    rate_limit_exceeded_handler,
    RequestLoggingMiddleware,
    ErrorHandlingMiddleware,
    RequestIDMiddleware,
)


# ========== 创建 FastAPI 应用 ==========

app = FastAPI(
    title=settings.APP_NAME,
    description="个性化智能视频编辑 API - 基于 AI 的视频内容分析和智能剪辑服务",
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)


# ========== 配置中间件 ==========

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

# 自定义中间件
app.add_middleware(RequestIDMiddleware)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(ErrorHandlingMiddleware)

# 速率限制
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)


# ========== 根端点 ==========

@app.get("/", response_model=Dict[str, str])
async def root():
    """API 根端点"""
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """健康检查"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(),
        version=settings.APP_VERSION,
        services={
            "video_processing": True,
            "recommendation": True,
            "user_management": True,
        },
    )


# ========== 认证端点 ==========

@app.post(
    f"{settings.API_V1_PREFIX}/auth/login",
    response_model=LoginResponse,
    tags=["认证"],
)
@limiter.limit("10/minute")
async def login(request: Request, login_data: LoginRequest):
    """
    用户登录

    获取 JWT 访问令牌
    """
    user = authenticate_user(login_data.username, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 创建访问令牌
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )

    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user_id=user["username"],
    )


@app.get(f"{settings.API_V1_PREFIX}/auth/me", tags=["认证"])
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """获取当前用户信息"""
    return {
        "username": current_user["username"],
        "full_name": current_user["full_name"],
        "email": current_user["email"],
    }


# ========== 视频处理端点 ==========

@app.post(
    f"{settings.API_V1_PREFIX}/videos/process",
    response_model=VideoProcessResponse,
    tags=["视频处理"],
)
@limiter.limit("10/minute")
async def process_video(
    request: Request,
    background_tasks: BackgroundTasks,
    process_request: VideoProcessRequest,
    current_user: Optional[dict] = Depends(get_optional_user),
):
    """
    处理视频

    支持两种方式：
    1. 提供 YouTube URL
    2. 上传本地视频文件（使用 /videos/upload 端点）

    处理是异步的，使用 job_id 查询状态
    """
    if not process_request.video_url:
        raise HTTPException(
            status_code=400,
            detail="必须提供 video_url 或先上传文件",
        )

    # 生成任务 ID
    job_id = generate_job_id()

    # 创建任务
    video_service.job_manager.create_job(job_id)

    # 添加后台任务
    background_tasks.add_task(
        video_service.process_video,
        job_id,
        process_request,
        None,
    )

    return VideoProcessResponse(
        job_id=job_id,
        status=JobStatus.PENDING,
        message="视频处理已开始",
        estimated_time=300,  # 预估 5 分钟
    )


@app.post(
    f"{settings.API_V1_PREFIX}/videos/upload",
    response_model=FileInfo,
    tags=["视频处理"],
)
@limiter.limit("5/minute")
async def upload_video(
    request: Request,
    file: UploadFile = File(...),
    current_user: Optional[dict] = Depends(get_optional_user),
):
    """
    上传视频文件

    支持的格式：mp4, avi, mov, mkv, webm
    最大文件大小：500MB
    """
    try:
        filepath, video_id = await save_uploaded_file(file)

        return FileInfo(
            filename=file.filename,
            filepath=filepath,
            size=file.size,
            content_type=file.content_type,
            uploaded_at=datetime.now(),
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件上传失败: {str(e)}")


@app.post(
    f"{settings.API_V1_PREFIX}/videos/process-uploaded",
    response_model=VideoProcessResponse,
    tags=["视频处理"],
)
@limiter.limit("10/minute")
async def process_uploaded_video(
    request: Request,
    background_tasks: BackgroundTasks,
    filepath: str,
    process_request: VideoProcessRequest,
    current_user: Optional[dict] = Depends(get_optional_user),
):
    """
    处理已上传的视频

    先使用 /videos/upload 上传文件，然后使用此端点处理
    """
    if not Path(filepath).exists():
        raise HTTPException(status_code=404, detail="文件不存在")

    # 生成任务 ID
    job_id = generate_job_id()

    # 创建任务
    video_service.job_manager.create_job(job_id)

    # 添加后台任务
    background_tasks.add_task(
        video_service.process_video,
        job_id,
        process_request,
        filepath,
    )

    return VideoProcessResponse(
        job_id=job_id,
        status=JobStatus.PENDING,
        message="视频处理已开始",
        estimated_time=300,
    )


@app.get(
    f"{settings.API_V1_PREFIX}/jobs/{{job_id}}",
    response_model=JobStatusResponse,
    tags=["视频处理"],
)
async def get_job_status(
    job_id: str,
    current_user: Optional[dict] = Depends(get_optional_user),
):
    """
    获取处理任务状态

    返回任务的当前状态、进度和结果
    """
    job = video_service.job_manager.get_job(job_id)

    if not job:
        raise HTTPException(status_code=404, detail="任务不存在")

    return JobStatusResponse(**job)


@app.get(
    f"{settings.API_V1_PREFIX}/jobs",
    response_model=List[JobStatusResponse],
    tags=["视频处理"],
)
async def list_jobs(
    status_filter: Optional[JobStatus] = Query(None, alias="status"),
    current_user: dict = Depends(get_current_user),
):
    """
    列出所有任务

    可选择按状态过滤
    """
    jobs = video_service.job_manager.list_jobs(status=status_filter)
    return [JobStatusResponse(**job) for job in jobs]


@app.get(
    f"{settings.API_V1_PREFIX}/videos/{{video_id}}/download",
    tags=["视频处理"],
)
async def download_video(
    video_id: str,
    current_user: Optional[dict] = Depends(get_optional_user),
):
    """
    下载处理后的视频

    返回视频文件
    """
    filepath = get_video_filepath(video_id)

    if not filepath:
        raise HTTPException(status_code=404, detail="视频不存在")

    return FileResponse(
        filepath,
        media_type="video/mp4",
        filename=f"edited_{video_id}.mp4",
    )


# ========== 用户管理端点 ==========

@app.post(
    f"{settings.API_V1_PREFIX}/users",
    response_model=UserProfileResponse,
    tags=["用户管理"],
)
async def create_user(profile_request: UserProfileRequest):
    """
    创建用户画像

    初始化用户配置和偏好设置
    """
    try:
        profile = user_service.create_user(profile_request)
        return UserProfileResponse(**profile.to_dict())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get(
    f"{settings.API_V1_PREFIX}/users/{{user_id}}",
    response_model=UserProfileResponse,
    tags=["用户管理"],
)
async def get_user(user_id: str):
    """
    获取用户信息

    返回用户画像和偏好设置
    """
    profile = user_service.get_user(user_id)

    if not profile:
        raise HTTPException(status_code=404, detail="用户不存在")

    return UserProfileResponse(**profile.to_dict())


@app.put(
    f"{settings.API_V1_PREFIX}/users/{{user_id}}",
    response_model=UserProfileResponse,
    tags=["用户管理"],
)
async def update_user(user_id: str, profile_request: UserProfileRequest):
    """
    更新用户配置

    修改用户兴趣和偏好设置
    """
    try:
        profile = user_service.update_user(user_id, profile_request)
        return UserProfileResponse(**profile.to_dict())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ========== 推荐系统端点 ==========

@app.get(
    f"{settings.API_V1_PREFIX}/recommendations/{{user_id}}",
    response_model=RecommendationsResponse,
    tags=["推荐系统"],
)
async def get_recommendations(
    user_id: str,
    num: int = Query(10, ge=1, le=50, description="推荐数量"),
    seed_video_id: Optional[str] = Query(None, description="种子视频ID"),
):
    """
    获取个性化推荐

    基于用户画像和行为历史推荐视频
    """
    try:
        recommendations = recommendation_service.get_recommendations(
            user_id=user_id,
            num=num,
            seed_video_id=seed_video_id,
        )

        return RecommendationsResponse(
            user_id=user_id,
            recommendations=[
                RecommendationItem(
                    video_id=rec.video_id,
                    score=rec.score,
                    reason=rec.reason,
                    cf_score=rec.cf_score,
                    cb_score=rec.cb_score,
                    popularity_score=rec.popularity_score,
                )
                for rec in recommendations
            ],
            total=len(recommendations),
            generated_at=datetime.now(),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post(
    f"{settings.API_V1_PREFIX}/feedback",
    tags=["推荐系统"],
)
async def submit_feedback(feedback: FeedbackRequest):
    """
    提交用户反馈

    记录用户对视频的行为（点赞、跳过等）
    """
    try:
        user_service.submit_feedback(feedback)

        # 如果有评分，添加到推荐系统
        if feedback.rating is not None:
            recommendation_service.add_interaction(
                feedback.user_id,
                feedback.video_id,
                feedback.rating,
            )

        return {"status": "success", "message": "反馈已记录"}

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========== 统计和分析端点 ==========

@app.get(
    f"{settings.API_V1_PREFIX}/stats/trending",
    response_model=TrendingResponse,
    tags=["统计分析"],
)
async def get_trending(
    period: str = Query("today", regex="^(today|week|month)$"),
):
    """
    获取热门内容

    返回指定时间段内的热门视频
    """
    # TODO: 实现真实的热门内容统计
    return TrendingResponse(
        videos=[
            {
                "video_id": f"video_{i}",
                "title": f"热门视频 {i}",
                "views": 10000 - i * 100,
                "likes": 500 - i * 10,
            }
            for i in range(1, 11)
        ],
        period=period,
        generated_at=datetime.now(),
    )


@app.get(
    f"{settings.API_V1_PREFIX}/stats/analytics",
    response_model=AnalyticsResponse,
    tags=["统计分析"],
    dependencies=[Depends(get_current_user)],
)
async def get_analytics():
    """
    获取系统分析数据

    需要认证。返回系统的整体统计信息
    """
    jobs = video_service.job_manager.list_jobs()
    active_jobs = video_service.job_manager.list_jobs(status=JobStatus.PROCESSING)

    # 计算平均处理时间
    completed_jobs = [job for job in jobs if job["status"] == JobStatus.COMPLETED]
    avg_processing_time = 0
    if completed_jobs:
        processing_times = [
            (job["updated_at"] - job["created_at"]).total_seconds()
            for job in completed_jobs
        ]
        avg_processing_time = sum(processing_times) / len(processing_times)

    # 计算平均压缩率
    avg_compression_ratio = 0
    if completed_jobs:
        compression_ratios = [
            job.get("result", {}).get("compression_ratio", 0)
            for job in completed_jobs
            if job.get("result")
        ]
        if compression_ratios:
            avg_compression_ratio = sum(compression_ratios) / len(compression_ratios)

    return AnalyticsResponse(
        total_users=len(user_service.users),
        total_videos=len(completed_jobs),
        total_jobs=len(jobs),
        active_jobs=len(active_jobs),
        avg_processing_time=avg_processing_time,
        avg_compression_ratio=avg_compression_ratio,
        popular_interests=[],
        system_health="healthy",
    )


# ========== 管理端点 ==========

@app.post(
    f"{settings.API_V1_PREFIX}/admin/cleanup",
    tags=["管理"],
    dependencies=[Depends(get_current_user)],
)
async def cleanup_files(days: int = Query(7, ge=1, le=30)):
    """
    清理旧文件

    删除指定天数之前的文件。需要认证
    """
    try:
        cleanup_old_files(days=days)
        return {"status": "success", "message": f"已清理 {days} 天前的文件"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========== 错误处理 ==========

@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    """404 错误处理"""
    return JSONResponse(
        status_code=404,
        content=ErrorResponse(
            error="NotFound",
            message="资源不存在",
            timestamp=datetime.now(),
        ).dict(),
    )


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc: Exception):
    """500 错误处理"""
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="InternalServerError",
            message="服务器内部错误",
            details={"exception": str(exc)} if settings.DEBUG else None,
            timestamp=datetime.now(),
        ).dict(),
    )


# ========== 启动事件 ==========

@app.on_event("startup")
async def startup_event():
    """启动事件"""
    print(f"{'='*60}")
    print(f"{settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"{'='*60}")
    print(f"API 文档: http://{settings.HOST}:{settings.PORT}/docs")
    print(f"ReDoc: http://{settings.HOST}:{settings.PORT}/redoc")
    print(f"{'='*60}")


@app.on_event("shutdown")
async def shutdown_event():
    """关闭事件"""
    print("API 服务器正在关闭...")


# ========== 主函数 ==========

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        workers=1 if settings.DEBUG else settings.WORKERS,
    )
