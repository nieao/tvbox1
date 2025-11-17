"""
API 业务服务层

处理核心业务逻辑
"""

import sys
import os
from pathlib import Path
from typing import Dict, Optional, Any
from datetime import datetime
import asyncio
from concurrent.futures import ThreadPoolExecutor
import json

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.editor import VideoEditor, EditingResult
from src.services.recommendation import HybridRecommender
from src.models.user_profile import UserProfile
from src.services.personalization import PersonalizationConfig
from src.services.feedback_learning import FeedbackLearningSystem

from .config import settings
from .models import (
    JobStatus,
    VideoProcessRequest,
    UserProfileRequest,
    FeedbackRequest,
)


class JobManager:
    """任务管理器"""

    def __init__(self):
        self.jobs: Dict[str, Dict[str, Any]] = {}
        self.executor = ThreadPoolExecutor(max_workers=settings.MAX_CONCURRENT_JOBS)

    def create_job(self, job_id: str) -> Dict[str, Any]:
        """创建任务"""
        job = {
            "job_id": job_id,
            "status": JobStatus.PENDING,
            "progress": 0.0,
            "message": "任务已创建",
            "result": None,
            "error": None,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }
        self.jobs[job_id] = job
        return job

    def update_job(
        self,
        job_id: str,
        status: Optional[JobStatus] = None,
        progress: Optional[float] = None,
        message: Optional[str] = None,
        result: Optional[Dict] = None,
        error: Optional[str] = None,
    ):
        """更新任务状态"""
        if job_id not in self.jobs:
            raise ValueError(f"任务不存在: {job_id}")

        job = self.jobs[job_id]

        if status is not None:
            job["status"] = status
        if progress is not None:
            job["progress"] = progress
        if message is not None:
            job["message"] = message
        if result is not None:
            job["result"] = result
        if error is not None:
            job["error"] = error

        job["updated_at"] = datetime.now()

    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """获取任务状态"""
        return self.jobs.get(job_id)

    def list_jobs(self, status: Optional[JobStatus] = None) -> list:
        """列出所有任务"""
        if status:
            return [job for job in self.jobs.values() if job["status"] == status]
        return list(self.jobs.values())


class VideoProcessingService:
    """视频处理服务"""

    def __init__(self):
        self.job_manager = JobManager()

    async def process_video(
        self,
        job_id: str,
        request: VideoProcessRequest,
        input_path: Optional[str] = None,
    ):
        """
        处理视频（异步）

        Args:
            job_id: 任务ID
            request: 处理请求
            input_path: 输入文件路径（上传文件）
        """
        try:
            # 更新任务状态
            self.job_manager.update_job(
                job_id,
                status=JobStatus.PROCESSING,
                progress=0.1,
                message="开始处理视频...",
            )

            # 创建个性化配置
            config = PersonalizationConfig(
                interests=request.user_interests,
                output_length=request.output_length.value,
                transition_style=request.transition_style.value,
            )

            # 创建视频编辑器
            editor = VideoEditor(
                config=config,
                transition_style=request.transition_style.value,
                transition_template=request.transition_template.value,
            )

            # 生成输出路径
            video_id = job_id.replace("job_", "video_")
            output_path = settings.OUTPUT_DIR / f"edited_{video_id}.mp4"

            # 在线程池中执行处理
            loop = asyncio.get_event_loop()

            def process_sync():
                try:
                    if request.video_url:
                        # 处理 YouTube 视频
                        result = editor.process_youtube_video(
                            request.video_url,
                            str(output_path),
                            quality=request.quality.value,
                            use_transcript=request.use_transcript,
                            max_segments=request.max_segments,
                        )
                    elif input_path:
                        # 处理上传的视频
                        result = editor.process_video(
                            input_path,
                            str(output_path),
                            max_segments=request.max_segments,
                        )
                    else:
                        raise ValueError("必须提供 video_url 或上传文件")

                    return result
                except Exception as e:
                    raise e

            # 执行处理
            result: EditingResult = await loop.run_in_executor(
                self.job_manager.executor, process_sync
            )

            # 构建结果
            result_dict = {
                "video_id": result.video_id,
                "output_path": str(output_path),
                "original_duration": result.original_duration,
                "edited_duration": result.edited_duration,
                "compression_ratio": result.compression_ratio,
                "density_improvement": result.density_improvement,
                "segments_count": result.segments_count,
                "used_strategy": result.used_strategy,
                "download_url": f"/api/v1/videos/{result.video_id}/download",
            }

            # 更新任务状态为完成
            self.job_manager.update_job(
                job_id,
                status=JobStatus.COMPLETED,
                progress=1.0,
                message="处理完成",
                result=result_dict,
            )

        except Exception as e:
            # 更新任务状态为失败
            self.job_manager.update_job(
                job_id,
                status=JobStatus.FAILED,
                progress=0.0,
                message="处理失败",
                error=str(e),
            )
            print(f"视频处理失败: {e}")


