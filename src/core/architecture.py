"""
Synapse 核心架构模块

基于 Home Assistant、OpenHAB、Node-RED、EdgeX、KubeEdge、EMQX 的设计模式
实现：分层架构、插件系统、消息总线、设备抽象
"""

from typing import Dict, Any, Optional, List, Callable, Type
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import asyncio
import logging
import inspect

logger = logging.getLogger(__name__)


# ============================================================================
# 1. 设备抽象层 (参考 Home Assistant Entity, OpenHAB Thing)
# ============================================================================

class DeviceState(Enum):
    """设备状态"""
    UNKNOWN = "unknown"
    ONLINE = "online"
    OFFLINE = "offline"
    UNAVAILABLE = "unavailable"
    ERROR = "error"


@dataclass
class DeviceProperty:
    """设备属性"""
    name: str
    value: Any
    unit: Optional[str] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    readonly: bool = False
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class DeviceCapability:
    """设备能力"""
    name: str
    actions: List[str] = field(default_factory=list)
    properties: List[str] = field(default_factory=list)


class BaseDevice:
    """
    设备基类 - 统一设备抽象
    
    参考:
    - Home Assistant: Entity
    - OpenHAB: Thing
    - EdgeX: Device
    """
    
    def __init__(self, device_id: str, name: str, device_type: str = "generic"):
        self.device_id = device_id
        self.name = name
        self.device_type = device_type
        self.state = DeviceState.UNKNOWN
        self.properties: Dict[str, DeviceProperty] = {}
        self.capabilities: List[DeviceCapability] = []
        self._callbacks: List[Callable] = []
        self._last_seen: Optional[datetime] = None
    
    async def initialize(self) -> bool:
        """初始化设备"""
        self.state = DeviceState.ONLINE
        self._last_seen = datetime.now()
        logger.info(f"设备初始化: {self.device_id}")
        return True
    
    async def connect(self) -> bool:
        """连接设备"""
        raise NotImplementedError
    
    async def disconnect(self) -> None:
        """断开设备"""
        self.state = DeviceState.OFFLINE
        logger.info(f"设备断开: {self.device_id}")
    
    def get_property(self, name: str) -> Optional[DeviceProperty]:
        """获取属性"""
        return self.properties.get(name)
    
    def set_property(self, name: str, value: Any) -> bool:
        """设置属性"""
        if name in self.properties:
            prop = self.properties[name]
            if not prop.readonly:
                prop.value = value
                prop.last_updated = datetime.now()
                self._notify_callbacks(name, value)
                return True
        return False
    
    def add_callback(self, callback: Callable) -> None:
        """添加状态变化回调"""
        self._callbacks.append(callback)
    
    def _notify_callbacks(self, property_name: str, value: Any) -> None:
        """通知回调"""
        for callback in self._callbacks:
            try:
                callback(self.device_id, property_name, value)
            except Exception as e:
                logger.error(f"回调执行失败: {e}")
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "device_id": self.device_id,
            "name": self.name,
            "type": self.device_type,
            "state": self.state.value,
            "properties": {
                k: {"value": v.value, "unit": v.unit}
                for k, v in self.properties.items()
            },
            "capabilities": [
                {"name": c.name, "actions": c.actions}
                for c in self.capabilities
            ],
            "last_seen": self._last_seen.isoformat() if self._last_seen else None
        }


