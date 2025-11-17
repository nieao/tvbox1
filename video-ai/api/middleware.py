"""
中间件模块

实现速率限制、日志记录等功能
"""

import time
from typing import Callable
from collections import defaultdict
from datetime import datetime, timedelta

from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from .config import settings


# ========== 速率限制器 ==========

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[
        f"{settings.RATE_LIMIT_PER_MINUTE}/minute",
        f"{settings.RATE_LIMIT_PER_HOUR}/hour",
    ],
    enabled=settings.RATE_LIMIT_ENABLED,
)


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """速率限制超出处理"""
    return JSONResponse(
        status_code=429,
        content={
            "error": "RateLimitExceeded",
            "message": "请求过于频繁，请稍后再试",
            "detail": str(exc.detail),
        },
    )


# ========== 请求日志中间件 ==========

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """请求日志中间件"""

    async def dispatch(self, request: Request, call_next: Callable):
        start_time = time.time()

        # 记录请求
        print(f"[{datetime.now().isoformat()}] {request.method} {request.url.path}")

        # 处理请求
        response = await call_next(request)

        # 记录响应
        process_time = time.time() - start_time
        print(
            f"[{datetime.now().isoformat()}] {request.method} {request.url.path} "
            f"- {response.status_code} ({process_time:.3f}s)"
        )

        # 添加处理时间到响应头
        response.headers["X-Process-Time"] = str(process_time)

        return response


# ========== CORS 中间件 ==========
# 注意：通常使用 FastAPI 的 CORSMiddleware 即可


# ========== 错误处理中间件 ==========

class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """错误处理中间件"""

    async def dispatch(self, request: Request, call_next: Callable):
        try:
            return await call_next(request)
        except HTTPException as exc:
            # HTTP 异常直接传递
            raise exc
        except Exception as exc:
            # 捕获所有未处理的异常
            print(f"未处理的异常: {exc}")
            return JSONResponse(
                status_code=500,
                content={
                    "error": "InternalServerError",
                    "message": "服务器内部错误",
                    "detail": str(exc) if settings.DEBUG else None,
                    "timestamp": datetime.now().isoformat(),
                },
            )


# ========== IP 限制中间件 ==========

class IPWhitelistMiddleware(BaseHTTPMiddleware):
    """IP 白名单中间件（可选）"""

    def __init__(self, app, whitelist: list = None):
        super().__init__(app)
        self.whitelist = whitelist or []

    async def dispatch(self, request: Request, call_next: Callable):
        if self.whitelist and request.client:
            client_ip = request.client.host
            if client_ip not in self.whitelist:
                return JSONResponse(
                    status_code=403,
                    content={
                        "error": "Forbidden",
                        "message": "IP 地址未授权",
                    },
                )

        return await call_next(request)


# ========== 简单的内存速率限制器（备用）==========

class SimpleRateLimiter:
    """简单的内存速率限制器"""

    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.requests = defaultdict(list)

    def is_allowed(self, key: str) -> bool:
        """检查是否允许请求"""
        now = datetime.now()
        cutoff_time = now - timedelta(minutes=1)

        # 清理过期记录
        self.requests[key] = [
            req_time for req_time in self.requests[key] if req_time > cutoff_time
        ]

        # 检查请求数
        if len(self.requests[key]) >= self.requests_per_minute:
            return False

        # 记录新请求
        self.requests[key].append(now)
        return True


# 创建全局实例
simple_rate_limiter = SimpleRateLimiter(
    requests_per_minute=settings.RATE_LIMIT_PER_MINUTE
)


# ========== 请求 ID 中间件 ==========

class RequestIDMiddleware(BaseHTTPMiddleware):
    """为每个请求添加唯一 ID"""

    async def dispatch(self, request: Request, call_next: Callable):
        import uuid

        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id

        return response


# ========== 缓存中间件 ==========

class SimpleCacheMiddleware(BaseHTTPMiddleware):
    """简单的响应缓存中间件（用于 GET 请求）"""

    def __init__(self, app, ttl: int = 60):
        super().__init__(app)
        self.cache = {}
        self.ttl = ttl

    async def dispatch(self, request: Request, call_next: Callable):
        # 只缓存 GET 请求
        if request.method != "GET":
            return await call_next(request)

        # 生成缓存键
        cache_key = f"{request.method}:{request.url.path}:{request.url.query}"

        # 检查缓存
        if cache_key in self.cache:
            cached_data, cached_time = self.cache[cache_key]
            if (datetime.now() - cached_time).seconds < self.ttl:
                print(f"缓存命中: {cache_key}")
                return Response(
                    content=cached_data["content"],
                    status_code=cached_data["status_code"],
                    headers=cached_data["headers"],
                    media_type=cached_data["media_type"],
                )

        # 处理请求
        response = await call_next(request)

        # 只缓存成功的响应
        if response.status_code == 200:
            # 读取响应内容
            content = b""
            async for chunk in response.body_iterator:
                content += chunk

            # 缓存
            self.cache[cache_key] = (
                {
                    "content": content,
                    "status_code": response.status_code,
                    "headers": dict(response.headers),
                    "media_type": response.media_type,
                },
                datetime.now(),
            )

            # 返回新响应
            return Response(
                content=content,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type,
            )

        return response
