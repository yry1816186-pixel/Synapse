"""
场景引擎 - 智能场景执行
"""

from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import asyncio
import logging
import json
from abc import ABC, abstractmethod
import uuid

logger = logging.getLogger(__name__)


class SceneState(Enum):
    """场景状态"""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


class TriggerType(Enum):
    """触发器类型"""
    DEVICE = "device"  # 设备状态变化
    TIME = "time"  # 定时触发
    SCHEDULE = "schedule"  # 调度触发
    EVENT = "event"  # 事件触发
    MANUAL = "manual"  # 手动触发
    CONDITION = "condition"  # 条件满足
    LOCATION = "location"  # 位置触发
    VOICE = "voice"  # 语音触发


class ActionType(Enum):
    """动作类型"""
    DEVICE_CONTROL = "device_control"  # 设备控制
    SCENE = "scene"  # 执行子场景
    NOTIFY = "notify"  # 通知
    HTTP = "http"  # HTTP 请求
    DELAY = "delay"  # 延时
    CONDITION = "condition"  # 条件分支
    LOOP = "loop"  # 循环
    SCRIPT = "script"  # 脚本执行


@dataclass
class Trigger:
    """触发器"""
    trigger_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    trigger_type: TriggerType = TriggerType.MANUAL
    config: Dict[str, Any] = field(default_factory=dict)
    enabled: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "trigger_id": self.trigger_id,
            "trigger_type": self.trigger_type.value,
            "config": self.config,
            "enabled": self.enabled
        }


@dataclass
class Condition:
    """条件"""
    field: str
    operator: str  # eq, ne, gt, lt, gte, lte, contains, matches
    value: Any

    def evaluate(self, context: Dict[str, Any]) -> bool:
        """评估条件"""
        actual = context.get(self.field)
        if actual is None:
            return False

        ops = {
            "eq": lambda a, b: a == b,
            "ne": lambda a, b: a != b,
            "gt": lambda a, b: a > b,
            "lt": lambda a, b: a < b,
            "gte": lambda a, b: a >= b,
            "lte": lambda a, b: a <= b,
            "contains": lambda a, b: b in a if hasattr(a, '__contains__') else False,
            "matches": lambda a, b: bool(__import__('re').match(b, str(a)))
        }

        op_func = ops.get(self.operator)
        if op_func is None:
            return False

        try:
            return op_func(actual, self.value)
        except Exception:
            return False


@dataclass
class Action:
    """动作"""
    action_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    action_type: ActionType = ActionType.DEVICE_CONTROL
    config: Dict[str, Any] = field(default_factory=dict)
    conditions: List[Condition] = field(default_factory=list)
    on_success: Optional[str] = None  # 下一个动作 ID
    on_failure: Optional[str] = None
    timeout: int = 30  # 秒
    retry_count: int = 0

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """执行动作"""
        # 检查条件
        for condition in self.conditions:
            if not condition.evaluate(context):
                return {"success": False, "reason": "条件不满足"}

        # 根据类型执行
        try:
            if self.action_type == ActionType.DELAY:
                delay = self.config.get("seconds", 1)
                await asyncio.sleep(delay)
                return {"success": True}

            elif self.action_type == ActionType.NOTIFY:
                message = self.config.get("message", "")
                logger.info(f"通知: {message}")
                return {"success": True, "message": message}

            elif self.action_type == ActionType.DEVICE_CONTROL:
                device_id = self.config.get("device_id")
                command = self.config.get("command")
                params = self.config.get("params", {})
                logger.info(f"设备控制: {device_id} -> {command}")
                return {"success": True, "device_id": device_id, "command": command}

            else:
                logger.warning(f"未实现的动作类型: {self.action_type}")
                return {"success": False, "reason": "未实现的动作类型"}

        except asyncio.TimeoutError:
            return {"success": False, "reason": "超时"}
        except Exception as e:
            return {"success": False, "reason": str(e)}


