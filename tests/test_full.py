"""
完整测试套件
"""

import pytest
import asyncio
from typing import Dict, Any

# ============ 核心模块测试 ============

class TestPluginSystem:
    """插件系统测试"""

    @pytest.fixture
    def manager(self):
        from synapse.src.core.plugin_system import PluginManager
        return PluginManager()

    @pytest.mark.asyncio
    async def test_register_plugin(self, manager):
        from synapse.src.core.plugin_system import PluginBase, HookType

        class TestPlugin(PluginBase):
            name = "test"
            hooks = [HookType.SYSTEM_EVENT]

            async def initialize(self, context):
                return True

            async def shutdown(self):
                pass

        plugin = TestPlugin()
        result = await manager.register_plugin(plugin)
        assert result is True
        assert "test" in manager.list_plugins()


class TestEventBus:
    """事件总线测试"""

    @pytest.fixture
    def bus(self):
        from synapse.src.core.event_bus import EventBus
        return EventBus()

    @pytest.mark.asyncio
    async def test_publish_subscribe(self, bus):
        from synapse.src.core.event_bus import Event, EventType

        received = []

        async def callback(event):
            received.append(event)

        bus.subscribe(EventType.SYSTEM_START, callback)
        await bus.start()

        event = Event(event_type=EventType.SYSTEM_START, source="test")
        await bus.publish(event)

        await asyncio.sleep(0.1)
        assert len(received) == 1

        await bus.stop()


class TestScheduler:
    """调度器测试"""

    def test_priority_order(self):
        from synapse.src.core.scheduler import TaskPriority

        assert TaskPriority.LOW.value < TaskPriority.NORMAL.value
        assert TaskPriority.NORMAL.value < TaskPriority.HIGH.value
        assert TaskPriority.HIGH.value < TaskPriority.CRITICAL.value


class TestMetrics:
    """指标测试"""

    @pytest.fixture
    def monitor(self):
        from synapse.src.core.metrics import PerformanceMonitor
        return PerformanceMonitor()

    def test_counter(self, monitor):
        monitor.metrics.counter("test_counter", 1)
        assert monitor.metrics.get_counter("test_counter") == 1

        monitor.metrics.counter("test_counter", 2)
        assert monitor.metrics.get_counter("test_counter") == 3

    def test_gauge(self, monitor):
        monitor.metrics.gauge("test_gauge", 42.5)
        assert monitor.metrics.get_gauge("test_gauge") == 42.5

    def test_histogram(self, monitor):
        for i in range(100):
            monitor.metrics.histogram("test_histogram", i)

        stats = monitor.metrics.get_histogram_stats("test_histogram")
        assert stats["count"] == 100
        assert stats["min"] == 0
        assert stats["max"] == 99


# ============ 设备模块测试 ============

class TestDeviceAbstraction:
    """设备抽象层测试"""

    @pytest.fixture
    def registry(self):
        from synapse.src.device_abstraction import DeviceRegistry
        return DeviceRegistry()

    @pytest.mark.asyncio
    async def test_register_device(self, registry):
        from synapse.src.device_abstraction import VirtualDevice, DeviceType

        device = VirtualDevice(
            device_id="test_1",
            name="测试设备",
            device_type=DeviceType.SENSOR
        )

        result = await registry.register(device)
        assert result is True
        assert registry.get("test_1") is not None

    @pytest.mark.asyncio
    async def test_virtual_device(self):
        from synapse.src.device_abstraction import VirtualDevice, DeviceType

        device = VirtualDevice(
            device_id="v1",
            name="虚拟设备",
            device_type=DeviceType.SWITCH
        )

        await device.connect()
        assert device.state.value == "online"

        result = await device.execute("test_command")
        assert result["success"] is True

        await device.disconnect()
        assert device.state.value == "offline"


class TestDeviceAdapters:
    """设备适配器测试"""

    @pytest.mark.asyncio
    async def test_switch_adapter(self):
        from synapse.src.device_abstraction.adapters import SwitchAdapter

        switch = SwitchAdapter("switch_1", "测试开关")
        await switch.connect()

        result = await switch.execute("turn_on")
        assert result["success"] is True
        assert result["is_on"] is True

        result = await switch.execute("turn_off")
        assert result["success"] is True
        assert result["is_on"] is False

    @pytest.mark.asyncio
    async def test_light_adapter(self):
        from synapse.src.device_abstraction.adapters import LightAdapter

        light = LightAdapter("light_1", "测试灯")
        await light.connect()

        result = await light.write("brightness", 50)
        assert result is True

        data = await light.read()
        assert data["brightness"] == 50


# ============ 场景模块测试 ============