class DeviceRegistry:
    """
    设备注册表 - 管理所有设备
    
    参考:
    - Home Assistant: EntityRegistry
    - EdgeX: DeviceService
    """
    
    def __init__(self):
        self._devices: Dict[str, BaseDevice] = {}
        self._device_types: Dict[str, Type[BaseDevice]] = {}
    
    def register_device_type(self, device_type: str, cls: Type[BaseDevice]) -> None:
        """注册设备类型"""
        self._device_types[device_type] = cls
        logger.info(f"注册设备类型: {device_type}")
    
    async def create_device(self, device_id: str, name: str, 
                           device_type: str = "generic") -> Optional[BaseDevice]:
        """创建设备"""
        if device_id in self._devices:
            return self._devices[device_id]
        
        cls = self._device_types.get(device_type, BaseDevice)
        device = cls(device_id=device_id, name=name, device_type=device_type)
        
        if await device.initialize():
            self._devices[device_id] = device
            return device
        
        return None
    
    def get_device(self, device_id: str) -> Optional[BaseDevice]:
        """获取设备"""
        return self._devices.get(device_id)
    
    def get_all_devices(self) -> List[BaseDevice]:
        """获取所有设备"""
        return list(self._devices.values())
    
    async def remove_device(self, device_id: str) -> bool:
        """移除设备"""
        if device_id in self._devices:
            device = self._devices.pop(device_id)
            await device.disconnect()
            return True
        return False
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计"""
        states = {}
        for device in self._devices.values():
            state = device.state.value
            states[state] = states.get(state, 0) + 1
        
        return {
            "total_devices": len(self._devices),
            "device_types": len(self._device_types),
            "states": states
        }


# ============================================================================
# 2. 消息总线 (参考 Home Assistant EventBus, EMQX)
# ============================================================================

@dataclass
class Event:
    """事件"""
    event_type: str
    data: Dict[str, Any]
    source: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)


class EventBus:
    """
    事件总线 - 核心通信机制
    
    参考:
    - Home Assistant: EventBus
    - EMQX: Pub/Sub
    - Node-RED: Flow
    """
    
    def __init__(self):
        self._listeners: Dict[str, List[Callable]] = {}
        self._event_history: List[Event] = []
        self._max_history = 1000
        self._event_count = 0
    
    def subscribe(self, event_type: str, callback: Callable) -> Callable:
        """
        订阅事件
        
        Args:
            event_type: 事件类型
            callback: 回调函数
            
        Returns:
            取消订阅函数
        """
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        
        self._listeners[event_type].append(callback)
        
        def unsubscribe():
            if callback in self._listeners[event_type]:
                self._listeners[event_type].remove(callback)
        
        return unsubscribe
    
    async def publish(self, event_type: str, data: Dict[str, Any], 
                     source: str = None) -> None:
        """
        发布事件
        
        Args:
            event_type: 事件类型
            data: 事件数据
            source: 事件来源
        """
        event = Event(
            event_type=event_type,
            data=data,
            source=source
        )
        
        self._event_count += 1
        self._event_history.append(event)
        
        # 限制历史大小
        if len(self._event_history) > self._max_history:
            self._event_history = self._event_history[-self._max_history:]
        
        # 通知监听者
        listeners = self._listeners.get(event_type, [])
        for callback in listeners:
            try:
                if inspect.iscoroutinefunction(callback):
                    await callback(event)
                else:
                    callback(event)
            except Exception as e:
                logger.error(f"事件处理失败: {event_type} - {e}")
    
    def get_history(self, event_type: str = None, limit: int = 100) -> List[Event]:
        """获取事件历史"""
        if event_type:
            events = [e for e in self._event_history if e.event_type == event_type]
        else:
            events = self._event_history
        
        return events[-limit:]
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计"""
        return {
            "total_events": self._event_count,
            "event_types": list(self._listeners.keys()),
            "listeners": {
                k: len(v) for k, v in self._listeners.items()
            },
            "history_size": len(self._event_history)
        }


# ============================================================================
# 3. 插件系统 (参考 Home Assistant Integration, OpenHAB Binding)
# ============================================================================

@dataclass
class PluginInfo:
    """插件信息"""
    plugin_id: str
    name: str
    version: str
    description: str = ""
    author: str = ""
    dependencies: List[str] = field(default_factory=list)


class BasePlugin:
    """
    插件基类
    
    参考:
    - Home Assistant: Integration
    - OpenHAB: Binding
    - Node-RED: Node
    """
    
    def __init__(self, plugin_id: str, name: str, version: str = "1.0.0"):
        self.info = PluginInfo(
            plugin_id=plugin_id,
            name=name,
            version=version
        )
        self._enabled = False
        self._event_bus: Optional[EventBus] = None
        self._device_registry: Optional[DeviceRegistry] = None
    
    async def setup(self, event_bus: EventBus, device_registry: DeviceRegistry) -> bool:
        """
        设置插件
        
        Args:
            event_bus: 事件总线
            device_registry: 设备注册表
            
        Returns:
            是否成功
        """
        self._event_bus = event_bus
        self._device_registry = device_registry
        logger.info(f"插件设置: {self.info.plugin_id}")
        return True
    
    async def enable(self) -> bool:
        """启用插件"""
        self._enabled = True
        logger.info(f"插件启用: {self.info.plugin_id}")
        return True
    
    async def disable(self) -> None:
        """禁用插件"""
        self._enabled = False
        logger.info(f"插件禁用: {self.info.plugin_id}")
    
    @property
    def is_enabled(self) -> bool:
        """是否启用"""
        return self._enabled


