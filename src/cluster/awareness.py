"""
集群资源感知 - Synapse 的"自我意识"
参考 OpenClaw 的资源监控设计
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import asyncio
import logging
import platform
import os

logger = logging.getLogger(__name__)


class ResourceType(Enum):
    """资源类型"""
    CPU = "cpu"
    MEMORY = "memory"
    STORAGE = "storage"
    NETWORK = "network"
    GPU = "gpu"


@dataclass
class ResourceMetrics:
    """资源指标"""
    resource_type: ResourceType
    total: float = 0.0
    used: float = 0.0
    available: float = 0.0
    utilization: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class NodeInfo:
    """节点信息"""
    node_id: str
    name: str
    node_type: str  # "edge", "server", "workstation", "iot"
    ip_address: str
    location: str = ""
    resources: Dict[ResourceType, ResourceMetrics] = field(default_factory=dict)
    capabilities: List[str] = field(default_factory=list)
    status: str = "unknown"
    last_heartbeat: datetime = None


class ClusterAwareness:
    """
    集群感知系统
    
    让 Synapse "感知"整个区域的计算资源
    类似 OpenClaw 感知主机的扩展版
    """

    def __init__(self):
        self._nodes: Dict[str, NodeInfo] = {}
        self._self_node: Optional[NodeInfo] = None
        self._running = False

    async def initialize(self) -> None:
        """初始化 - 感知自身"""
        self._self_node = await self._discover_self()
        self._nodes[self._self_node.node_id] = self._self_node
        logger.info(f"集群感知初始化: {self._self_node.name}")

    async def _discover_self(self) -> NodeInfo:
        """发现自身节点信息"""
        node_id = f"node_{platform.node()}"
        
        # 获取系统资源
        cpu_total = os.cpu_count() or 1
        
        try:
            import psutil
            memory_total = psutil.virtual_memory().total / (1024**3)  # GB
            storage_total = psutil.disk_usage('/').total / (1024**3)  # GB
        except ImportError:
            memory_total = 16.0
            storage_total = 100.0

        return NodeInfo(
            node_id=node_id,
            name=platform.node(),
            node_type="server",
            ip_address=self._get_local_ip(),
            location="default",
            resources={
                ResourceType.CPU: ResourceMetrics(
                    resource_type=ResourceType.CPU,
                    total=cpu_total,
                    available=cpu_total
                ),
                ResourceType.MEMORY: ResourceMetrics(
                    resource_type=ResourceType.MEMORY,
                    total=memory_total,
                    available=memory_total
                ),
                ResourceType.STORAGE: ResourceMetrics(
                    resource_type=ResourceType.STORAGE,
                    total=storage_total,
                    available=storage_total
                )
            },
            capabilities=["compute", "storage", "network"],
            status="ready"
        )

    def _get_local_ip(self) -> str:
        """获取本地 IP"""
        import socket
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"

    async def register_node(self, node: NodeInfo) -> None:
        """注册节点"""
        self._nodes[node.node_id] = node
        logger.info(f"节点注册: {node.name} ({node.node_type})")

    async def unregister_node(self, node_id: str) -> None:
        """注销节点"""
        if node_id in self._nodes:
            del self._nodes[node_id]
            logger.info(f"节点注销: {node_id}")

    async def update_metrics(self, node_id: str, 
                            metrics: Dict[ResourceType, ResourceMetrics]) -> None:
        """更新节点指标"""
        node = self._nodes.get(node_id)
        if node:
            node.resources.update(metrics)
            node.last_heartbeat = datetime.now()

    async def update_self_metrics(self) -> None:
        """更新自身指标"""
        if not self._self_node:
            return

        try:
            import psutil
            
            # CPU
            cpu_percent = psutil.cpu_percent(interval=0.1)
            self._self_node.resources[ResourceType.CPU].utilization = cpu_percent / 100
            self._self_node.resources[ResourceType.CPU].used = \
                self._self_node.resources[ResourceType.CPU].total * cpu_percent / 100

            # Memory
            mem = psutil.virtual_memory()
            self._self_node.resources[ResourceType.MEMORY].utilization = mem.percent / 100
            self._self_node.resources[ResourceType.MEMORY].used = mem.used / (1024**3)

        except ImportError:
            pass

    def get_cluster_status(self) -> Dict[str, Any]:
        """获取集群状态"""
        total_cpu = 0
        total_memory = 0
        total_nodes = len(self._nodes)

        for node in self._nodes.values():
            if ResourceType.CPU in node.resources:
                total_cpu += node.resources[ResourceType.CPU].total
            if ResourceType.MEMORY in node.resources:
                total_memory += node.resources[ResourceType.MEMORY].total

        return {
            "total_nodes": total_nodes,
            "total_cpu_cores": total_cpu,
            "total_memory_gb": total_memory,
            "nodes": {
                node_id: {
                    "name": node.name,
                    "type": node.node_type,
                    "status": node.status,
                    "location": node.location
                }
                for node_id, node in self._nodes.items()
            }
        }

    def get_available_resources(self) -> Dict[str, float]:
        """获取可用资源"""
        available = {
            "cpu_cores": 0.0,
            "memory_gb": 0.0,
            "storage_gb": 0.0
        }

        for node in self._nodes.values():
            if node.status != "ready":
                continue

            if ResourceType.CPU in node.resources:
                available["cpu_cores"] += node.resources[ResourceType.CPU].available
            if ResourceType.MEMORY in node.resources:
                available["memory_gb"] += node.resources[ResourceType.MEMORY].available
            if ResourceType.STORAGE in node.resources:
                available["storage_gb"] += node.resources[ResourceType.STORAGE].available

        return available

    def find_best_node(self, requirements: Dict[str, float]) -> Optional[str]:
        """找到最适合的节点"""
        best_node = None
        best_score = -1

        for node_id, node in self._nodes.items():
            if node.status != "ready":
                continue

            score = 0

            # CPU 匹配
            if "cpu" in requirements:
                available = node.resources.get(ResourceType.CPU, ResourceMetrics(ResourceType.CPU))
                if available.available >= requirements["cpu"]:
                    score += 10

            # Memory 匹配
            if "memory" in requirements:
                available = node.resources.get(ResourceType.MEMORY, ResourceMetrics(ResourceType.MEMORY))
                if available.available >= requirements["memory"]:
                    score += 10

            if score > best_score:
                best_score = score
                best_node = node_id

        return best_node


# 全局集群感知
cluster_awareness = ClusterAwareness()
