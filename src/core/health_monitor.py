"""
服务健康监控器 - 24/7 监控
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import logging

logger = logging.getLogger(__name__)


class ServiceStatus(Enum):
    """服务状态"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class ServiceHealth:
    """服务健康状态"""
    service_name: str
    status: ServiceStatus = ServiceStatus.UNKNOWN
    last_check: datetime = None
    last_healthy: datetime = None
    consecutive_failures: int = 0
    total_checks: int = 0
    total_failures: int = 0


@dataclass
class Alert:
    """告警"""
    alert_id: str
    service_name: str
    severity: str  # info, warning, critical
    message: str
    timestamp: datetime = field(default_factory=datetime.now)
    resolved: bool = False


class HealthMonitor:
    """健康监控器"""

    def __init__(self, check_interval: int = 60):
        self.check_interval = check_interval
        self._services: Dict[str, ServiceHealth] = {}
        self._alerts: List[Alert] = []
        self._checkers: Dict[str, callable] = {}
        self._running = False
        self._alert_counter = 0

    def register_service(self, service_name: str, checker: callable) -> None:
        """注册服务"""
        self._services[service_name] = ServiceHealth(service_name=service_name)
        self._checkers[service_name] = checker
        logger.info(f"注册服务监控: {service_name}")

    async def start(self) -> None:
        """启动监控"""
        self._running = True
        logger.info("健康监控器启动")
        asyncio.create_task(self._monitor_loop())

    async def stop(self) -> None:
        """停止监控"""
        self._running = False
        logger.info("健康监控器停止")

    async def _monitor_loop(self) -> None:
        """监控循环"""
        while self._running:
            await self._check_all()
            await asyncio.sleep(self.check_interval)

    async def _check_all(self) -> None:
        """检查所有服务"""
        for service_name, checker in self._checkers.items():
            try:
                is_healthy = await checker() if asyncio.iscoroutinefunction(checker) else checker()
                await self._update_health(service_name, is_healthy)
            except Exception as e:
                await self._update_health(service_name, False, str(e))

    async def _update_health(self, service_name: str, is_healthy: bool, error: str = None) -> None:
        """更新健康状态"""
        health = self._services.get(service_name)
        if not health:
            return

        health.last_check = datetime.now()
        health.total_checks += 1

        if is_healthy:
            health.status = ServiceStatus.HEALTHY
            health.last_healthy = datetime.now()
            health.consecutive_failures = 0

            # 解决之前的告警
            for alert in self._alerts:
                if alert.service_name == service_name and not alert.resolved:
                    alert.resolved = True
        else:
            health.consecutive_failures += 1
            health.total_failures += 1

            if health.consecutive_failures >= 3:
                health.status = ServiceStatus.UNHEALTHY
                await self._create_alert(service_name, "critical", 
                    f"{service_name} 连续失败 {health.consecutive_failures} 次")
            elif health.consecutive_failures >= 1:
                health.status = ServiceStatus.DEGRADED
                await self._create_alert(service_name, "warning",
                    f"{service_name} 检测到问题: {error}")

    async def _create_alert(self, service_name: str, severity: str, message: str) -> None:
        """创建告警"""
        self._alert_counter += 1
        alert = Alert(
            alert_id=f"alert_{self._alert_counter}",
            service_name=service_name,
            severity=severity,
            message=message
        )
        self._alerts.append(alert)
        logger.warning(f"告警 [{severity}]: {message}")

    def get_health(self, service_name: str = None) -> Dict[str, Any]:
        """获取健康状态"""
        if service_name:
            health = self._services.get(service_name)
            if health:
                return {
                    "service": service_name,
                    "status": health.status.value,
                    "last_check": health.last_check.isoformat() if health.last_check else None,
                    "consecutive_failures": health.consecutive_failures,
                    "uptime": 1 - (health.total_failures / max(health.total_checks, 1))
                }
            return {}

        return {
            name: {
                "status": h.status.value,
                "last_check": h.last_check.isoformat() if h.last_check else None,
                "uptime": 1 - (h.total_failures / max(h.total_checks, 1))
            }
            for name, h in self._services.items()
        }

    def get_alerts(self, unresolved_only: bool = False) -> List[Dict[str, Any]]:
        """获取告警"""
        alerts = self._alerts
        if unresolved_only:
            alerts = [a for a in alerts if not a.resolved]

        return [
            {
                "alert_id": a.alert_id,
                "service": a.service_name,
                "severity": a.severity,
                "message": a.message,
                "timestamp": a.timestamp.isoformat(),
                "resolved": a.resolved
            }
            for a in alerts[-50:]  # 最近50条
        ]

    def get_overall_status(self) -> ServiceStatus:
        """获取总体状态"""
        if not self._services:
            return ServiceStatus.UNKNOWN

        statuses = [h.status for h in self._services.values()]

        if ServiceStatus.UNHEALTHY in statuses:
            return ServiceStatus.UNHEALTHY
        elif ServiceStatus.DEGRADED in statuses:
            return ServiceStatus.DEGRADED
        elif ServiceStatus.HEALTHY in statuses:
            return ServiceStatus.HEALTHY
        else:
            return ServiceStatus.UNKNOWN


# 全局监控器
health_monitor = HealthMonitor()
