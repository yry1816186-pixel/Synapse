"""
数据桥接 - 统一的数据出口
借鉴 EMQX bridge 架构
"""

from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import asyncio
import logging
import json

logger = logging.getLogger(__name__)


class BridgeType(Enum):
    """桥接类型"""
    KAFKA = "kafka"
    RABBITMQ = "rabbitmq"
    REDIS = "redis"
    MONGODB = "mongodb"
    MYSQL = "mysql"
    POSTGRESQL = "postgresql"
    ELASTICSEARCH = "elasticsearch"
    INFLUXDB = "influxdb"
    TIMESCALE = "timescale"
    HTTP = "http"
    WEBHOOK = "webhook"
    MQTT = "mqtt"
    NATS = "nats"
    PULSAR = "pulsar"
    S3 = "s3"
    CUSTOM = "custom"


@dataclass
class BridgeConfig:
    """桥接配置"""
    bridge_id: str
    bridge_type: BridgeType
    name: str = ""
    enabled: bool = True
    config: Dict[str, Any] = field(default_factory=dict)
    batch_size: int = 100
    batch_timeout: int = 5  # 秒
    retry_count: int = 3


@dataclass
class BridgeStatus:
    """桥接状态"""
    bridge_id: str
    connected: bool = False
    last_success: Optional[datetime] = None
    last_failure: Optional[datetime] = None
    total_messages: int = 0
    failed_messages: int = 0
    error_message: Optional[str] = None


class DataBridge:
    """数据桥接基类"""

    def __init__(self, config: BridgeConfig):
        self.config = config
        self._status = BridgeStatus(bridge_id=config.bridge_id)
        self._buffer: List[Dict[str, Any]] = []
        self._running = False

    async def connect(self) -> bool:
        """连接"""
        raise NotImplementedError

    async def disconnect(self) -> None:
        """断开"""
        self._running = False
        self._status.connected = False

    async def send(self, data: Dict[str, Any]) -> bool:
        """发送数据"""
        self._buffer.append(data)

        # 批量发送
        if len(self._buffer) >= self.config.batch_size:
            return await self._flush()

        return True

    async def _flush(self) -> bool:
        """刷新缓冲区"""
        if not self._buffer:
            return True

        data = self._buffer.copy()
        self._buffer.clear()

        try:
            success = await self._write_batch(data)
            if success:
                self._status.last_success = datetime.now()
                self._status.total_messages += len(data)
            else:
                self._status.last_failure = datetime.now()
                self._status.failed_messages += len(data)
            return success
        except Exception as e:
            self._status.error_message = str(e)
            self._status.last_failure = datetime.now()
            return False

    async def _write_batch(self, data: List[Dict[str, Any]]) -> bool:
        """写入批量数据"""
        raise NotImplementedError

    @property
    def status(self) -> BridgeStatus:
        return self._status


class HTTPBridge(DataBridge):
    """HTTP 桥接"""

    async def connect(self) -> bool:
        self._status.connected = True
        self._running = True
        return True

    async def _write_batch(self, data: List[Dict[str, Any]]) -> bool:
        url = self.config.config.get("url")
        headers = self.config.config.get("headers", {})

        from .http import HTTPClient
        client = HTTPClient()

        result = await client.request(
            "POST", url,
            headers=headers,
            json={"data": data}
        )

        return result.get("success", False)


class RedisBridge(DataBridge):
    """Redis 桥接"""

    async def connect(self) -> bool:
        # TODO: 实现 Redis 连接
        self._status.connected = True
        return True

    async def _write_batch(self, data: List[Dict[str, Any]]) -> bool:
        # TODO: 实现 Redis 批量写入
        return True


class BridgeManager:
    """桥接管理器"""

    def __init__(self):
        self._bridges: Dict[str, DataBridge] = {}
        self._type_registry: Dict[BridgeType, type] = {
            BridgeType.HTTP: HTTPBridge,
            BridgeType.REDIS: RedisBridge,
        }

    def register_type(self, bridge_type: BridgeType, bridge_class: type) -> None:
        """注册桥接类型"""
        self._type_registry[bridge_type] = bridge_class

    async def create_bridge(self, config: BridgeConfig) -> Optional[DataBridge]:
        """创建桥接"""
        bridge_class = self._type_registry.get(config.bridge_type)
        if not bridge_class:
            logger.error(f"未知的桥接类型: {config.bridge_type}")
            return None

        bridge = bridge_class(config)
        if await bridge.connect():
            self._bridges[config.bridge_id] = bridge
            logger.info(f"桥接已创建: {config.name} [{config.bridge_type.value}]")
            return bridge

        return None

    async def remove_bridge(self, bridge_id: str) -> bool:
        """移除桥接"""
        bridge = self._bridges.get(bridge_id)
        if not bridge:
            return False

        await bridge.disconnect()
        del self._bridges[bridge_id]
        return True

    async def send_to_bridge(self, bridge_id: str, data: Dict[str, Any]) -> bool:
        """发送数据到指定桥接"""
        bridge = self._bridges.get(bridge_id)
        if not bridge:
            return False

        return await bridge.send(data)

    async def broadcast(self, data: Dict[str, Any]) -> Dict[str, bool]:
        """广播到所有桥接"""
        results = {}
        for bridge_id, bridge in self._bridges.items():
            results[bridge_id] = await bridge.send(data)
        return results

    def get_status(self) -> Dict[str, BridgeStatus]:
        """获取所有桥接状态"""
        return {bid: bridge.status for bid, bridge in self._bridges.items()}


# 全局管理器
bridge_manager = BridgeManager()
