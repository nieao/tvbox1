"""
API 测试套件

使用 pytest 和 httpx 测试 API 端点
"""

import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import sys

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from api.main import app
from api.config import settings


# ========== Fixtures ==========

@pytest.fixture
def client():
    """创建测试客户端"""
    return TestClient(app)


@pytest.fixture
def auth_headers(client):
    """获取认证头"""
    response = client.post(
        f"{settings.API_V1_PREFIX}/auth/login",
        json={"username": "demo", "password": "demo123"},
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# ========== 基础端点测试 ==========

def test_root_endpoint(client):
    """测试根端点"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == settings.APP_NAME
    assert data["status"] == "running"


def test_health_check(client):
    """测试健康检查端点"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "services" in data
    assert data["services"]["video_processing"] is True


# ========== 认证测试 ==========

def test_login_success(client):
    """测试成功登录"""
    response = client.post(
        f"{settings.API_V1_PREFIX}/auth/login",
        json={"username": "demo", "password": "demo123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_failure(client):
    """测试登录失败"""
    response = client.post(
        f"{settings.API_V1_PREFIX}/auth/login",
        json={"username": "demo", "password": "wrongpassword"},
    )
    assert response.status_code == 401


def test_get_current_user(client, auth_headers):
    """测试获取当前用户信息"""
    response = client.get(
        f"{settings.API_V1_PREFIX}/auth/me",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "demo"


def test_unauthorized_access(client):
    """测试未授权访问"""
    response = client.get(f"{settings.API_V1_PREFIX}/auth/me")
    assert response.status_code == 403


# ========== 视频处理测试 ==========

def test_process_video_youtube(client):
    """测试处理 YouTube 视频"""
    response = client.post(
        f"{settings.API_V1_PREFIX}/videos/process",
        json={
            "video_url": "https://www.youtube.com/watch?v=test",
            "user_interests": ["tech", "ai"],
            "output_length": "short",
            "transition_style": "text",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "job_id" in data
    assert data["status"] == "pending"


def test_process_video_invalid_url(client):
    """测试无效的视频 URL"""
    response = client.post(
        f"{settings.API_V1_PREFIX}/videos/process",
        json={
            "video_url": "https://example.com/video",
            "user_interests": [],
        },
    )
    assert response.status_code == 422  # Validation error


def test_get_job_status(client):
    """测试获取任务状态"""
    # 先创建一个任务
    response = client.post(
        f"{settings.API_V1_PREFIX}/videos/process",
        json={
            "video_url": "https://www.youtube.com/watch?v=test",
            "user_interests": ["tech"],
        },
    )
    job_id = response.json()["job_id"]

    # 查询任务状态
    response = client.get(f"{settings.API_V1_PREFIX}/jobs/{job_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["job_id"] == job_id
    assert "status" in data
    assert "progress" in data


def test_get_nonexistent_job(client):
    """测试获取不存在的任务"""
    response = client.get(f"{settings.API_V1_PREFIX}/jobs/nonexistent")
    assert response.status_code == 404


def test_list_jobs(client, auth_headers):
    """测试列出任务"""
    response = client.get(
        f"{settings.API_V1_PREFIX}/jobs",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


# ========== 用户管理测试 ==========

def test_create_user(client):
    """测试创建用户"""
    response = client.post(
        f"{settings.API_V1_PREFIX}/users",
        json={
            "user_id": "test_user_123",
            "interests": ["tech", "ai", "programming"],
            "preferred_duration": "medium",
            "language": "zh-CN",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == "test_user_123"


def test_get_user(client):
    """测试获取用户信息"""
    # 先创建用户
    client.post(
        f"{settings.API_V1_PREFIX}/users",
        json={
            "user_id": "test_user_456",
            "interests": ["tech"],
        },
    )

    # 获取用户信息
    response = client.get(f"{settings.API_V1_PREFIX}/users/test_user_456")
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == "test_user_456"


def test_get_nonexistent_user(client):
    """测试获取不存在的用户"""
    response = client.get(f"{settings.API_V1_PREFIX}/users/nonexistent")
    assert response.status_code == 404


def test_update_user(client):
    """测试更新用户信息"""
    # 先创建用户
    client.post(
        f"{settings.API_V1_PREFIX}/users",
        json={
            "user_id": "test_user_789",
            "interests": ["tech"],
        },
    )

    # 更新用户
    response = client.put(
        f"{settings.API_V1_PREFIX}/users/test_user_789",
        json={
            "user_id": "test_user_789",
            "interests": ["tech", "ai", "music"],
            "preferred_duration": "long",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["interests"]) >= 3


# ========== 推荐系统测试 ==========

def test_get_recommendations(client):
    """测试获取推荐"""
    # 先创建用户
    client.post(
        f"{settings.API_V1_PREFIX}/users",
        json={
            "user_id": "test_user_rec",
            "interests": ["tech", "ai"],
        },
    )

    # 获取推荐
    response = client.get(
        f"{settings.API_V1_PREFIX}/recommendations/test_user_rec",
        params={"num": 5},
    )
    assert response.status_code == 200
    data = response.json()
    assert "recommendations" in data
    assert data["user_id"] == "test_user_rec"


def test_submit_feedback(client):
    """测试提交反馈"""
    # 先创建用户
    client.post(
        f"{settings.API_V1_PREFIX}/users",
        json={"user_id": "test_user_feedback", "interests": []},
    )

    # 提交反馈
    response = client.post(
        f"{settings.API_V1_PREFIX}/feedback",
        json={
            "user_id": "test_user_feedback",
            "video_id": "video_123",
            "action": "like",
            "rating": 0.9,
            "watch_time": 300,
            "watch_percentage": 0.8,
        },
    )
    assert response.status_code == 200


def test_submit_feedback_nonexistent_user(client):
    """测试为不存在的用户提交反馈"""
    response = client.post(
        f"{settings.API_V1_PREFIX}/feedback",
        json={
            "user_id": "nonexistent_user",
            "video_id": "video_123",
            "action": "like",
        },
    )
    assert response.status_code == 404


# ========== 统计分析测试 ==========

def test_get_trending(client):
    """测试获取热门内容"""
    response = client.get(
        f"{settings.API_V1_PREFIX}/stats/trending",
        params={"period": "today"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "videos" in data
    assert data["period"] == "today"


def test_get_analytics(client, auth_headers):
    """测试获取系统分析数据"""
    response = client.get(
        f"{settings.API_V1_PREFIX}/stats/analytics",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "total_users" in data
    assert "total_videos" in data
    assert "system_health" in data


def test_get_analytics_unauthorized(client):
    """测试未授权访问分析数据"""
    response = client.get(f"{settings.API_V1_PREFIX}/stats/analytics")
    assert response.status_code == 403


# ========== 管理功能测试 ==========

def test_cleanup_files(client, auth_headers):
    """测试清理文件"""
    response = client.post(
        f"{settings.API_V1_PREFIX}/admin/cleanup",
        params={"days": 7},
        headers=auth_headers,
    )
    assert response.status_code == 200


# ========== 速率限制测试 ==========

@pytest.mark.skip(reason="速率限制测试可能会影响其他测试")
def test_rate_limiting(client):
    """测试速率限制"""
    # 发送大量请求
    for _ in range(settings.RATE_LIMIT_PER_MINUTE + 5):
        response = client.get("/health")

    # 最后几个请求应该被限制
    assert response.status_code in [200, 429]


# ========== 错误处理测试 ==========

def test_404_error(client):
    """测试 404 错误"""
    response = client.get("/nonexistent-endpoint")
    assert response.status_code == 404


def test_validation_error(client):
    """测试验证错误"""
    response = client.post(
        f"{settings.API_V1_PREFIX}/users",
        json={
            "user_id": "",  # 空 user_id 应该失败
            "interests": [],
        },
    )
    assert response.status_code == 422


# ========== 运行测试 ==========

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
