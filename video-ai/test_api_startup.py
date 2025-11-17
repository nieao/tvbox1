#!/usr/bin/env python3
"""
测试 API 是否可以正常启动

快速验证 API 配置和依赖
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """测试模块导入"""
    print("测试模块导入...")

    try:
        from api.main import app
        print("✅ api.main 导入成功")
    except ImportError as e:
        print(f"❌ api.main 导入失败: {e}")
        return False

    try:
        from api.models import VideoProcessRequest, UserProfileRequest
        print("✅ api.models 导入成功")
    except ImportError as e:
        print(f"❌ api.models 导入失败: {e}")
        return False

    try:
        from api.services import video_service, user_service, recommendation_service
        print("✅ api.services 导入成功")
    except ImportError as e:
        print(f"❌ api.services 导入失败: {e}")
        return False

    try:
        from api.auth import authenticate_user, create_access_token
        print("✅ api.auth 导入成功")
    except ImportError as e:
        print(f"❌ api.auth 导入失败: {e}")
        return False

    return True


def test_api_routes():
    """测试 API 路由"""
    print("\n测试 API 路由...")

    try:
        from api.main import app
        from fastapi.testclient import TestClient

        client = TestClient(app)

        # 测试根端点
        response = client.get("/")
        assert response.status_code == 200
        print("✅ 根端点测试通过")

        # 测试健康检查
        response = client.get("/health")
        assert response.status_code == 200
        print("✅ 健康检查端点测试通过")

        # 测试 OpenAPI 文档
        response = client.get("/openapi.json")
        assert response.status_code == 200
        print("✅ OpenAPI 文档生成成功")

        return True

    except Exception as e:
        print(f"❌ API 路由测试失败: {e}")
        return False


def test_config():
    """测试配置"""
    print("\n测试配置...")

    try:
        from api.config import settings

        print(f"  APP_NAME: {settings.APP_NAME}")
        print(f"  APP_VERSION: {settings.APP_VERSION}")
        print(f"  HOST: {settings.HOST}")
        print(f"  PORT: {settings.PORT}")
        print(f"  DEBUG: {settings.DEBUG}")

        print("✅ 配置加载成功")
        return True

    except Exception as e:
        print(f"❌ 配置测试失败: {e}")
        return False


def main():
    """主函数"""
    print("=" * 60)
    print("Video-AI API 启动测试")
    print("=" * 60)

    # 运行测试
    results = []

    results.append(("模块导入", test_imports()))
    results.append(("配置", test_config()))
    results.append(("API 路由", test_api_routes()))

    # 显示结果
    print("\n" + "=" * 60)
    print("测试结果")
    print("=" * 60)

    all_passed = True
    for name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{name}: {status}")
        if not passed:
            all_passed = False

    print("=" * 60)

    if all_passed:
        print("✅ 所有测试通过！API 可以正常启动")
        print("\n启动命令:")
        print("  python -m uvicorn api.main:app --reload")
        print("\n访问文档:")
        print("  http://localhost:8000/docs")
        return 0
    else:
        print("❌ 部分测试失败，请检查配置")
        return 1


if __name__ == "__main__":
    sys.exit(main())
