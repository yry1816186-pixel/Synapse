"""
WebSocket API - 实时通信
"""

from typing import Dict, Any, Optional, List, Set
from dataclasses import dataclass, field
from datetime import datetime
import asyncio
import logging
import json
from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)


@dataclass
class WebSocketClient:
    """WebSocket 客户端"""
    websocket: WebSocket
    client_id: str
    tenant_id: Optional[str] = None
    user_id: Optional[str] = None
    subscriptions: Set[str] = field(default_factory=set)
    connected_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)


class WebSocketManager:
    """WebSocket 管理器"""

    def __init__(self):
        self._clients: Dict[str, WebSocketClient] = {}
        self._subscriptions: Dict[str, Set[str]] = {}  # topic -> client_ids

    async def connect(self, websocket: WebSocket, client_id: str) -> WebSocketClient:
        """接受连接"""
        await websocket.accept()

        client = WebSocketClient(
            websocket=websocket,
            client_id=client_id
        )
        self._clients[client_id] = client

        logger.info(f"WebSocket 连接: {client_id}")
        return client

    async def disconnect(self, client_id: str) -> None:
        """断开连接"""
        client = self._clients.pop(client_id, None)
        if client:
            # 清理订阅
            for topic in client.subscriptions:
                if topic in self._subscriptions:
                    self._subscriptions[topic].discard(client_id)

            logger.info(f"WebSocket 断开: {client_id}")

    async def subscribe(self, client_id: str, topic: str) -> None:
        """订阅主题"""
        client = self._clients.get(client_id)
        if not client:
            return

        client.subscriptions.add(topic)

        if topic not in self._subscriptions:
            self._subscriptions[topic] = set()
        self._subscriptions[topic].add(client_id)

        logger.debug(f"订阅: {client_id} -> {topic}")

    async def unsubscribe(self, client_id: str, topic: str) -> None:
        """取消订阅"""
        client = self._clients.get(client_id)
        if client:
            client.subscriptions.discard(topic)

        if topic in self._subscriptions:
            self._subscriptions[topic].discard(client_id)

    async def send_to(self, client_id: str, message: Dict[str, Any]) -> bool:
        """发送到指定客户端"""
        client = self._clients.get(client_id)
        if not client:
            return False

        try:
            await client.websocket.send_json(message)
            client.last_activity = datetime.now()
            return True
        except Exception as e:
            logger.error(f"发送消息失败: {e}")
            return False

    async def broadcast(self, topic: str, message: Dict[str, Any]) -> int:
        """广播到订阅者"""
        client_ids = self._subscriptions.get(topic, set())
        count = 0

        for client_id in client_ids:
            if await self.send_to(client_id, message):
                count += 1

        return count

    async def broadcast_all(self, message: Dict[str, Any]) -> int:
        """广播到所有客户端"""
        count = 0
        for client_id in self._clients:
            if await self.send_to(client_id, message):
                count += 1
        return count

    def get_client(self, client_id: str) -> Optional[WebSocketClient]:
        """获取客户端"""
        return self._clients.get(client_id)

    def get_clients_by_tenant(self, tenant_id: str) -> List[WebSocketClient]:
        """获取租户的所有客户端"""
        return [c for c in self._clients.values() if c.tenant_id == tenant_id]

    @property
    def client_count(self) -> int:
        return len(self._clients)


# 全局管理器
ws_manager = WebSocketManager()


async def websocket_handler(websocket: WebSocket, client_id: str):
    """WebSocket 处理器"""
    client = await ws_manager.connect(websocket, client_id)

    try:
        # 发送欢迎消息
        await ws_manager.send_to(client_id, {
            "type": "connected",
            "client_id": client_id,
            "timestamp": datetime.now().isoformat()
        })

        while True:
            # 接收消息
            data = await websocket.receive_text()

            try:
                message = json.loads(data)
                await handle_message(client_id, message)
            except json.JSONDecodeError:
                await ws_manager.send_to(client_id, {
                    "type": "error",
                    "message": "无效的 JSON"
                })

    except WebSocketDisconnect:
        pass
    finally:
        await ws_manager.disconnect(client_id)


async def handle_message(client_id: str, message: Dict[str, Any]) -> None:
    """处理消息"""
    msg_type = message.get("type", "unknown")

    if msg_type == "subscribe":
        topic = message.get("topic")
        if topic:
            await ws_manager.subscribe(client_id, topic)
            await ws_manager.send_to(client_id, {
                "type": "subscribed",
                "topic": topic
            })

    elif msg_type == "unsubscribe":
        topic = message.get("topic")
        if topic:
            await ws_manager.unsubscribe(client_id, topic)
            await ws_manager.send_to(client_id, {
                "type": "unsubscribed",
                "topic": topic
            })

    elif msg_type == "ping":
        await ws_manager.send_to(client_id, {"type": "pong"})

    elif msg_type == "device_command":
        # 设备命令
        device_id = message.get("device_id")
        command = message.get("command")
        params = message.get("params", {})

        # 广播到订阅该设备的客户端
        await ws_manager.broadcast(f"device:{device_id}", {
            "type": "device_command",
            "device_id": device_id,
            "command": command,
            "params": params
        })

    else:
        # 未知消息类型
        logger.warning(f"未知消息类型: {msg_type}")