@dataclass
class Scene:
    """场景定义"""
    scene_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    description: str = ""
    triggers: List[Trigger] = field(default_factory=list)
    actions: List[Action] = field(default_factory=list)
    enabled: bool = True
    priority: int = 5
    tenant_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "scene_id": self.scene_id,
            "name": self.name,
            "description": self.description,
            "enabled": self.enabled,
            "priority": self.priority,
            "triggers": [t.to_dict() for t in self.triggers],
            "actions_count": len(self.actions)
        }


class SceneEngine:
    """场景引擎"""

    def __init__(self):
        self._scenes: Dict[str, Scene] = {}
        self._running_scenes: Dict[str, asyncio.Task] = {}
        self._trigger_handlers: Dict[TriggerType, List[Callable]] = {}
        self._state = SceneState.IDLE
        self._context: Dict[str, Any] = {}

    async def register_scene(self, scene: Scene) -> bool:
        """注册场景"""
        if scene.scene_id in self._scenes:
            logger.warning(f"场景 {scene.scene_id} 已存在")
            return False

        self._scenes[scene.scene_id] = scene
        logger.info(f"场景已注册: {scene.name} [{scene.scene_id}]")
        return True

    async def unregister_scene(self, scene_id: str) -> bool:
        """注销场景"""
        if scene_id not in self._scenes:
            return False

        # 停止正在执行的场景
        if scene_id in self._running_scenes:
            self._running_scenes[scene_id].cancel()
            del self._running_scenes[scene_id]

        del self._scenes[scene_id]
        logger.info(f"场景已注销: {scene_id}")
        return True

    async def trigger_scene(self, scene_id: str, trigger_type: TriggerType = TriggerType.MANUAL,
                           context: Dict[str, Any] = None) -> str:
        """触发场景执行"""
        if scene_id not in self._scenes:
            raise ValueError(f"场景不存在: {scene_id}")

        scene = self._scenes[scene_id]

        if not scene.enabled:
            raise ValueError(f"场景已禁用: {scene_id}")

        # 创建执行任务
        execution_id = f"{scene_id}_{uuid.uuid4().hex[:8]}"
        task = asyncio.create_task(self._execute_scene(scene, context or {}))
        self._running_scenes[execution_id] = task

        logger.info(f"场景已触发: {scene.name} [{execution_id}]")
        return execution_id

    async def _execute_scene(self, scene: Scene, context: Dict[str, Any]) -> Dict[str, Any]:
        """执行场景"""
        start_time = datetime.now()
        results = []

        try:
            for action in scene.actions:
                result = await action.execute(context)
                results.append({
                    "action_id": action.action_id,
                    "result": result
                })

                if not result.get("success"):
                    logger.warning(f"动作执行失败: {action.action_id}")
                    if action.on_failure:
                        # 处理失败情况
                        pass
                    break

                if action.on_success:
                    # 继续执行下一个动作
                    pass

            duration = (datetime.now() - start_time).total_seconds()
            logger.info(f"场景执行完成: {scene.name} (耗时: {duration:.2f}s)")

            return {
                "success": True,
                "scene_id": scene.scene_id,
                "duration": duration,
                "results": results
            }

        except asyncio.CancelledError:
            logger.info(f"场景执行被取消: {scene.name}")
            return {"success": False, "reason": "cancelled"}
        except Exception as e:
            logger.error(f"场景执行错误: {e}")
            return {"success": False, "reason": str(e)}

    def get_scene(self, scene_id: str) -> Optional[Scene]:
        """获取场景"""
        return self._scenes.get(scene_id)

    def list_scenes(self) -> List[Scene]:
        """列出所有场景"""
        return list(self._scenes.values())

    async def start(self) -> None:
        """启动场景引擎"""
        self._state = SceneState.RUNNING
        logger.info("场景引擎已启动")

    async def stop(self) -> None:
        """停止场景引擎"""
        self._state = SceneState.IDLE

        # 取消所有正在执行的场景
        for execution_id, task in self._running_scenes.items():
            task.cancel()

        self._running_scenes.clear()
        logger.info("场景引擎已停止")


# 全局场景引擎实例
scene_engine = SceneEngine()
