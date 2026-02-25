"""
ZeroMQ 高性能消息适配器 - 借鉴 Neurosim 论文
用于边缘消息队列
"""

from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from datetime import datetime
import asyncio
import logging

logger = logging.getLogger(__name__)


@dataclass
class MessageStats:
    """消息统计"""
    sent: int = 0
    received: int = 0
    errors: int = 0
    total_bytes: int = 0


class ZeroMQAdapter:
    """
    ZeroMQ 高性能消息适配器
    
    借鉴 Neurosim 论文的高性能通信设计
    """

    def __init__(self):
        self._context = None
        self._sockets: Dict[str, Any] = {}
        self._stats = MessageStats()
        self._connected = False
        self._handlers: Dict[str, Callable] = {}

    async def initialize(self) -> bool:
        """初始化 ZeroMQ"""
        try:
            import zmq
            import zmq.asyncio

            self._context = zmq.asyncio.Context()
            self._connected = True
            logger.info("ZeroMQ 初始化成功")
            return True
        except ImportError:
            logger.warning("ZeroMQ 未安装，使用模拟模式")
            self._connected = True
            return True

    async def create_publisher(self, name: str, bind_url: str = "tcp://*:5555") -> bool:
        """创建发布者"""
        if not self._connected:
            await self.initialize()

        try:
            if self._context:
                import zmq
                socket = self._context.socket(zmq.PUB)
                socket.bind(bind_url)
                self._sockets[name] = socket
                logger.info(f"发布者已创建: {name} @ {bind_url}")
            else:
                self._sockets[name] = {"type": "pub", "url": bind_url}
            return True
        except Exception as e:
            logger.error(f"创建发布者失败: {e}")
            return False

    async def create_subscriber(self, name: str, connect_url: str = "tcp://localhost:5555",
                                topic: str = "") -> bool:
        """创建订阅者"""
        if not self._connected:
            await self.initialize()

        try:
            if self._context:
                import zmq
                socket = self._context.socket(zmq.SUB)
                socket.connect(connect_url)
                socket.setsockopt_string(zmq.SUBSCRIBE, topic)
                self._sockets[name] = socket
                logger.info(f"订阅者已创建: {name} @ {connect_url}")
            else:
                self._sockets[name] = {"type": "sub", "url": connect_url}
            return True
        except Exception as e:
            logger.error(f"创建订阅者失败: {e}")
            return False

    async def send(self, socket_name: str, topic: str, message: bytes) -> bool:
        """发送消息"""
        socket = self._sockets.get(socket_name)
        if not socket:
            return False

        try:
            if hasattr(socket, 'send_multipart'):
                await socket.send_multipart([topic.encode(), message])
            else:
                pass  # 模拟模式

            self._stats.sent += 1
            self._stats.total_bytes += len(message)
            return True
        except Exception as e:
            logger.error(f"发送消息失败: {e}")
            self._stats.errors += 1
            return False

    async def receive(self, socket_name: str, timeout_ms: int = 1000) -> Optional[tuple]:
        """接收消息"""
        socket = self._sockets.get(socket_name)
        if not socket:
            return None

        try:
            if hasattr(socket, 'recv_multipart'):
                import zmq
                topic, message = await socket.recv_multipart()
                self._stats.received += 1
                self._stats.total_bytes += len(message)
                return topic.decode(), message
            else:
                return None
        except Exception as e:
            logger.error(f"接收消息失败: {e}")
            self._stats.errors += 1
            return None

    def on_message(self, topic: str, handler: Callable) -> None:
        """注册消息处理器"""
        self._handlers[topic] = handler

    async def start_listening(self, socket_name: str) -> None:
        """开始监听"""
        while self._connected:
            result = await self.receive(socket_name)
            if result:
                topic, message = result
                handler = self._handlers.get(topic)
                if handler:
                    try:
                        if asyncio.iscoroutinefunction(handler):
                            await handler(topic, message)
                        else:
                            handler(topic, message)
                    except Exception as e:
                        logger.error(f"消息处理错误: {e}")

    def get_stats(self) -> Dict[str, int]:
        """获取统计"""
        return {
            "sent": self._stats.sent,
            "received": self._stats.received,
            "errors": self._stats.errors,
            "total_bytes": self._stats.total_bytes
        }

    async def close(self) -> None:
        """关闭连接"""
        for socket in self._sockets.values():
            if hasattr(socket, 'close'):
                socket.close()

        if self._context:
            self._context.term()

        self._connected = False
        logger.info("ZeroMQ 已关闭")


# 全局适配器
zeromq_adapter = ZeroMQAdapter()
