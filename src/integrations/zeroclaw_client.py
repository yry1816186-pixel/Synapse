"""
Synapse + ZeroClaw 边缘集成层

提供与 ZeroClaw 边缘节点的通信和管理
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import asyncio
import json
import logging

logger = logging.getLogger(__name__)


class EdgeNodeStatus(Enum):
    """边缘节点状态"""
    ONLINE = "online"
    OFFLINE = "offline"
    BUSY = "busy"
    ERROR = "error"


@dataclass
class EdgeNode:
    """边缘节点"""
    node_id: str
    name: str
    endpoint: str
    status: EdgeNodeStatus = EdgeNodeStatus.OFFLINE
    last_heartbeat: Optional[datetime] = None
    capabilities: List[str] = field(default_factory=list)
    memory_mb: float = 0.0
    cpu_percent: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "name": self.name,
            "endpoint": self.endpoint,
            "status": self.status.value,
            "last_heartbeat": self.last_heartbeat.isoformat() if self.last_heartbeat else None,
            "capabilities": self.capabilities,
            "memory_mb": self.memory_mb,
            "cpu_percent": self.cpu_percent
        }


@dataclass
class EdgeTask:
    """边缘任务"""
    task_id: str
    node_id: str
    task_type: str
    payload: Dict[str, Any]
    priority: int = 0
    status: str = "pending"
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None


class ZeroClawIntegration:
    """
    ZeroClaw 集成层

    管理 Synapse 与 ZeroClaw 边缘节点的通信
    """

    def __init__(self):
        self._nodes: Dict[str, EdgeNode] = {}
        self._tasks: Dict[str, EdgeTask] = {}
        self._task_queue: asyncio.Queue = None
        self._running = False

    async def start(self) -> None:
        """启动集成层"""
        self._task_queue = asyncio.Queue()
        self._running = True
        logger.info("ZeroClaw 集成层已启动")

    async def stop(self) -> None:
        """停止集成层"""
        self._running = False
        logger.info("ZeroClaw 集成层已停止")

    def register_node(self, node: EdgeNode) -> bool:
        """注册边缘节点"""
        if node.node_id in self._nodes:
            logger.warning(f"节点已存在: {node.node_id}")
            return False

        self._nodes[node.node_id] = node
        logger.info(f"注册边缘节点: {node.name} ({node.node_id})")
        return True

    def unregister_node(self, node_id: str) -> bool:
        """注销边缘节点"""
        if node_id not in self._nodes:
            return False

        del self._nodes[node_id]
        logger.info(f"注销边缘节点: {node_id}")
        return True

    def get_node(self, node_id: str) -> Optional[EdgeNode]:
        """获取节点"""
        return self._nodes.get(node_id)

    def list_nodes(self) -> List[EdgeNode]:
        """列出所有节点"""
        return list(self._nodes.values())

    async def send_task(self, node_id: str, task_type: str,
                       payload: Dict[str, Any], priority: int = 0) -> Optional[str]:
        """
        发送任务到边缘节点

        Args:
            node_id: 节点 ID
            task_type: 任务类型
            payload: 任务数据
            priority: 优先级 (0-10, 10 最高)

        Returns:
            任务 ID 或 None
        """
        if node_id not in self._nodes:
            logger.error(f"节点不存在: {node_id}")
            return None

        node = self._nodes[node_id]
        if node.status != EdgeNodeStatus.ONLINE:
            logger.error(f"节点不可用: {node.status.value}")
            return None

        task_id = f"task_{datetime.now().strftime('%Y%m%d%H%M%S')}_{len(self._tasks)}"

        task = EdgeTask(
            task_id=task_id,
            node_id=node_id,
            task_type=task_type,
            payload=payload,
            priority=priority
        )

        self._tasks[task_id] = task
        await self._task_queue.put(task)

        logger.info(f"发送任务: {task_id} -> {node.name}")
        return task_id

    async def get_task_result(self, task_id: str) -> Optional[Dict[str, Any]]:
        """获取任务结果"""
        if task_id not in self._tasks:
            return None

        task = self._tasks[task_id]
        return {
            "task_id": task.task_id,
            "status": task.status,
            "result": task.result,
            "completed_at": task.completed_at.isoformat() if task.completed_at else None
        }

    async def send_sensor_command(self, node_id: str, sensor_id: str,
                                  command: str, params: Dict = None) -> Optional[str]:
        """发送传感器命令"""
        return await self.send_task(
            node_id=node_id,
            task_type="sensor_command",
            payload={
                "sensor_id": sensor_id,
                "command": command,
                "params": params or {}
            }
        )

    async def read_sensor(self, node_id: str, sensor_id: str) -> Optional[str]:
        """读取传感器数据"""
        return await self.send_task(
            node_id=node_id,
            task_type="sensor_read",
            payload={"sensor_id": sensor_id}
        )

    async def execute_rule(self, node_id: str, rule_id: str,
                          trigger_data: Dict = None) -> Optional[str]:
        """执行规则"""
        return await self.send_task(
            node_id=node_id,
            task_type="rule_execute",
            payload={
                "rule_id": rule_id,
                "trigger_data": trigger_data or {}
            }
        )

    async def call_cloud_api(self, node_id: str, api_name: str,
                            params: Dict = None) -> Optional[str]:
        """请求边缘节点调用云端 API"""
        return await self.send_task(
            node_id=node_id,
            task_type="cloud_api_call",
            payload={
                "api_name": api_name,
                "params": params or {}
            },
            priority=5  # API 调用优先级较高
        )

    async def health_check(self, node_id: str) -> Dict[str, Any]:
        """健康检查"""
        if node_id not in self._nodes:
            return {"error": "节点不存在"}

        node = self._nodes[node_id]

        # 模拟健康检查
        return {
            "node_id": node_id,
            "status": node.status.value,
            "memory_mb": node.memory_mb,
            "cpu_percent": node.cpu_percent,
            "capabilities": node.capabilities,
            "timestamp": datetime.now().isoformat()
        }

    def get_stats(self) -> Dict[str, Any]:
        """获取统计"""
        online = sum(1 for n in self._nodes.values() if n.status == EdgeNodeStatus.ONLINE)
        offline = sum(1 for n in self._nodes.values() if n.status == EdgeNodeStatus.OFFLINE)

        pending_tasks = sum(1 for t in self._tasks.values() if t.status == "pending")
        completed_tasks = sum(1 for t in self._tasks.values() if t.status == "completed")

        return {
            "total_nodes": len(self._nodes),
            "online_nodes": online,
            "offline_nodes": offline,
            "total_tasks": len(self._tasks),
            "pending_tasks": pending_tasks,
            "completed_tasks": completed_tasks
        }


# 全局集成实例
zeroclaw_integration = ZeroClawIntegration()