class UserService:
    """用户服务"""

    def __init__(self):
        self.users: Dict[str, UserProfile] = {}
        self.profiles_dir = Path(settings.OUTPUT_DIR) / "profiles"
        self.profiles_dir.mkdir(parents=True, exist_ok=True)

    def create_user(self, request: UserProfileRequest) -> UserProfile:
        """创建用户画像"""
        profile = UserProfile(
            user_id=request.user_id,
            age_range=request.age_range,
            location=request.location,
            language=request.language,
        )

        # 设置偏好
        profile.preferences["preferred_duration"] = request.preferred_duration.value
        profile.preferences["skip_topics"] = request.skip_topics

        # 初始化兴趣
        for interest in request.interests:
            from src.models.user_profile import UserInterest

            profile.interests[interest] = UserInterest(
                topic=interest,
                weight=0.5,
                confidence=0.5,
                last_updated=datetime.now().isoformat(),
            )

        # 保存
        self.users[request.user_id] = profile
        self._save_profile(profile)

        return profile

    def get_user(self, user_id: str) -> Optional[UserProfile]:
        """获取用户画像"""
        if user_id in self.users:
            return self.users[user_id]

        # 尝试从磁盘加载
        filepath = self.profiles_dir / f"{user_id}.json"
        if filepath.exists():
            profile = UserProfile.load(str(filepath))
            self.users[user_id] = profile
            return profile

        return None

    def update_user(self, user_id: str, request: UserProfileRequest) -> UserProfile:
        """更新用户画像"""
        profile = self.get_user(user_id)
        if not profile:
            # 如果不存在，创建新的
            return self.create_user(request)

        # 更新兴趣
        for interest in request.interests:
            if interest not in profile.interests:
                from src.models.user_profile import UserInterest

                profile.interests[interest] = UserInterest(
                    topic=interest,
                    weight=0.5,
                    confidence=0.5,
                    last_updated=datetime.now().isoformat(),
                )

        # 更新偏好
        profile.preferences["preferred_duration"] = request.preferred_duration.value
        profile.preferences["skip_topics"] = request.skip_topics

        # 保存
        self._save_profile(profile)
        return profile

    def submit_feedback(self, request: FeedbackRequest):
        """提交用户反馈"""
        profile = self.get_user(request.user_id)
        if not profile:
            raise ValueError(f"用户不存在: {request.user_id}")

        # 添加反馈事件
        profile.add_feedback_event(request.video_id, request.action.value)

        # 如果有观看数据，添加观看事件
        if request.watch_time is not None and request.watch_percentage is not None:
            profile.add_watch_event(
                video_id=request.video_id,
                category="unknown",  # TODO: 获取视频分类
                tags=[],  # TODO: 获取视频标签
                watch_time=request.watch_time,
                watch_percentage=request.watch_percentage,
            )

        # 更新指标
        profile.calculate_engagement_score()
        profile.calculate_loyalty_score()
        profile.update_activity_level()

        # 保存
        self._save_profile(profile)

    def _save_profile(self, profile: UserProfile):
        """保存用户画像"""
        filepath = self.profiles_dir / f"{profile.user_id}.json"
        profile.save(str(filepath))


class RecommendationService:
    """推荐服务"""

    def __init__(self):
        self.recommender = HybridRecommender()
        self._load_sample_data()

    def _load_sample_data(self):
        """加载示例数据（用于演示）"""
        # 添加一些示例视频
        video_ids = [f"video_{i}" for i in range(1, 21)]

        for video_id in video_ids:
            # 添加视频特征
            self.recommender.add_video_features(
                video_id,
                {
                    "tech": 0.8 if int(video_id.split("_")[1]) % 3 == 0 else 0.2,
                    "ai": 0.7 if int(video_id.split("_")[1]) % 2 == 0 else 0.3,
                    "education": 0.6
                    if int(video_id.split("_")[1]) % 5 == 0
                    else 0.4,
                },
            )

            # 添加视频统计
            self.recommender.add_video_stats(
                video_id,
                views=10000 + int(video_id.split("_")[1]) * 1000,
                likes=500 + int(video_id.split("_")[1]) * 50,
                shares=100 + int(video_id.split("_")[1]) * 10,
                comments=50 + int(video_id.split("_")[1]) * 5,
            )

    def get_recommendations(
        self, user_id: str, num: int = 10, seed_video_id: Optional[str] = None
    ):
        """获取个性化推荐"""
        recommendations = self.recommender.recommend(
            user_id=user_id, k=num, seed_video_id=seed_video_id
        )

        return recommendations

    def add_interaction(self, user_id: str, video_id: str, rating: float):
        """添加用户交互"""
        self.recommender.add_video_interaction(user_id, video_id, rating)


# 创建全局服务实例
video_service = VideoProcessingService()
user_service = UserService()
recommendation_service = RecommendationService()
