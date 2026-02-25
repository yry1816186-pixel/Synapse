"""
设备抽象层 - 统一的设备接口
"""

from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import asyncio
import logging
from abc import ABC, abstractmethod
import uuid

logger = logging.getLogger(__name__)


class DeviceState(Enum):
    """设备状态"""
    OFFLINE = "offline"
    ONLINE = "online"
    BUSY = "busy"
    ERROR = "error"
    MAINTENANCE = "maintenance"


class DeviceType(Enum):
    """设备类型"""
    SENSOR = "sensor"
    ACTUATOR = "actuator"
    CAMERA = "camera"
    SPEAKER = "speaker"
    LIGHT = "light"
    SWITCH = "switch"
    THERMOSTAT = "thermostat"
    LOCK = "lock"
    ROBOT = "robot"
    DRONE = "drone"
    GATEWAY = "gateway"
    CUSTOM = "custom"


@dataclass
class DeviceCapability:
    """设备能力"""
    name: str
    type: str  # "sensor", "action", "config"
    schema: Dict[str, Any] = field(default_factory=dict)
    description: str = ""


@dataclass
class DeviceInfo:
    """设备信息"""
    device_id: str
    name: str
    device_type: DeviceType
    manufacturer: str = ""
    model: str = ""
    firmware_version: str = ""
    capabilities: List[DeviceCapability] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DeviceStatus:
    """设备状态"""
    device_id: str
    state: DeviceState
    last_seen: datetime = field(default_factory=datetime.now)
    battery_level: Optional[float] = None
    signal_strength: Optional[int] = None
    error_message: Optional[str] = None
    attributes: Dict[str, Any] = field(default_factory=dict)


class DeviceBase(ABC):
    """设备基类"""

    def __init__(self, device_id: str, name: str, device_type: DeviceType):
        self.device_id = device_id
        self.name = name
        self.device_type = device_type
        self._state = DeviceState.OFFLINE
        self._status: Optional[DeviceStatus] = None
        self._callbacks: List[Callable] = []

    @abstractmethod
    async def connect(self) -> bool:
        """连接设备"""
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """断开设备"""
        pass

    @abstractmethod
    async def read(self, capability: str = None) -> Dict[str, Any]:
        """读取设备数据"""
        pass

    @abstractmethod
    async def write(self, capability: str, value: Any) -> bool:
        """写入设备数据"""
        pass

    @abstractmethod
    async def execute(self, command: str, params: Dict[str, Any] = None) -> Any:
        """执行设备命令"""
        pass

    @property
    def state(self) -> DeviceState:
        """获取设备状态"""
        return self._state

    @property
    def status(self) -> Optional[DeviceStatus]:
        """获取详细状态"""
        return self._status

    def on_state_change(self, callback: Callable) -> None:
        """注册状态变化回调"""
        self._callbacks.append(callback)

    async def _update_state(self, new_state: DeviceState, **kwargs) -> None:
        """更新设备状态"""
        old_state = self._state
        self._state = new_state

        self._status = DeviceStatus(
            device_id=self.device_id,
            state=new_state,
            **kwargs
        )

        for callback in self._callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(self.device_id, old_state, new_state)
                else:
                    callback(self.device_id, old_state, new_state)
            except Exception as e:
                logger.error(f"设备状态回调错误: {e}")

    @property
    def info(self) -> DeviceInfo:
        """获取设备信息"""
        return DeviceInfo(
            device_id=self.device_id,
            name=self.name,
            device_type=self.device_type
        )


class DeviceRegistry:
    """设备注册中心"""

    def __init__(self):
        self._devices: Dict[str, DeviceBase] = {}
        self._type_index: Dict[DeviceType, List[str]] = {}

    async def register(self, device: DeviceBase) -> bool:
        """注册设备"""
        if device.device_id in self._devices:
            logger.warning(f"设备 {device.device_id} 已存在")
            return False

        self._devices[device.device_id] = device

        # 建立类型索引
        if device.device_type not in self._type_index:
            self._type_index[device.device_type] = []
        self._type_index[device.device_type].append(device.device_id)

        logger.info(f"设备已注册: {device.name} [{device.device_id}]")
        return True

    async def unregister(self, device_id: str) -> bool:
        """注销设备"""
        if device_id not in self._devices:
            return False

        device = self._devices[device_id]

        # 断开连接
        await device.disconnect()

        # 移除类型索引
        if device.device_type in self._type_index:
            if device_id in self._type_index[device.device_type]:
                self._type_index[device.device_type].remove(device_id)

        del self._devices[device_id]
        logger.info(f"设备已注销: {device_id}")
        return True

    def get(self, device_id: str) -> Optional[DeviceBase]:
        """获取设备"""
        return self._devices.get(device_id)

    def get_by_type(self, device_type: DeviceType) -> List[DeviceBase]:
        """按类型获取设备"""
        device_ids = self._type_index.get(device_type, [])
        return [self._devices[did] for did in device_ids if did in self._devices]

    def list_all(self) -> List[DeviceBase]:
        """列出所有设备"""
        return list(self._devices.values())

    async def health_check(self) -> Dict[str, DeviceState]:
        """健康检查所有设备"""
        result = {}
        for device_id, device in self._devices.items():
            result[device_id] = device.state
        return result


class VirtualDevice(DeviceBase):
    """虚拟设备 - 用于模拟和测试"""

    def __init__(self, device_id: str, name: str, device_type: DeviceType,
                 initial_state: Dict[str, Any] = None):
        super().__init__(device_id, name, device_type)
        self._data: Dict[str, Any] = initial_state or {}

    async def connect(self) -> bool:
        """连接"""
        await self._update_state(DeviceState.ONLINE)
        return True

    async def disconnect(self) -> None:
        """断开"""
        await self._update_state(DeviceState.OFFLINE)

    async def read(self, capability: str = None) -> Dict[str, Any]:
        """读取"""
        if capability:
            return {capability: self._data.get(capability)}
        return self._data.copy()

    async def write(self, capability: str, value: Any) -> bool:
        """写入"""
        self._data[capability] = value
        return True

    async def execute(self, command: str, params: Dict[str, Any] = None) -> Any:
        """执行命令"""
        logger.info(f"虚拟设备 {self.name} 执行命令: {command}")
        return {"success": True, "command": command}


# 全局设备注册中心
device_registry = DeviceRegistry()