class TestSceneEngine:
    """场景引擎测试"""

    @pytest.fixture
    def engine(self):
        from synapse.src.scene_engine import SceneEngine
        return SceneEngine()

    @pytest.fixture
    def sample_scene(self):
        from synapse.src.scene_engine import Scene, Trigger, TriggerType, Action, ActionType

        return Scene(
            scene_id="test_scene",
            name="测试场景",
            triggers=[Trigger(trigger_type=TriggerType.MANUAL)],
            actions=[Action(action_type=ActionType.DELAY, config={"seconds": 0.1})]
        )

    @pytest.mark.asyncio
    async def test_register_scene(self, engine, sample_scene):
        result = await engine.register_scene(sample_scene)
        assert result is True

    @pytest.mark.asyncio
    async def test_trigger_scene(self, engine, sample_scene):
        await engine.register_scene(sample_scene)
        await engine.start()

        execution_id = await engine.trigger_scene(sample_scene.scene_id)
        assert execution_id is not None

        await engine.stop()


class TestHope:
    """Hope 模块测试"""

    @pytest.fixture
    def hope(self):
        from synapse.src.scene_engine.hope import HopeModule
        return HopeModule()

    @pytest.mark.asyncio
    async def test_remember_recall(self, hope):
        await hope.initialize()

        await hope.remember("test_key", "test_value")
        result = await hope.recall("test_key")

        assert result == "test_value"

    @pytest.mark.asyncio
    async def test_learn(self, hope):
        await hope.initialize()

        await hope.learn(
            "device_data",
            {"device_id": "sensor_1", "type": "temperature"},
            {"action": "log"}
        )

        # 学习后应该能预测
        prediction = await hope.predict({"device_id": "sensor_1", "type": "temperature"})
        # 预测可能为 None（置信度不够）或有值


# ============ 多租户测试 ============

class TestTenancy:
    """多租户系统测试"""

    @pytest.fixture
    def manager(self):
        from synapse.src.tenancy import TenantManager
        return TenantManager()

    @pytest.mark.asyncio
    async def test_create_tenant(self, manager):
        from synapse.src.tenancy import PlanType

        tenant = await manager.create_tenant("测试租户", PlanType.PRO)
        assert tenant is not None
        assert tenant.name == "测试租户"

    @pytest.mark.asyncio
    async def test_add_user(self, manager):
        from synapse.src.tenancy import PlanType

        tenant = await manager.create_tenant("测试租户")
        user = await manager.add_user(
            tenant.tenant_id,
            "testuser",
            "test@example.com"
        )

        assert user is not None
        assert user.username == "testuser"


class TestPermissions:
    """权限测试"""

    @pytest.fixture
    def manager(self):
        from synapse.src.tenancy import PermissionManager
        return PermissionManager()

    def test_admin_permission(self, manager):
        from synapse.src.tenancy import User

        admin = User(user_id="admin", tenant_id="t1", username="admin", role="admin")
        assert manager.check_permission(admin, "devices", "read") is True
        assert manager.check_permission(admin, "devices", "write") is True

    def test_normal_user_permission(self, manager):
        from synapse.src.tenancy import User

        user = User(user_id="user", tenant_id="t1", username="user", role="user")
        assert manager.check_permission(user, "devices", "read") is True
        assert manager.check_permission(user, "devices", "write") is False


# ============ AI 模块测试 ============

class TestAIModule:
    """AI 模块测试"""

    def test_llm_manager(self):
        from synapse.src.ai import LLMManager, LLMConfig, LLMProvider

        manager = LLMManager()
        assert manager is not None

    def test_agent_manager(self):
        from synapse.src.ai.agent import AgentManager, AgentConfig, AgentRole

        manager = AgentManager()
        config = AgentConfig(
            name="test_agent",
            role=AgentRole.ASSISTANT
        )

        agent = manager.create_agent(config)
        assert agent is not None


# ============ 边缘计算测试 ============

class TestEdgeComputing:
    """边缘计算测试"""

    @pytest.mark.asyncio
    async def test_edge_cloud_router(self):
        from synapse.src.edge.inference import (
            EdgeCloudRouter, InferenceRequest, InferenceLocation
        )

        router = EdgeCloudRouter()

        request = InferenceRequest(
            request_id="test_1",
            model="test_model",
            input_data={"test": "data"},
            privacy_level="high"
        )

        location = router.route(request)
        assert location == InferenceLocation.EDGE


class TestTransaction:
    """事务测试"""

    @pytest.mark.asyncio
    async def test_transaction_commit(self):
        from synapse.src.scene_engine.transaction import TransactionManager

        manager = TransactionManager()
        tx = manager.begin_transaction()

        executed = []

        async def action1():
            executed.append(1)
            return True

        async def action2():
            executed.append(2)
            return True

        tx.add_action(action1)
        tx.add_action(action2)

        result = await tx.execute()
        assert result is True
        assert executed == [1, 2]

    @pytest.mark.asyncio
    async def test_transaction_rollback(self):
        from synapse.src.scene_engine.transaction import TransactionManager, TransactionState

        manager = TransactionManager()
        tx = manager.begin_transaction()

        executed = []
        rolled_back = []

        async def action1():
            executed.append(1)
            return True

        async def action2():
            executed.append(2)
            raise Exception("失败")

        async def rollback1(snapshot):
            rolled_back.append(1)

        tx.add_action(action1, rollback1)
        tx.add_action(action2)

        result = await tx.execute()
        assert result is False
        assert tx.state == TransactionState.ABORTED


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
