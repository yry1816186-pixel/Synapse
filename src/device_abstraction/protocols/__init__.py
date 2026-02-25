"""
协议支持 - 多协议设备接入
借鉴 EMQX gateway 架构
"""

from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import asyncio
import logging

logger = logging.getLogger(__name__)


class ProtocolType(Enum):
    """协议类型"""
    MQTT = "mqtt"
    COAP = "coap"
    HTTP = "http"
    WEBSOCKET = "websocket"
    MODBUS = "modbus"
    ZIGBEE = "zigbee"
    BLE = "ble"
    LORA = "lora"
    CUSTOM = "custom"


@dataclass
class ProtocolConfig:
    """协议配置"""
    protocol_type: ProtocolType
    port: int
    enabled: bool = True
    config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProtocolClient:
    """协议客户端信息"""
    client_id: str
    protocol_type: ProtocolType
    connected_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    address: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


class ProtocolGateway:
    """协议网关基类"""

    def __init__(self, config: ProtocolConfig):
        self.config = config
        self._clients: Dict[str, ProtocolClient] = {}
        self._running = False
        self._message_handler: Optional[Callable] = None

    async def start(self) -> bool:
        """启动网关"""
        self._running = True
        logger.info(f"协议网关已启动: {self.config.protocol_type.value} :{self.config.port}")
        return True

    async def stop(self) -> None:
        """停止网关"""
        self._running = False
        self._clients.clear()
        logger.info(f"协议网关已停止: {self.config.protocol_type.value}")

    async def on_client_connect(self, client_id: str, address: str = "", **metadata) -> None:
        """客户端连接"""
        client = ProtocolClient(
            client_id=client_id,
            protocol_type=self.config.protocol_type,
            address=address,
            metadata=metadata
        )
        self._clients[client_id] = client
        logger.info(f"客户端连接: {client_id} [{self.config.protocol_type.value}]")

    async def on_client_disconnect(self, client_id: str) -> None:
        """客户端断开"""
        if client_id in self._clients:
            del self._clients[client_id]
            logger.info(f"客户端断开: {client_id}")

    async def on_message(self, client_id: str, topic: str, payload: bytes) -> None:
        """消息处理"""
        if client_id in self._clients:
            self._clients[client_id].last_activity = datetime.now()

        if self._message_handler:
            await self._message_handler(client_id, topic, payload)

    def set_message_handler(self, handler: Callable) -> None:
        """设置消息处理器"""
        self._message_handler = handler

    def get_clients(self) -> List[ProtocolClient]:
        return list(self._clients.values())


class MQTTGateway(ProtocolGateway):
    """MQTT 网关"""

    async def start(self) -> bool:
        await super().start()
        # TODO: 实现 MQTT 服务器逻辑
        return True


class CoAPGateway(ProtocolGateway):
    """CoAP 网关"""

    async def start(self) -> bool:
        await super().start()
        # TODO: 实现 CoAP 服务器逻辑
        return True


class HTTPGateway(ProtocolGateway):
    """HTTP 网关"""

    async def start(self) -> bool:
        await super().start()
        # TODO: 实现 HTTP 服务器逻辑
        return True


class ProtocolManager:
    """协议管理器"""

    def __init__(self):
        self._gateways: Dict[ProtocolType, ProtocolGateway] = {}
        self._gateway_factory = {
            ProtocolType.MQTT: MQTTGateway,
            ProtocolType.COAP: CoAPGateway,
            ProtocolType.HTTP: HTTPGateway,
        }

    async def create_gateway(self, config: ProtocolConfig) -> Optional[ProtocolGateway]:
        """创建网关"""
        if config.protocol_type in self._gateways:
            logger.warning(f"网关已存在: {config.protocol_type.value}")
            return None

        gateway_class = self._gateway_factory.get(config.protocol_type)
        if not gateway_class:
            logger.error(f"不支持的协议: {config.protocol_type.value}")
            return None

        gateway = gateway_class(config)
        if await gateway.start():
            self._gateways[config.protocol_type] = gateway
            return gateway

        return None

    async def remove_gateway(self, protocol_type: ProtocolType) -> bool:
        """移除网关"""
        gateway = self._gateways.get(protocol_type)
        if not gateway:
            return False

        await gateway.stop()
        del self._gateways[protocol_type]
        return True

    def get_gateway(self, protocol_type: ProtocolType) -> Optional[ProtocolGateway]:
        return self._gateways.get(protocol_type)

    async def broadcast(self, topic: str, payload: bytes) -> int:
        """广播到所有网关"""
        count = 0
        for gateway in self._gateways.values():
            # TODO: 实现广播逻辑
            count += len(gateway.get_clients())
        return count

    async def start_all(self) -> None:
        """启动所有网关"""
        for gateway in self._gateways.values():
            await gateway.start()

    async def stop_all(self) -> None:
        """停止所有网关"""
        for gateway in self._gateways.values():
            await gateway.stop()


# 全局协议管理器
protocol_manager = ProtocolManager()
