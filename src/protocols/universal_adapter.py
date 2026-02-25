"""
万能协议适配器 - 开放设备接入框架
参考 Home Assistant 的组件系统设计
"""

from typing import Dict, Any, Optional, List, Type, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import asyncio
import logging
import importlib
import os
import json

logger = logging.getLogger(__name__)


class ProtocolType(Enum):
    """协议类型"""
    # 无线协议
    ZIGBEE = "zigbee"
    ZWAVE = "zwave"
    BLUETOOTH = "bluetooth"
    BLE = "ble"              # 低功耗蓝牙
    WIFI = "wifi"
    THREAD = "thread"
    MATTER = "matter"        # 新的统一协议
    LORA = "lora"            # 远距离低功耗

    # 有线协议
    ETHERNET = "ethernet"
    USB = "usb"
    SERIAL = "serial"        # RS232/RS485
    I2C = "i2c"
    SPI = "spi"
    GPIO = "gpio"
    CAN = "can"              # 工业总线

    # 软件协议
    MQTT = "mqtt"
    HTTP = "http"
    WEBSOCKET = "websocket"
    COAP = "coap"
    MODBUS = "modbus"        # 工业协议
    OPC_UA = "opc_ua"        # 工业物联网


class DeviceCategory(Enum):
    """设备类别"""
    LIGHT = "light"
    SWITCH = "switch"
    SENSOR = "sensor"
    CLIMATE = "climate"
    CAMERA = "camera"
    LOCK = "lock"
    COVER = "cover"          # 窗帘、门
    FAN = "fan"
    HUMIDIFIER = "humidifier"
    VACUUM = "vacuum"        # 扫地机
    MEDIA_PLAYER = "media_player"
    BINARY_SENSOR = "binary_sensor"
    UNKNOWN = "unknown"


@dataclass
class ProtocolAdapter:
    """协议适配器"""
    adapter_id: str
    name: str
    protocol_type: ProtocolType
    version: str = "1.0"
    author: str = ""
    description: str = ""
    supported_devices: List[str] = field(default_factory=list)
    config_schema: Dict[str, Any] = field(default_factory=dict)
    initialized: bool = False


@dataclass
class DeviceIntegration:
    """设备集成"""
    integration_id: str
    name: str
    brand: str = ""
    model: str = ""
    category: DeviceCategory = DeviceCategory.UNKNOWN
    protocols: List[ProtocolType] = field(default_factory=list)
    discovery_enabled: bool = True
    config: Dict[str, Any] = field(default_factory=dict)


class UniversalProtocolAdapter:
    """
    万能协议适配器
    
    设计理念：
    1. 插件化 - 每个协议是一个独立插件
    2. 自动发现 - 自动识别连接的设备
    3. 配置简单 - YAML/JSON 配置
    4. 完全开放 - 任何人可以开发适配器
    """

    def __init__(self):
        self._adapters: Dict[str, ProtocolAdapter] = {}
        self._integrations: Dict[str, DeviceIntegration] = {}
        self._device_handlers: Dict[str, Callable] = {}
        self._discovery_callbacks: List[Callable] = []

    async def register_adapter(self, adapter: ProtocolAdapter) -> bool:
        """注册协议适配器"""
        self._adapters[adapter.adapter_id] = adapter
        logger.info(f"注册协议适配器: {adapter.name} ({adapter.protocol_type.value})")
        return True

    async def register_integration(self, integration: DeviceIntegration) -> bool:
        """注册设备集成"""
        self._integrations[integration.integration_id] = integration
        logger.info(f"注册设备集成: {integration.name} ({integration.brand})")
        return True

    async def discover_devices(self, protocol_type: ProtocolType = None) -> List[Dict[str, Any]]:
        """自动发现设备"""
        discovered = []

        for adapter_id, adapter in self._adapters.items():
            if protocol_type and adapter.protocol_type != protocol_type:
                continue

            if not adapter.initialized:
                continue

            # 调用适配器的发现方法
            devices = await self._discover_via_adapter(adapter)
            discovered.extend(devices)

        # 通知发现回调
        for callback in self._discovery_callbacks:
            try:
                await callback(discovered)
            except Exception as e:
                logger.error(f"发现回调错误: {e}")

        return discovered

    async def _discover_via_adapter(self, adapter: ProtocolAdapter) -> List[Dict[str, Any]]:
        """通过适配器发现设备"""
        # 模拟设备发现
        # 实际实现需要具体协议的发现逻辑
        return []

    def on_device_discovered(self, callback: Callable) -> None:
        """注册设备发现回调"""
        self._discovery_callbacks.append(callback)

    async def connect_device(self, device_config: Dict[str, Any]) -> Optional[str]:
        """连接设备"""
        protocol = device_config.get("protocol")
        device_id = device_config.get("device_id", f"device_{datetime.now().timestamp()}")

        # 找到对应的适配器
        adapter = self._find_adapter_for_protocol(protocol)
        if not adapter:
            logger.warning(f"未找到协议适配器: {protocol}")
            return None

        # 执行连接
        handler = self._device_handlers.get(adapter.adapter_id)
        if handler:
            try:
                result = await handler("connect", device_config)
                if result.get("success"):
                    logger.info(f"设备连接成功: {device_id}")
                    return device_id
            except Exception as e:
                logger.error(f"设备连接失败: {e}")

        return None

    def _find_adapter_for_protocol(self, protocol: str) -> Optional[ProtocolAdapter]:
        """查找协议适配器"""
        for adapter in self._adapters.values():
            if adapter.protocol_type.value == protocol:
                return adapter
        return None

    def register_device_handler(self, adapter_id: str, handler: Callable) -> None:
        """注册设备处理器"""
        self._device_handlers[adapter_id] = handler

    def get_supported_protocols(self) -> List[str]:
        """获取支持的协议列表"""
        return [a.protocol_type.value for a in self._adapters.values()]

    def get_supported_brands(self) -> List[str]:
        """获取支持的品牌列表"""
        brands = set()
        for integration in self._integrations.values():
            if integration.brand:
                brands.add(integration.brand)
        return list(brands)


