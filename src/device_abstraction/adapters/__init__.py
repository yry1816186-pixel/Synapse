"""
设备适配器 - 各类设备的具体实现
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
import asyncio
import logging
import json

from .. import DeviceBase, DeviceType, DeviceState

logger = logging.getLogger(__name__)


class SensorAdapter(DeviceBase):
    """传感器适配器"""

    def __init__(self, device_id: str, name: str, sensor_type: str = "generic"):
        super().__init__(device_id, name, DeviceType.SENSOR)
        self.sensor_type = sensor_type
        self._value: Optional[Any] = None
        self._unit: str = ""
        self._last_update: Optional[datetime] = None

    async def connect(self) -> bool:
        await self._update_state(DeviceState.ONLINE)
        return True

    async def disconnect(self) -> None:
        await self._update_state(DeviceState.OFFLINE)

    async def read(self, capability: str = None) -> Dict[str, Any]:
        return {
            "value": self._value,
            "unit": self._unit,
            "sensor_type": self.sensor_type,
            "last_update": self._last_update.isoformat() if self._last_update else None
        }

    async def write(self, capability: str, value: Any) -> bool:
        return False  # 传感器通常只读

    async def execute(self, command: str, params: Dict[str, Any] = None) -> Any:
        if command == "update":
            self._value = params.get("value")
            self._unit = params.get("unit", self._unit)
            self._last_update = datetime.now()
            return {"success": True}
        return {"success": False, "error": "unknown command"}

    async def update_value(self, value: Any, unit: str = None) -> None:
        """更新传感器值"""
        self._value = value
        if unit:
            self._unit = unit
        self._last_update = datetime.now()


class SwitchAdapter(DeviceBase):
    """开关适配器"""

    def __init__(self, device_id: str, name: str):
        super().__init__(device_id, name, DeviceType.SWITCH)
        self._is_on: bool = False

    async def connect(self) -> bool:
        await self._update_state(DeviceState.ONLINE)
        return True

    async def disconnect(self) -> None:
        await self._update_state(DeviceState.OFFLINE)

    async def read(self, capability: str = None) -> Dict[str, Any]:
        return {"is_on": self._is_on}

    async def write(self, capability: str, value: Any) -> bool:
        if capability == "state":
            self._is_on = bool(value)
            return True
        return False

    async def execute(self, command: str, params: Dict[str, Any] = None) -> Any:
        if command == "turn_on":
            self._is_on = True
            return {"success": True, "is_on": True}
        elif command == "turn_off":
            self._is_on = False
            return {"success": True, "is_on": False}
        elif command == "toggle":
            self._is_on = not self._is_on
            return {"success": True, "is_on": self._is_on}
        return {"success": False, "error": "unknown command"}


class LightAdapter(DeviceBase):
    """灯光适配器"""

    def __init__(self, device_id: str, name: str):
        super().__init__(device_id, name, DeviceType.LIGHT)
        self._is_on: bool = False
        self._brightness: int = 100  # 0-100
        self._color: Dict[str, int] = {"r": 255, "g": 255, "b": 255}
        self._color_temp: int = 4000  # 开尔文

    async def connect(self) -> bool:
        await self._update_state(DeviceState.ONLINE)
        return True

    async def disconnect(self) -> None:
        await self._update_state(DeviceState.OFFLINE)

    async def read(self, capability: str = None) -> Dict[str, Any]:
        return {
            "is_on": self._is_on,
            "brightness": self._brightness,
            "color": self._color,
            "color_temp": self._color_temp
        }

    async def write(self, capability: str, value: Any) -> bool:
        if capability == "brightness":
            self._brightness = max(0, min(100, int(value)))
            return True
        elif capability == "color":
            if isinstance(value, dict):
                self._color = value
                return True
        elif capability == "color_temp":
            self._color_temp = int(value)
            return True
        elif capability == "state":
            self._is_on = bool(value)
            return True
        return False

    async def execute(self, command: str, params: Dict[str, Any] = None) -> Any:
        params = params or {}

        if command == "turn_on":
            self._is_on = True
            return {"success": True}
        elif command == "turn_off":
            self._is_on = False
            return {"success": True}
        elif command == "set_brightness":
            return {"success": await self.write("brightness", params.get("value", 100))}
        elif command == "set_color":
            return {"success": await self.write("color", params.get("color", {}))}
        elif command == "set_color_temp":
            return {"success": await self.write("color_temp", params.get("value", 4000))}

        return {"success": False, "error": "unknown command"}


class CameraAdapter(DeviceBase):
    """摄像头适配器"""

    def __init__(self, device_id: str, name: str):
        super().__init__(device_id, name, DeviceType.CAMERA)
        self._stream_url: Optional[str] = None
        self._is_recording: bool = False
        self._resolution: str = "1080p"

    async def connect(self) -> bool:
        await self._update_state(DeviceState.ONLINE)
        return True

    async def disconnect(self) -> None:
        self._is_recording = False
        await self._update_state(DeviceState.OFFLINE)

    async def read(self, capability: str = None) -> Dict[str, Any]:
        return {
            "stream_url": self._stream_url,
            "is_recording": self._is_recording,
            "resolution": self._resolution
        }

    async def write(self, capability: str, value: Any) -> bool:
        if capability == "resolution":
            self._resolution = value
            return True
        elif capability == "stream_url":
            self._stream_url = value
            return True
        return False

    async def execute(self, command: str, params: Dict[str, Any] = None) -> Any:
        params = params or {}

        if command == "start_recording":
            self._is_recording = True
            return {"success": True}
        elif command == "stop_recording":
            self._is_recording = False
            return {"success": True}
        elif command == "capture":
            # 返回模拟的截图 URL
            return {"success": True, "image_url": f"/capture/{self.device_id}/{datetime.now().isoformat()}.jpg"}
        elif command == "ptz":
            # 云台控制
            direction = params.get("direction")
            return {"success": True, "direction": direction}

        return {"success": False, "error": "unknown command"}


class ThermostatAdapter(DeviceBase):
    """温控器适配器"""

    def __init__(self, device_id: str, name: str):
        super().__init__(device_id, name, DeviceType.THERMOSTAT)
        self._current_temp: float = 22.0
        self._target_temp: float = 22.0
        self._mode: str = "auto"  # auto, heat, cool, off
        self._humidity: float = 50.0

    async def connect(self) -> bool:
        await self._update_state(DeviceState.ONLINE)
        return True

    async def disconnect(self) -> None:
        await self._update_state(DeviceState.OFFLINE)

    async def read(self, capability: str = None) -> Dict[str, Any]:
        return {
            "current_temp": self._current_temp,
            "target_temp": self._target_temp,
            "mode": self._mode,
            "humidity": self._humidity
        }

    async def write(self, capability: str, value: Any) -> bool:
        if capability == "target_temp":
            self._target_temp = float(value)
            return True
        elif capability == "mode":
            if value in ["auto", "heat", "cool", "off"]:
                self._mode = value
                return True
        return False

    async def execute(self, command: str, params: Dict[str, Any] = None) -> Any:
        params = params or {}

        if command == "set_temperature":
            return {"success": await self.write("target_temp", params.get("temperature"))}
        elif command == "set_mode":
            return {"success": await self.write("mode", params.get("mode"))}

        return {"success": False, "error": "unknown command"}


# 设备适配器工厂
ADAPTER_FACTORY = {
    DeviceType.SENSOR: SensorAdapter,
    DeviceType.SWITCH: SwitchAdapter,
    DeviceType.LIGHT: LightAdapter,
    DeviceType.CAMERA: CameraAdapter,
    DeviceType.THERMOSTAT: ThermostatAdapter,
}


def create_adapter(device_type: DeviceType, device_id: str, name: str, **kwargs) -> Optional[DeviceBase]:
    """创建设备适配器"""
    adapter_class = ADAPTER_FACTORY.get(device_type)
    if adapter_class:
        return adapter_class(device_id, name, **kwargs)
    return None
