"""
Video-AI API 客户端示例

演示如何使用 Python 调用 Video-AI API
"""

import requests
import time
from typing import Optional


class VideoAIClient:
    """Video-AI API 客户端"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api/v1"
        self.token: Optional[str] = None

    def login(self, username: str, password: str) -> str:
        """
        用户登录

        Args:
            username: 用户名
            password: 密码

        Returns:
            访问令牌
        """
        response = requests.post(
            f"{self.api_url}/auth/login",
            json={"username": username, "password": password}
        )
        response.raise_for_status()

        data = response.json()
        self.token = data["access_token"]
        print(f"✅ 登录成功！用户: {username}")

        return self.token

    def _get_headers(self):
        """获取请求头"""
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def create_user(self, user_id: str, interests: list, **kwargs) -> dict:
        """
        创建用户画像

        Args:
            user_id: 用户ID
            interests: 兴趣列表
            **kwargs: 其他参数

        Returns:
            用户信息
        """
        data = {
            "user_id": user_id,
            "interests": interests,
            **kwargs
        }

        response = requests.post(
            f"{self.api_url}/users",
            json=data,
            headers=self._get_headers()
        )
        response.raise_for_status()

        print(f"✅ 用户创建成功！用户ID: {user_id}")
        return response.json()

    def process_video(
        self,
        video_url: str,
        user_interests: list = None,
        output_length: str = "medium",
        **kwargs
    ) -> str:
        """
        处理 YouTube 视频

        Args:
            video_url: YouTube 视频 URL
            user_interests: 用户兴趣
            output_length: 输出长度
            **kwargs: 其他参数

        Returns:
            任务ID
        """
        data = {
            "video_url": video_url,
            "user_interests": user_interests or [],
            "output_length": output_length,
            **kwargs
        }

        response = requests.post(
            f"{self.api_url}/videos/process",
            json=data,
            headers=self._get_headers()
        )
        response.raise_for_status()

        job_id = response.json()["job_id"]
        print(f"✅ 视频处理已开始！任务ID: {job_id}")

        return job_id

    def get_job_status(self, job_id: str) -> dict:
        """
        查询任务状态

        Args:
            job_id: 任务ID

        Returns:
            任务状态信息
        """
        response = requests.get(
            f"{self.api_url}/jobs/{job_id}",
            headers=self._get_headers()
        )
        response.raise_for_status()

        return response.json()

    def wait_for_job(self, job_id: str, interval: int = 5) -> dict:
        """
        等待任务完成

        Args:
            job_id: 任务ID
            interval: 查询间隔（秒）

        Returns:
            任务结果
        """
        print(f"⏳ 等待任务完成...")

        while True:
            job = self.get_job_status(job_id)
            status = job["status"]
            progress = job["progress"]

            print(f"   进度: {progress*100:.1f}% - {job.get('message', '')}")

            if status == "completed":
                print("✅ 任务完成！")
                return job["result"]
            elif status == "failed":
                error = job.get("error", "未知错误")
                print(f"❌ 任务失败: {error}")
                raise Exception(error)

            time.sleep(interval)

    def download_video(self, video_id: str, output_path: str):
        """
        下载处理后的视频

        Args:
            video_id: 视频ID
            output_path: 输出路径
        """
        response = requests.get(
            f"{self.api_url}/videos/{video_id}/download",
            headers=self._get_headers(),
            stream=True
        )
        response.raise_for_status()

        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        print(f"✅ 视频下载成功！保存至: {output_path}")

    def get_recommendations(self, user_id: str, num: int = 10) -> list:
        """
        获取个性化推荐

        Args:
            user_id: 用户ID
            num: 推荐数量

        Returns:
            推荐列表
        """
        response = requests.get(
            f"{self.api_url}/recommendations/{user_id}",
            params={"num": num},
            headers=self._get_headers()
        )
        response.raise_for_status()

        data = response.json()
        print(f"✅ 获取到 {len(data['recommendations'])} 条推荐")

        return data["recommendations"]

    def submit_feedback(
        self,
        user_id: str,
        video_id: str,
        action: str,
        **kwargs
    ):
        """
        提交用户反馈

        Args:
            user_id: 用户ID
            video_id: 视频ID
            action: 动作（like, dislike, skip, save, share）
            **kwargs: 其他参数
        """
        data = {
            "user_id": user_id,
            "video_id": video_id,
            "action": action,
            **kwargs
        }

        response = requests.post(
            f"{self.api_url}/feedback",
            json=data,
            headers=self._get_headers()
        )
        response.raise_for_status()

        print(f"✅ 反馈已提交！动作: {action}")


def main():
    """主函数 - 演示完整流程"""

    print("=" * 60)
    print("Video-AI API 客户端示例")
    print("=" * 60)

    # 创建客户端
    client = VideoAIClient("http://localhost:8000")

    # 1. 登录
    print("\n[1] 登录...")
    client.login("demo", "demo123")

    # 2. 创建用户
    print("\n[2] 创建用户...")
    user_id = "demo_user_123"
    client.create_user(
        user_id=user_id,
        interests=["tech", "ai", "programming"],
        preferred_duration="medium"
    )

    # 3. 处理视频
    print("\n[3] 处理视频...")
    job_id = client.process_video(
        video_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        user_interests=["tech", "ai"],
        output_length="short",
        transition_style="text"
    )

    # 4. 等待任务完成
    print("\n[4] 等待处理完成...")
    result = client.wait_for_job(job_id)

    print("\n📊 处理结果:")
    print(f"   原始时长: {result['original_duration']:.1f}秒")
    print(f"   剪辑后时长: {result['edited_duration']:.1f}秒")
    print(f"   压缩率: {result['compression_ratio']:.1%}")
    print(f"   信息密度提升: {result['density_improvement']:.1%}")
    print(f"   片段数量: {result['segments_count']}")

    # 5. 下载视频
    print("\n[5] 下载视频...")
    video_id = result["video_id"]
    client.download_video(video_id, f"edited_{video_id}.mp4")

    # 6. 提交反馈
    print("\n[6] 提交反馈...")
    client.submit_feedback(
        user_id=user_id,
        video_id=video_id,
        action="like",
        rating=0.9
    )

    # 7. 获取推荐
    print("\n[7] 获取推荐...")
    recommendations = client.get_recommendations(user_id, num=5)

    print("\n📝 推荐视频:")
    for i, rec in enumerate(recommendations, 1):
        print(f"   {i}. {rec['video_id']} (分数: {rec['score']:.3f})")
        print(f"      原因: {rec['reason']}")

    print("\n" + "=" * 60)
    print("✅ 演示完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