class PluginManager:
    """
    插件管理器
    
    参考:
    - Home Assistant: Integration Setup
    - OpenHAB: AddonManager
    """
    
    def __init__(self):
        self._plugins: Dict[str, BasePlugin] = {}
        self._plugin_classes: Dict[str, Type[BasePlugin]] = {}
        self._event_bus: Optional[EventBus] = None
        self._device_registry: Optional[DeviceRegistry] = None
    
    def set_dependencies(self, event_bus: EventBus, device_registry: DeviceRegistry) -> None:
        """设置依赖"""
        self._event_bus = event_bus
        self._device_registry = device_registry
    
    def register_plugin_class(self, plugin_id: str, cls: Type[BasePlugin]) -> None:
        """注册插件类"""
        self._plugin_classes[plugin_id] = cls
        logger.info(f"注册插件类: {plugin_id}")
    
    async def load_plugin(self, plugin_id: str, config: Dict[str, Any] = None) -> Optional[BasePlugin]:
        """加载插件"""
        if plugin_id in self._plugins:
            return self._plugins[plugin_id]
        
        cls = self._plugin_classes.get(plugin_id)
        if not cls:
            logger.error(f"未找到插件类: {plugin_id}")
            return None
        
        # 实例化
        plugin = cls()
        
        # 设置
        if self._event_bus and self._device_registry:
            await plugin.setup(self._event_bus, self._device_registry)
        
        # 启用
        if await plugin.enable():
            self._plugins[plugin_id] = plugin
            return plugin
        
        return None
    
    async def unload_plugin(self, plugin_id: str) -> bool:
        """卸载插件"""
        if plugin_id in self._plugins:
            plugin = self._plugins.pop(plugin_id)
            await plugin.disable()
            return True
        return False
    
    def get_plugin(self, plugin_id: str) -> Optional[BasePlugin]:
        """获取插件"""
        return self._plugins.get(plugin_id)
    
    def get_all_plugins(self) -> List[BasePlugin]:
        """获取所有插件"""
        return list(self._plugins.values())
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计"""
        return {
            "total_plugins": len(self._plugins),
            "enabled_plugins": sum(1 for p in self._plugins.values() if p.is_enabled),
            "available_classes": list(self._plugin_classes.keys())
        }


# ============================================================================
# 4. 规则引擎 (参考 Node-RED Flow, Home Assistant Automation)
# ============================================================================

@dataclass
class RuleCondition:
    """规则条件"""
    field: str
    operator: str  # eq, ne, gt, lt, gte, lte, contains
    value: Any


@dataclass
class RuleAction:
    """规则动作"""
    action_type: str  # publish, call, set_property
    target: str
    params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Rule:
    """规则"""
    rule_id: str
    name: str
    trigger_event: str
    conditions: List[RuleCondition] = field(default_factory=list)
    actions: List[RuleAction] = field(default_factory=list)
    enabled: bool = True
    priority: int = 0
    trigger_count: int = 0


class RuleEngine:
    """
    规则引擎
    
    参考:
    - Node-RED: Flow
    - Home Assistant: Automation
    - OpenHAB: Rule
    """
    
    def __init__(self):
        self._rules: Dict[str, Rule] = {}
        self._event_bus: Optional[EventBus] = None
        self._unsubscribe: Optional[Callable] = None
        self._action_handlers: Dict[str, Callable] = {}
    
    def set_event_bus(self, event_bus: EventBus) -> None:
        """设置事件总线"""
        self._event_bus = event_bus
    
    def register_action_handler(self, action_type: str, handler: Callable) -> None:
        """注册动作处理器"""
        self._action_handlers[action_type] = handler
    
    def add_rule(self, rule: Rule) -> None:
        """添加规则"""
        self._rules[rule.rule_id] = rule
        logger.info(f"添加规则: {rule.name}")
    
    def remove_rule(self, rule_id: str) -> bool:
        """移除规则"""
        if rule_id in self._rules:
            del self._rules[rule_id]
            return True
        return False
    
    async def start(self) -> None:
        """启动规则引擎"""
        if self._event_bus:
            # 订阅所有事件
            self._unsubscribe = self._event_bus.subscribe(
                "*",  # 通配符
                self._handle_event
            )
            logger.info("规则引擎启动")
    
    async def stop(self) -> None:
        """停止规则引擎"""
        if self._unsubscribe:
            self._unsubscribe()
        logger.info("规则引擎停止")
    
    async def _handle_event(self, event: Event) -> None:
        """处理事件"""
        for rule in sorted(self._rules.values(), key=lambda r: r.priority):
            if not rule.enabled:
                continue
            
            if event.event_type != rule.trigger_event:
                continue
            
            # 检查条件
            if self._check_conditions(event, rule.conditions):
                # 执行动作
                await self._execute_actions(rule.actions, event)
                rule.trigger_count += 1
    
    def _check_conditions(self, event: Event, conditions: List[RuleCondition]) -> bool:
        """检查条件"""
        for cond in conditions:
            value = event.data.get(cond.field)
            
            if cond.operator == "eq" and value != cond.value:
                return False
            elif cond.operator == "ne" and value == cond.value:
                return False
            elif cond.operator == "gt" and not (value > cond.value):
                return False
            elif cond.operator == "lt" and not (value < cond.value):
                return False
            elif cond.operator == "gte" and not (value >= cond.value):
                return False
            elif cond.operator == "lte" and not (value <= cond.value):
                return False
            elif cond.operator == "contains" and cond.value not in str(value):
                return False
        
        return True
    
    async def _execute_actions(self, actions: List[RuleAction], event: Event) -> None:
        """执行动作"""
        for action in actions:
            handler = self._action_handlers.get(action.action_type)
            if handler:
                try:
                    if inspect.iscoroutinefunction(handler):
                        await handler(action.target, action.params, event)
                    else:
                        handler(action.target, action.params, event)
                except Exception as e:
                    logger.error(f"动作执行失败: {action.action_type} - {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计"""
        return {
            "total_rules": len(self._rules),
            "enabled_rules": sum(1 for r in self._rules.values() if r.enabled),
            "total_triggers": sum(r.trigger_count for r in self._rules.values())
        }