class AdapterPluginLoader:
    """
    适配器插件加载器
    
    从指定目录动态加载协议适配器插件
    """

    def __init__(self, plugin_dir: str = "./adapters"):
        self.plugin_dir = plugin_dir
        self._loaded_plugins: Dict[str, Any] = {}

    async def load_all(self) -> int:
        """加载所有插件"""
        if not os.path.exists(self.plugin_dir):
            logger.warning(f"插件目录不存在: {self.plugin_dir}")
            return 0

        count = 0
        for filename in os.listdir(self.plugin_dir):
            if filename.endswith(".py") and not filename.startswith("_"):
                plugin_name = filename[:-3]
                if await self.load_plugin(plugin_name):
                    count += 1

        logger.info(f"加载了 {count} 个适配器插件")
        return count

    async def load_plugin(self, plugin_name: str) -> bool:
        """加载单个插件"""
        try:
            # 动态导入
            module_path = f"{self.plugin_dir.replace('/', '.')}.{plugin_name}"
            module = importlib.import_module(module_path)

            # 查找适配器类
            adapter_class = getattr(module, "Adapter", None)
            if adapter_class:
                adapter = adapter_class()
                self._loaded_plugins[plugin_name] = adapter
                logger.info(f"加载适配器插件: {plugin_name}")
                return True

        except Exception as e:
            logger.error(f"加载插件失败 {plugin_name}: {e}")

        return False

    def get_plugin(self, plugin_name: str) -> Optional[Any]:
        """获取插件"""
        return self._loaded_plugins.get(plugin_name)


# 预置的协议适配器
BUILTIN_ADAPTERS = {
    "mqtt": ProtocolAdapter(
        adapter_id="mqtt",
        name="MQTT 适配器",
        protocol_type=ProtocolType.MQTT,
        description="支持所有 MQTT 协议设备",
        supported_devices=["*", "any mqtt device"]
    ),
    "http": ProtocolAdapter(
        adapter_id="http",
        name="HTTP/REST 适配器",
        protocol_type=ProtocolType.HTTP,
        description="支持 HTTP RESTful API 设备",
        supported_devices=["*", "any http device"]
    ),
    "zigbee": ProtocolAdapter(
        adapter_id="zigbee",
        name="Zigbee 适配器",
        protocol_type=ProtocolType.ZIGBEE,
        description="支持 Zigbee 智能家居设备",
        supported_devices=["xiaomi", "aqara", "hue", "ikea tradfri"]
    ),
    "bluetooth": ProtocolAdapter(
        adapter_id="bluetooth",
        name="蓝牙适配器",
        protocol_type=ProtocolType.BLUETOOTH,
        description="支持蓝牙 BLE 设备",
        supported_devices=["mi band", "temperature sensor", "smart lock"]
    ),
    "modbus": ProtocolAdapter(
        adapter_id="modbus",
        name="Modbus 适配器",
        protocol_type=ProtocolType.MODBUS,
        description="支持工业 Modbus 设备",
        supported_devices=["plc", "industrial sensor", "meter"]
    )
}


# 全局万能适配器
universal_adapter = UniversalProtocolAdapter()

# 预置适配器需要在主程序中手动注册
# for adapter_id, adapter in BUILTIN_ADAPTERS.items():
#     await universal_adapter.register_adapter(adapter)
