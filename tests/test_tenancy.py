"""
多租户系统测试
"""

import pytest
import asyncio
from synapse.src.tenancy import (
    TenantManager, PermissionManager,
    Tenant, User, TenantStatus, PlanType, TenantQuota
)


class TestTenantManager:
    """租户管理器测试"""

    @pytest.fixture
    def manager(self):
        return TenantManager()

    @pytest.mark.asyncio
    async def test_create_tenant(self, manager):
        """测试创建租户"""
        tenant = await manager.create_tenant("测试租户", PlanType.PRO)
        assert tenant is not None
        assert tenant.name == "测试租户"
        assert tenant.plan == PlanType.PRO

    @pytest.mark.asyncio
    async def test_get_tenant(self, manager):
        """测试获取租户"""
        tenant = await manager.create_tenant("测试租户")
        retrieved = await manager.get_tenant(tenant.tenant_id)
        assert retrieved is not None
        assert retrieved.tenant_id == tenant.tenant_id

    @pytest.mark.asyncio
    async def test_delete_tenant(self, manager):
        """测试删除租户"""
        tenant = await manager.create_tenant("测试租户")
        result = await manager.delete_tenant(tenant.tenant_id)
        assert result is True

        retrieved = await manager.get_tenant(tenant.tenant_id)
        assert retrieved is None

    @pytest.mark.asyncio
    async def test_update_plan(self, manager):
        """测试更新套餐"""
        tenant = await manager.create_tenant("测试租户", PlanType.FREE)
        result = await manager.update_tenant_plan(tenant.tenant_id, PlanType.ENTERPRISE)
        assert result is True

        updated = await manager.get_tenant(tenant.tenant_id)
        assert updated.plan == PlanType.ENTERPRISE


class TestUserManagement:
    """用户管理测试"""

    @pytest.fixture
    def manager(self):
        return TenantManager()

    @pytest.mark.asyncio
    async def test_add_user(self, manager):
        """测试添加用户"""
        tenant = await manager.create_tenant("测试租户")
        user = await manager.add_user(
            tenant.tenant_id,
            "testuser",
            "test@example.com",
            "user"
        )
        assert user is not None
        assert user.username == "testuser"

    @pytest.mark.asyncio
    async def test_remove_user(self, manager):
        """测试移除用户"""
        tenant = await manager.create_tenant("测试租户")
        user = await manager.add_user(tenant.tenant_id, "testuser", "test@example.com")

        result = await manager.remove_user(user.user_id)
        assert result is True

    @pytest.mark.asyncio
    async def test_get_users_by_tenant(self, manager):
        """测试获取租户用户"""
        tenant = await manager.create_tenant("测试租户")
        await manager.add_user(tenant.tenant_id, "user1", "user1@example.com")
        await manager.add_user(tenant.tenant_id, "user2", "user2@example.com")

        users = manager.get_users_by_tenant(tenant.tenant_id)
        assert len(users) == 2


class TestPermissionManager:
    """权限管理器测试"""

    @pytest.fixture
    def manager(self):
        return PermissionManager()

    @pytest.fixture
    def admin_user(self):
        return User(user_id="admin", tenant_id="t1", username="admin", role="admin")

    @pytest.fixture
    def normal_user(self):
        return User(user_id="user", tenant_id="t1", username="user", role="user")

    def test_admin_permission(self, manager, admin_user):
        """测试管理员权限"""
        assert manager.check_permission(admin_user, "devices", "read") is True
        assert manager.check_permission(admin_user, "devices", "write") is True
        assert manager.check_permission(admin_user, "scenes", "execute") is True

    def test_normal_user_permission(self, manager, normal_user):
        """测试普通用户权限"""
        assert manager.check_permission(normal_user, "devices", "read") is True
        assert manager.check_permission(normal_user, "devices", "write") is False

    def test_add_role_permission(self, manager):
        """测试添加角色权限"""
        manager.add_role_permission("custom_role", "write:devices")

        # 创建自定义角色用户
        user = User(user_id="custom", tenant_id="t1", username="custom", role="custom_role")
        # 这个测试需要先注册角色


class TestTenantQuota:
    """租户配额测试"""

    def test_free_plan_quota(self):
        """测试免费套餐配额"""
        quota = TenantQuota(
            max_devices=10,
            max_scenes=10,
            max_users=2
        )
        assert quota.max_devices == 10
        assert quota.max_scenes == 10

    @pytest.mark.asyncio
    async def test_quota_check(self):
        """测试配额检查"""
        manager = TenantManager()
        tenant = await manager.create_tenant("测试租户", PlanType.FREE)

        # 免费套餐最多 10 个设备
        result = await manager.check_quota(tenant.tenant_id, "devices", 5)
        assert result is True

        result = await manager.check_quota(tenant.tenant_id, "devices", 15)
        assert result is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
