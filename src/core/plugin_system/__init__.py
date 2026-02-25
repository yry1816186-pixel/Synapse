"""
插件系统 - 支持动态加载和生命周期管理
"""

from typing import Dict, List, Callable, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import asyncio
import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class HookType(Enum):
    """Hook 类型"""
    # 生命周期 Hooks
    BEFORE_START = "before_start"
    AFTER_START = "after_start"
    BEFORE_STOP = "before_stop"
    AFTER_STOP = "after_stop"

    # 设备 Hooks
    DEVICE_CONNECT = "device_connect"
    DEVICE_DISCONNECT = "device_disconnect"
    DEVICE_DATA = "device_data"
    DEVICE_COMMAND = "device_command"

    # 场景 Hooks
    SCENE_TRIGGER = "scene_trigger"
    SCENE_EXECUTE = "scene_execute"
    SCENE_COMPLETE = "scene_complete"
    SCENE_ERROR = "scene_error"

    # 用户 Hooks
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    USER_ACTION = "user_action"

    # 系统 Hooks
    SYSTEM_EVENT = "system_event"
    SCHEDULE_TICK = "schedule_tick"


@dataclass
class HookContext:
    """Hook 上下文"""
    hook_type: HookType
    data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=lambda: asyncio.get_event_loop().time() if asyncio.get_event_loop().is_running() else 0)


class PluginBase(ABC):
    """插件基类"""

    name: str = "base_plugin"
    version: str = "1.0.0"
    description: str = "基础插件"
    author: str = ""
    hooks: List[HookType] = []

    @abstractmethod
    async def initialize(self, context: Dict[str, Any]) -> bool:
        """初始化插件"""
        pass

    @abstractmethod
    async def shutdown(self) -> None:
        """关闭插件"""
        pass

    async def on_hook(self, context: HookContext) -> Optional[Dict[str, Any]]:
        """Hook 回调"""
        return None


class PluginManager:
    """插件管理器"""

    def __init__(self):
        self._plugins: Dict[str, PluginBase] = {}
        self._hooks: Dict[HookType, List[Callable]] = {}
        self._initialized = False

        # 初始化所有 Hook 类型的列表
        for hook_type in HookType:
            self._hooks[hook_type] = []

    async def register_plugin(self, plugin: PluginBase) -> bool:
        """注册插件"""
        if plugin.name in self._plugins:
            logger.warning(f"插件 {plugin.name} 已存在")
            return False

        try:
            if await plugin.initialize({}):
                self._plugins[plugin.name] = plugin

                # 注册插件的 Hooks
                for hook_type in plugin.hooks:
                    self._hooks[hook_type].append(plugin.on_hook)

                logger.info(f"插件 {plugin.name} v{plugin.version} 注册成功")
                return True
            else:
                logger.error(f"插件 {plugin.name} 初始化失败")
                return False
        except Exception as e:
            logger.error(f"注册插件 {plugin.name} 时发生错误: {e}")
            return False

    async def unregister_plugin(self, name: str) -> bool:
        """注销插件"""
        if name not in self._plugins:
            return False

        plugin = self._plugins[name]
        await plugin.shutdown()

        # 移除插件的 Hooks
        for hook_type in plugin.hooks:
            if plugin.on_hook in self._hooks[hook_type]:
                self._hooks[hook_type].remove(plugin.on_hook)

        del self._plugins[name]
        logger.info(f"插件 {name} 已注销")
        return True

    async def emit_hook(self, hook_type: HookType, data: Dict[str, Any] = None,
                        metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """触发 Hook"""
        context = HookContext(
            hook_type=hook_type,
            data=data or {},
            metadata=metadata or {}
        )

        results = []
        for callback in self._hooks[hook_type]:
            try:
                result = await callback(context)
                if result:
                    results.append(result)
            except Exception as e:
                logger.error(f"Hook {hook_type} 执行错误: {e}")

        return results

    def get_plugin(self, name: str) -> Optional[PluginBase]:
        """获取插件"""
        return self._plugins.get(name)

    def list_plugins(self) -> List[str]:
        """列出所有插件"""
        return list(self._plugins.keys())

    async def shutdown_all(self) -> None:
        """关闭所有插件"""
        for name in list(self._plugins.keys()):
            await self.unregister_plugin(name)


# 全局插件管理器实例
plugin_manager = PluginManager()
