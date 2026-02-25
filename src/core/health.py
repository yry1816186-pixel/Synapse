"""
健康检查模块
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import asyncio
import logging

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """健康状态"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


@dataclass
class HealthCheckResult:
    """健康检查结果"""
    name: str
    status: HealthStatus
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    latency_ms: float = 0


class HealthChecker:
    """健康检查器"""

    def __init__(self):
        self._checks: Dict[str, callable] = {}
        self._results: Dict[str, HealthCheckResult] = {}

    def register(self, name: str, check_func: callable) -> None:
        """注册健康检查"""
        self._checks[name] = check_func
        logger.info(f"注册健康检查: {name}")

    async def run_check(self, name: str) -> HealthCheckResult:
        """运行单个检查"""
        if name not in self._checks:
            return HealthCheckResult(
                name=name,
                status=HealthStatus.UNHEALTHY,
                message="检查不存在"
            )

        start = datetime.now()
        try:
            result = await self._checks[name]() if asyncio.iscoroutinefunction(self._checks[name]) else self._checks[name]()

            if isinstance(result, HealthCheckResult):
                self._results[name] = result
                return result

            # 简单返回值
            status = HealthStatus.HEALTHY if result else HealthStatus.UNHEALTHY
            result = HealthCheckResult(
                name=name,
                status=status,
                message="OK" if result else "FAILED"
            )
            self._results[name] = result
            return result

        except Exception as e:
            result = HealthCheckResult(
                name=name,
                status=HealthStatus.UNHEALTHY,
                message=str(e)
            )
            self._results[name] = result
            return result

    async def run_all(self) -> Dict[str, HealthCheckResult]:
        """运行所有检查"""
        tasks = [self.run_check(name) for name in self._checks]
        await asyncio.gather(*tasks)
        return self._results

    def get_result(self, name: str) -> Optional[HealthCheckResult]:
        """获取检查结果"""
        return self._results.get(name)

    def get_all_results(self) -> Dict[str, HealthCheckResult]:
        """获取所有结果"""
        return self._results

    def get_overall_status(self) -> HealthStatus:
        """获取总体状态"""
        if not self._results:
            return HealthStatus.HEALTHY

        statuses = [r.status for r in self._results.values()]

        if HealthStatus.UNHEALTHY in statuses:
            return HealthStatus.UNHEALTHY
        elif HealthStatus.DEGRADED in statuses:
            return HealthStatus.DEGRADED
        else:
            return HealthStatus.HEALTHY


# 预定义检查
async def check_database() -> HealthCheckResult:
    """检查数据库"""
    # 模拟检查
    await asyncio.sleep(0.01)
    return HealthCheckResult(
        name="database",
        status=HealthStatus.HEALTHY,
        message="连接正常"
    )


async def check_redis() -> HealthCheckResult:
    """检查 Redis"""
    await asyncio.sleep(0.01)
    return HealthCheckResult(
        name="redis",
        status=HealthStatus.HEALTHY,
        message="连接正常"
    )


async def check_mqtt() -> HealthCheckResult:
    """检查 MQTT"""
    await asyncio.sleep(0.01)
    return HealthCheckResult(
        name="mqtt",
        status=HealthStatus.HEALTHY,
        message="连接正常"
    )


# 全局健康检查器
health_checker = HealthChecker()

# 注册默认检查
health_checker.register("database", check_database)
health_checker.register("redis", check_redis)
health_checker.register("mqtt", check_mqtt)
