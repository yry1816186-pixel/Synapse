"""
多租户系统 - 租户管理和权限控制
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import asyncio
import logging
import uuid

logger = logging.getLogger(__name__)


class TenantStatus(Enum):
    """租户状态"""
    ACTIVE = "active"
    SUSPENDED = "suspended"
    TRIAL = "trial"
    EXPIRED = "expired"


class PlanType(Enum):
    """套餐类型"""
    FREE = "free"
    STARTER = "starter"
    PRO = "pro"
    ENTERPRISE = "enterprise"


@dataclass
class TenantQuota:
    """租户配额"""
    max_devices: int = 100
    max_scenes: int = 50
    max_users: int = 10
    max_api_calls_per_day: int = 10000
    storage_mb: int = 1000
    features: List[str] = field(default_factory=list)


# 套餐配额定义
PLAN_QUOTAS = {
    PlanType.FREE: TenantQuota(
        max_devices=10,
        max_scenes=10,
        max_users=2,
        max_api_calls_per_day=1000,
        storage_mb=100,
        features=["basic"]
    ),
    PlanType.STARTER: TenantQuota(
        max_devices=50,
        max_scenes=30,
        max_users=5,
        max_api_calls_per_day=5000,
        storage_mb=500,
        features=["basic", "scenes"]
    ),
    PlanType.PRO: TenantQuota(
        max_devices=200,
        max_scenes=100,
        max_users=20,
        max_api_calls_per_day=50000,
        storage_mb=2000,
        features=["basic", "scenes", "api", "analytics"]
    ),
    PlanType.ENTERPRISE: TenantQuota(
        max_devices=10000,
        max_scenes=5000,
        max_users=1000,
        max_api_calls_per_day=1000000,
        storage_mb=50000,
        features=["basic", "scenes", "api", "analytics", "sso", "custom"]
    ),
}


@dataclass
class Tenant:
    """租户"""
    tenant_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    status: TenantStatus = TenantStatus.ACTIVE
    plan: PlanType = PlanType.FREE
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    settings: Dict[str, Any] = field(default_factory=dict)

    @property
    def quota(self) -> TenantQuota:
        return PLAN_QUOTAS[self.plan]


@dataclass
class User:
    """用户"""
    user_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    tenant_id: str = ""
    username: str = ""
    email: str = ""
    role: str = "user"  # admin, manager, user
    created_at: datetime = field(default_factory=datetime.now)
    last_login: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class TenantManager:
    """租户管理器"""

    def __init__(self):
        self._tenants: Dict[str, Tenant] = {}
        self._users: Dict[str, User] = {}
        self._tenant_users: Dict[str, List[str]] = {}

    async def create_tenant(self, name: str, plan: PlanType = PlanType.FREE,
                           **kwargs) -> Tenant:
        """创建租户"""
        tenant = Tenant(
            name=name,
            plan=plan,
            **kwargs
        )

        self._tenants[tenant.tenant_id] = tenant
        self._tenant_users[tenant.tenant_id] = []

        logger.info(f"租户已创建: {name} [{tenant.tenant_id}]")
        return tenant

    async def delete_tenant(self, tenant_id: str) -> bool:
        """删除租户"""
        if tenant_id not in self._tenants:
            return False

        # 删除租户下的所有用户
        for user_id in self._tenant_users.get(tenant_id, []):
            if user_id in self._users:
                del self._users[user_id]

        del self._tenants[tenant_id]
        del self._tenant_users[tenant_id]

        logger.info(f"租户已删除: {tenant_id}")
        return True

    async def get_tenant(self, tenant_id: str) -> Optional[Tenant]:
        """获取租户"""
        return self._tenants.get(tenant_id)

    async def update_tenant_plan(self, tenant_id: str, plan: PlanType) -> bool:
        """更新租户套餐"""
        tenant = self._tenants.get(tenant_id)
        if not tenant:
            return False

        tenant.plan = plan
        logger.info(f"租户 {tenant_id} 套餐已更新为 {plan.value}")
        return True

    async def add_user(self, tenant_id: str, username: str, email: str,
                      role: str = "user") -> Optional[User]:
        """添加用户"""
        if tenant_id not in self._tenants:
            return None

        tenant = self._tenants[tenant_id]
        quota = tenant.quota

        # 检查用户数量限制
        current_users = len(self._tenant_users.get(tenant_id, []))
        if current_users >= quota.max_users:
            logger.warning(f"租户 {tenant_id} 已达用户上限")
            return None

        user = User(
            tenant_id=tenant_id,
            username=username,
            email=email,
            role=role
        )

        self._users[user.user_id] = user
        self._tenant_users[tenant_id].append(user.user_id)

        logger.info(f"用户已添加: {username} -> {tenant_id}")
        return user

    async def remove_user(self, user_id: str) -> bool:
        """移除用户"""
        if user_id not in self._users:
            return False

        user = self._users[user_id]
        tenant_id = user.tenant_id

        if tenant_id in self._tenant_users:
            self._tenant_users[tenant_id].remove(user_id)

        del self._users[user_id]
        logger.info(f"用户已移除: {user_id}")
        return True

    def get_users_by_tenant(self, tenant_id: str) -> List[User]:
        """获取租户下的用户"""
        user_ids = self._tenant_users.get(tenant_id, [])
        return [self._users[uid] for uid in user_ids if uid in self._users]

    async def check_quota(self, tenant_id: str, resource: str,
                         current: int) -> bool:
        """检查配额"""
        tenant = self._tenants.get(tenant_id)
        if not tenant:
            return False

        quota = tenant.quota
        limits = {
            "devices": quota.max_devices,
            "scenes": quota.max_scenes,
            "users": quota.max_users
        }

        limit = limits.get(resource)
        if limit is None:
            return True

        return current < limit


class PermissionManager:
    """权限管理器 - 基于 Casbin"""

    def __init__(self):
        self._policies: Dict[str, List[Dict[str, Any]]] = {}
        self._roles: Dict[str, List[str]] = {
            "admin": ["*"],
            "manager": ["read:*", "write:devices", "write:scenes", "execute:scenes"],
            "user": ["read:devices", "read:scenes", "execute:scenes"]
        }

    def check_permission(self, user: User, resource: str,
                        action: str) -> bool:
        """检查权限"""
        role = user.role
        permissions = self._roles.get(role, [])

        for perm in permissions:
            if perm == "*":
                return True

            perm_action, perm_resource = perm.split(":", 1)

            if perm_action == action or perm_action == "*":
                if perm_resource == resource or perm_resource == "*":
                    return True
                if resource.startswith(perm_resource.rstrip("*")):
                    return True

        return False

    def add_role_permission(self, role: str, permission: str) -> None:
        """添加角色权限"""
        if role not in self._roles:
            self._roles[role] = []
        self._roles[role].append(permission)

    def get_role_permissions(self, role: str) -> List[str]:
        """获取角色权限"""
        return self._roles.get(role, [])


# 全局实例
tenant_manager = TenantManager()
permission_manager = PermissionManager()