# ============================================================================
# 5. 分层架构 - 服务层
# ============================================================================

class SynapseCore:
    """
    Synapse 核心 - 整合所有模块
    
    分层架构:
    - Gateway Layer: API/WebSocket
    - Core Layer: DeviceRegistry, EventBus, RuleEngine
    - Data Layer: Storage, Cache
    """
    
    def __init__(self):
        # 核心组件
        self.event_bus = EventBus()
        self.device_registry = DeviceRegistry()
        self.plugin_manager = PluginManager()
        self.rule_engine = RuleEngine()
        
        # 设置依赖
        self.plugin_manager.set_dependencies(self.event_bus, self.device_registry)
        self.rule_engine.set_event_bus(self.event_bus)
        
        # 注册默认动作处理器
        self._setup_default_handlers()
        
        self._initialized = False
    
    def _setup_default_handlers(self) -> None:
        """设置默认处理器"""
        async def publish_handler(target: str, params: Dict, event: Event) -> None:
            await self.event_bus.publish(target, params)
        
        self.rule_engine.register_action_handler("publish", publish_handler)
    
    async def initialize(self) -> None:
        """初始化核心"""
        logger.info("=== Synapse Core 初始化 ===")
        
        # 启动规则引擎
        await self.rule_engine.start()
        
        self._initialized = True
        logger.info("=== Synapse Core 初始化完成 ===")
    
    async def shutdown(self) -> None:
        """关闭核心"""
        await self.rule_engine.stop()
        
        # 断开所有设备
        for device in self.device_registry.get_all_devices():
            await device.disconnect()
        
        self._initialized = False
        logger.info("Synapse Core 已关闭")
    
    def get_full_stats(self) -> Dict[str, Any]:
        """获取完整统计"""
        return {
            "initialized": self._initialized,
            "devices": self.device_registry.get_stats(),
            "events": self.event_bus.get_stats(),
            "plugins": self.plugin_manager.get_stats(),
            "rules": self.rule_engine.get_stats()
        }


# 全局实例
synapse_core = SynapseCore()
