"""
多租户隔离系统 - δ-公平性调度
借鉴 MUSE/Equilibria 论文
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import asyncio
import logging
import math

logger = logging.getLogger(__name__)


class ResourceType(Enum):
    """资源类型"""
    CPU = "cpu"
    MEMORY = "memory"
    STORAGE = "storage"
    NETWORK = "network"
    GPU = "gpu"


@dataclass
class TenantQuota:
    """租户配额"""
    tenant_id: str
    cpu_limit: float = 1.0        # CPU 核数
    memory_limit: float = 1024    # MB
    storage_limit: float = 10240  # MB
    network_limit: float = 100    # Mbps
    gpu_limit: float = 0.0        # GPU 数量
    priority: int = 5             # 优先级 1-10


@dataclass
class ResourceUsage:
    """资源使用"""
    cpu_used: float = 0.0
    memory_used: float = 0.0
    storage_used: float = 0.0
    network_used: float = 0.0
    gpu_used: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)


class DeltaFairScheduler:
    """
    δ-公平性调度器

    延迟受限公平调度
    解决多租户隔离问题
    """

    def __init__(self, delta: float = 0.1):
        """
        初始化

        Args:
            delta: 公平性容忍度 (0-1)
        """
        self.delta = delta
        self._quotas: Dict[str, TenantQuota] = {}
        self._usage: Dict[str, ResourceUsage] = {}
        self._fair_shares: Dict[str, float] = {}
        self._total_resources = {
            ResourceType.CPU: 16.0,
            ResourceType.MEMORY: 32768.0,
            ResourceType.STORAGE: 1000000.0,
            ResourceType.NETWORK: 1000.0,
            ResourceType.GPU: 4.0
        }

    def register_tenant(self, quota: TenantQuota) -> None:
        """注册租户"""
        self._quotas[quota.tenant_id] = quota
        self._usage[quota.tenant_id] = ResourceUsage()
        self._update_fair_shares()
        logger.info(f"注册租户: {quota.tenant_id}")

    def _update_fair_shares(self) -> None:
        """更新公平份额"""
        total_weight = sum(q.priority for q in self._quotas.values())

        for tenant_id, quota in self._quotas.items():
            self._fair_shares[tenant_id] = quota.priority / total_weight if total_weight > 0 else 0

    async def allocate(self, tenant_id: str, resource_type: ResourceType,
                      amount: float) -> bool:
        """
        分配资源

        使用 δ-公平性检查
        """
        if tenant_id not in self._quotas:
            return False

        quota = self._quotas[tenant_id]
        usage = self._usage[tenant_id]

        # 检查配额
        limit = self._get_limit(quota, resource_type)
        used = self._get_used(usage, resource_type)

        if used + amount > limit:
            logger.warning(f"租户 {tenant_id} {resource_type.value} 配额不足")
            return False

        # 检查 δ-公平性
        if not self._check_fairness(tenant_id, resource_type, amount):
            logger.warning(f"租户 {tenant_id} 违反 δ-公平性")
            return False

        # 分配
        self._set_used(usage, resource_type, used + amount)
        return True

    def _get_limit(self, quota: TenantQuota, resource_type: ResourceType) -> float:
        """获取配额限制"""
        limits = {
            ResourceType.CPU: quota.cpu_limit,
            ResourceType.MEMORY: quota.memory_limit,
            ResourceType.STORAGE: quota.storage_limit,
            ResourceType.NETWORK: quota.network_limit,
            ResourceType.GPU: quota.gpu_limit
        }
        return limits.get(resource_type, 0)

    def _get_used(self, usage: ResourceUsage, resource_type: ResourceType) -> float:
        """获取已使用量"""
        used = {
            ResourceType.CPU: usage.cpu_used,
            ResourceType.MEMORY: usage.memory_used,
            ResourceType.STORAGE: usage.storage_used,
            ResourceType.NETWORK: usage.network_used,
            ResourceType.GPU: usage.gpu_used
        }
        return used.get(resource_type, 0)

    def _set_used(self, usage: ResourceUsage, resource_type: ResourceType,
                 value: float) -> None:
        """设置使用量"""
        if resource_type == ResourceType.CPU:
            usage.cpu_used = value
        elif resource_type == ResourceType.MEMORY:
            usage.memory_used = value
        elif resource_type == ResourceType.STORAGE:
            usage.storage_used = value
        elif resource_type == ResourceType.NETWORK:
            usage.network_used = value
        elif resource_type == ResourceType.GPU:
            usage.gpu_used = value

    def _check_fairness(self, tenant_id: str, resource_type: ResourceType,
                       amount: float) -> bool:
        """检查 δ-公平性"""
        fair_share = self._fair_shares.get(tenant_id, 0)
        total_used = sum(self._get_used(u, resource_type) for u in self._usage.values())
        tenant_used = self._get_used(self._usage[tenant_id], resource_type)

        if total_used == 0:
            return True

        # 计算当前份额
        current_share = tenant_used / total_used

        # δ-公平性：份额差不超过 delta
        if current_share > fair_share + self.delta:
            return False

        return True

    async def release(self, tenant_id: str, resource_type: ResourceType,
                     amount: float) -> None:
        """释放资源"""
        if tenant_id not in self._usage:
            return

        usage = self._usage[tenant_id]
        used = self._get_used(usage, resource_type)
        self._set_used(usage, resource_type, max(0, used - amount))

    def get_tenant_usage(self, tenant_id: str) -> Optional[Dict[str, Any]]:
        """获取租户使用情况"""
        if tenant_id not in self._quotas:
            return None

        quota = self._quotas[tenant_id]
        usage = self._usage[tenant_id]

        return {
            "tenant_id": tenant_id,
            "cpu": {"used": usage.cpu_used, "limit": quota.cpu_limit},
            "memory": {"used": usage.memory_used, "limit": quota.memory_limit},
            "storage": {"used": usage.storage_used, "limit": quota.storage_limit},
            "network": {"used": usage.network_used, "limit": quota.network_limit},
            "gpu": {"used": usage.gpu_used, "limit": quota.gpu_limit},
            "fair_share": self._fair_shares.get(tenant_id, 0)
        }

    def get_system_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        total_usage = {
            "cpu": sum(u.cpu_used for u in self._usage.values()),
            "memory": sum(u.memory_used for u in self._usage.values()),
            "storage": sum(u.storage_used for u in self._usage.values()),
            "network": sum(u.network_used for u in self._usage.values()),
            "gpu": sum(u.gpu_used for u in self._usage.values())
        }

        return {
            "tenants": len(self._quotas),
            "delta": self.delta,
            "total_usage": total_usage,
            "total_resources": {k.value: v for k, v in self._total_resources.items()}
        }


# 全局调度器
delta_fair_scheduler = DeltaFairScheduler()
