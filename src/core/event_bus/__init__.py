"""
事件总线 - 发布-订阅模式
"""

from typing import Dict, List, Callable, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import asyncio
import logging
import json
from collections import defaultdict
import uuid

logger = logging.getLogger(__name__)


class EventType(Enum):
    """事件类型"""
    # 设备事件
    DEVICE_CONNECTED = "device.connected"
    DEVICE_DISCONNECTED = "device.disconnected"
    DEVICE_DATA = "device.data"
    DEVICE_STATUS = "device.status"
    DEVICE_ERROR = "device.error"

    # 场景事件
    SCENE_TRIGGERED = "scene.triggered"
    SCENE_STARTED = "scene.started"
    SCENE_COMPLETED = "scene.completed"
    SCENE_FAILED = "scene.failed"

    # 用户事件
    USER_LOGIN = "user.login"
    USER_LOGOUT = "user.logout"
    USER_COMMAND = "user.command"

    # 系统事件
    SYSTEM_START = "system.start"
    SYSTEM_STOP = "system.stop"
    SYSTEM_ERROR = "system.error"
    SYSTEM_HEALTH = "system.health"

    # 告警事件
    ALERT_TRIGGERED = "alert.triggered"
    ALERT_CLEARED = "alert.cleared"

    # 租户事件
    TENANT_CREATED = "tenant.created"
    TENANT_DELETED = "tenant.deleted"


@dataclass
class Event:
    """事件对象"""
    event_type: EventType
    source: str
    data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "source": self.source,
            "data": self.data,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat()
        }

    def to_json(self) -> str:
        """转换为 JSON"""
        return json.dumps(self.to_dict())


class EventBus:
    """事件总线"""

    def __init__(self):
        self._subscribers: Dict[EventType, List[Callable]] = defaultdict(list)
        self._wildcard_subscribers: List[Callable] = []
        self._event_queue: asyncio.Queue = None
        self._running = False
        self._middleware: List[Callable] = []

    async def start(self) -> None:
        """启动事件总线"""
        self._event_queue = asyncio.Queue()
        self._running = True
        asyncio.create_task(self._process_events())
        logger.info("事件总线已启动")

    async def stop(self) -> None:
        """停止事件总线"""
        self._running = False
        if self._event_queue:
            await self._event_queue.put(None)  # 发送停止信号
        logger.info("事件总线已停止")

    def subscribe(self, event_type: EventType, callback: Callable) -> None:
        """订阅事件"""
        self._subscribers[event_type].append(callback)
        logger.debug(f"订阅事件: {event_type.value}")

    def subscribe_all(self, callback: Callable) -> None:
        """订阅所有事件"""
        self._wildcard_subscribers.append(callback)

    def unsubscribe(self, event_type: EventType, callback: Callable) -> None:
        """取消订阅"""
        if callback in self._subscribers[event_type]:
            self._subscribers[event_type].remove(callback)

    def add_middleware(self, middleware: Callable) -> None:
        """添加中间件"""
        self._middleware.append(middleware)

    async def publish(self, event: Event) -> None:
        """发布事件"""
        if not self._running:
            logger.warning("事件总线未运行，事件被丢弃")
            return

        # 执行中间件
        for middleware in self._middleware:
            try:
                event = await middleware(event)
                if event is None:
                    return  # 中间件阻止了事件
            except Exception as e:
                logger.error(f"中间件执行错误: {e}")

        await self._event_queue.put(event)

    async def emit(self, event_type: EventType, source: str,
                   data: Dict[str, Any] = None,
                   metadata: Dict[str, Any] = None) -> str:
        """便捷方法：发布事件"""
        event = Event(
            event_type=event_type,
            source=source,
            data=data or {},
            metadata=metadata or {}
        )
        await self.publish(event)
        return event.event_id

    async def _process_events(self) -> None:
        """处理事件队列"""
        while self._running:
            try:
                event = await self._event_queue.get()

                if event is None:
                    break

                await self._dispatch_event(event)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"处理事件时发生错误: {e}")

    async def _dispatch_event(self, event: Event) -> None:
        """分发事件到订阅者"""
        # 分发到特定订阅者
        callbacks = self._subscribers.get(event.event_type, [])

        for callback in callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(event)
                else:
                    callback(event)
            except Exception as e:
                logger.error(f"事件回调执行错误: {e}")

        # 分发到通配订阅者
        for callback in self._wildcard_subscribers:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(event)
                else:
                    callback(event)
            except Exception as e:
                logger.error(f"通配回调执行错误: {e}")


# 全局事件总线实例
event_bus = EventBus()
