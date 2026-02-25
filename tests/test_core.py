"""
核心模块测试
"""

import pytest
import asyncio
from synapse.src.core.plugin_system import (
    PluginManager, PluginBase, HookType, HookContext
)
from synapse.src.core.event_bus import EventBus, Event, EventType
from synapse.src.core.config import ConfigManager
from synapse.src.core.scheduler import TaskScheduler, TaskPriority


class TestPluginSystem:
    """插件系统测试"""

    @pytest.fixture
    def manager(self):
        return PluginManager()

    @pytest.mark.asyncio
    async def test_register_plugin(self, manager):
        """测试注册插件"""
        class TestPlugin(PluginBase):
            name = "test_plugin"
            hooks = [HookType.SYSTEM_EVENT]

            async def initialize(self, context):
                return True

            async def shutdown(self):
                pass

        plugin = TestPlugin()
        result = await manager.register_plugin(plugin)
        assert result is True
        assert "test_plugin" in manager.list_plugins()


class TestEventBus:
    """事件总线测试"""

    @pytest.fixture
    def bus(self):
        return EventBus()

    @pytest.mark.asyncio
    async def test_subscribe_and_publish(self, bus):
        """测试订阅和发布"""
        received = []

        async def callback(event):
            received.append(event)

        bus.subscribe(EventType.SYSTEM_START, callback)
        await bus.start()

        event = Event(
            event_type=EventType.SYSTEM_START,
            source="test"
        )
        await bus.publish(event)

        await asyncio.sleep(0.1)
        assert len(received) == 1

        await bus.stop()


class TestScheduler:
    """调度器测试"""

    @pytest.fixture
    def scheduler(self):
        return TaskScheduler()

    def test_priority_order(self):
        """测试优先级顺序"""
        assert TaskPriority.LOW.value < TaskPriority.NORMAL.value
        assert TaskPriority.NORMAL.value < TaskPriority.HIGH.value
        assert TaskPriority.HIGH.value < TaskPriority.CRITICAL.value


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
