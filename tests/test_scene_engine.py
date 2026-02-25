"""
场景引擎测试
"""

import pytest
import asyncio
from synapse.src.scene_engine import (
    SceneEngine, Scene, Trigger, TriggerType,
    Action, ActionType, Condition, SceneState
)
from synapse.src.scene_engine.hope import HopeModule


class TestSceneEngine:
    """场景引擎测试"""

    @pytest.fixture
    def engine(self):
        return SceneEngine()

    @pytest.fixture
    def sample_scene(self):
        return Scene(
            scene_id="test_scene_1",
            name="测试场景",
            description="用于测试的场景",
            triggers=[
                Trigger(trigger_type=TriggerType.MANUAL)
            ],
            actions=[
                Action(action_type=ActionType.DELAY, config={"seconds": 0.1})
            ]
        )

    @pytest.mark.asyncio
    async def test_register_scene(self, engine, sample_scene):
        """测试注册场景"""
        result = await engine.register_scene(sample_scene)
        assert result is True
        assert sample_scene.scene_id in [s.scene_id for s in engine.list_scenes()]

    @pytest.mark.asyncio
    async def test_trigger_scene(self, engine, sample_scene):
        """测试触发场景"""
        await engine.register_scene(sample_scene)
        await engine.start()

        execution_id = await engine.trigger_scene(sample_scene.scene_id)
        assert execution_id is not None

        await engine.stop()

    @pytest.mark.asyncio
    async def test_unregister_scene(self, engine, sample_scene):
        """测试注销场景"""
        await engine.register_scene(sample_scene)
        result = await engine.unregister_scene(sample_scene.scene_id)
        assert result is True

    @pytest.mark.asyncio
    async def test_list_scenes(self, engine, sample_scene):
        """测试列出场景"""
        await engine.register_scene(sample_scene)
        scenes = engine.list_scenes()
        assert len(scenes) == 1


class TestAction:
    """动作测试"""

    def test_action_creation(self):
        """测试创建动作"""
        action = Action(
            action_type=ActionType.DELAY,
            config={"seconds": 1}
        )
        assert action.action_type == ActionType.DELAY

    @pytest.mark.asyncio
    async def test_delay_action(self):
        """测试延时动作"""
        action = Action(
            action_type=ActionType.DELAY,
            config={"seconds": 0.1}
        )
        result = await action.execute({})
        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_notify_action(self):
        """测试通知动作"""
        action = Action(
            action_type=ActionType.NOTIFY,
            config={"message": "测试消息"}
        )
        result = await action.execute({})
        assert result["success"] is True


class TestCondition:
    """条件测试"""

    def test_eq_condition(self):
        """测试等于条件"""
        condition = Condition(field="value", operator="eq", value=10)
        assert condition.evaluate({"value": 10}) is True
        assert condition.evaluate({"value": 20}) is False

    def test_gt_condition(self):
        """测试大于条件"""
        condition = Condition(field="temp", operator="gt", value=25)
        assert condition.evaluate({"temp": 30}) is True
        assert condition.evaluate({"temp": 20}) is False

    def test_contains_condition(self):
        """测试包含条件"""
        condition = Condition(field="tags", operator="contains", value="important")
        assert condition.evaluate({"tags": ["important", "urgent"]}) is True
        assert condition.evaluate({"tags": ["normal"]}) is False


class TestHopeModule:
    """Hope 持续学习模块测试"""

    @pytest.fixture
    def hope(self):
        return HopeModule()

    @pytest.mark.asyncio
    async def test_initialize(self, hope):
        """测试初始化"""
        await hope.initialize()
        # 应该不会抛出异常

    @pytest.mark.asyncio
    async def test_remember_recall(self, hope):
        """测试记忆和回忆"""
        await hope.initialize()

        await hope.remember("test_key", "test_value")
        result = await hope.recall("test_key")

        assert result == "test_value"

    @pytest.mark.asyncio
    async def test_learn(self, hope):
        """测试学习"""
        await hope.initialize()

        # 学习一个事件
        await hope.learn(
            "device_data",
            {"device_id": "sensor_1", "type": "temperature"},
            {"action": "log"}
        )

        # 预测
        prediction = await hope.predict({"device_id": "sensor_1", "type": "temperature"})
        # 预测可能为 None（置信度不够）或有值


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
