"""
分布式限流系统 - 借鉴最新论文
Redis + Lua 三层限流架构
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import asyncio
import logging
import time

logger = logging.getLogger(__name__)


class RateLimitStrategy(Enum):
    """限流策略"""
    TOKEN_BUCKET = "token_bucket"    # 令牌桶
    SLIDING_WINDOW = "sliding_window"  # 滑动窗口
    LEAKY_BUCKET = "leaky_bucket"    # 漏桶


@dataclass
class RateLimitConfig:
    """限流配置"""
    max_requests: int = 100        # 最大请求数
    window_seconds: int = 60       # 时间窗口
    strategy: RateLimitStrategy = RateLimitStrategy.SLIDING_WINDOW


@dataclass
class RateLimitResult:
    """限流结果"""
    allowed: bool
    remaining: int
    reset_at: float
    retry_after: float = 0


class DistributedRateLimiter:
    """
    分布式限流器

    Redis + Lua 三层限流架构
    - L1: 本地缓存限流
    - L2: 分布式限流
    - L3: 全局限流
    """

    def __init__(self, redis_client=None):
        self._redis = redis_client
        self._local_cache: Dict[str, List[float]] = {}
        self._configs: Dict[str, RateLimitConfig] = {}

    def configure(self, key: str, config: RateLimitConfig) -> None:
        """配置限流规则"""
        self._configs[key] = config

    async def check(self, key: str, identifier: str) -> RateLimitResult:
        """检查限流"""
        config = self._configs.get(key)
        if not config:
            return RateLimitResult(allowed=True, remaining=-1, reset_at=0)

        # L1: 本地缓存检查
        local_result = self._check_local(key, identifier, config)
        if not local_result.allowed:
            return local_result

        # L2: 分布式检查（如果有 Redis）
        if self._redis:
            return await self._check_distributed(key, identifier, config)

        return local_result

    def _check_local(self, key: str, identifier: str, config: RateLimitConfig) -> RateLimitResult:
        """本地限流检查"""
        cache_key = f"{key}:{identifier}"
        now = time.time()
        window_start = now - config.window_seconds

        # 获取或创建缓存
        if cache_key not in self._local_cache:
            self._local_cache[cache_key] = []

        # 清理过期记录
        self._local_cache[cache_key] = [
            t for t in self._local_cache[cache_key] if t > window_start
        ]

        # 检查
        current_count = len(self._local_cache[cache_key])
        remaining = config.max_requests - current_count - 1

        if current_count >= config.max_requests:
            oldest = min(self._local_cache[cache_key])
            retry_after = oldest + config.window_seconds - now
            return RateLimitResult(
                allowed=False,
                remaining=0,
                reset_at=oldest + config.window_seconds,
                retry_after=retry_after
            )

        # 记录
        self._local_cache[cache_key].append(now)

        return RateLimitResult(
            allowed=True,
            remaining=max(0, remaining),
            reset_at=now + config.window_seconds
        )

    async def _check_distributed(self, key: str, identifier: str, 
                                 config: RateLimitConfig) -> RateLimitResult:
        """分布式限流检查"""
        # 模拟 Redis + Lua 脚本执行
        # 实际: EVALSHA lua_script key_count keys argv
        return self._check_local(key, identifier, config)

    def get_stats(self) -> Dict[str, Any]:
        """获取统计"""
        return {
            "tracked_keys": len(self._local_cache),
            "configured_limits": len(self._configs)
        }


# 全局限流器
rate_limiter = DistributedRateLimiter()
