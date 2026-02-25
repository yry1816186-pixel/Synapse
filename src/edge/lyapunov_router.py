"""
Lyapunov 稳定路由器 - 借鉴 Stable-MoE 论文
用于边缘节点 AI 训练的负载均衡
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
import math
import logging

logger = logging.getLogger(__name__)


@dataclass
class NodeState:
    """节点状态"""
    node_id: str
    load: float = 0.0
    capacity: float = 1.0
    latency_ms: float = 0.0
    last_update: datetime = field(default_factory=datetime.now)


class LyapunovStableRouter:
    """
    Lyapunov 稳定路由器
    
    基于 Stable-MoE 论文的 Lyapunov 稳定性理论，
    实现边缘节点的负载均衡路由。
    """

    def __init__(self, alpha: float = 0.1, beta: float = 0.9):
        """
        初始化路由器
        
        Args:
            alpha: 学习率
            beta: 动量系数
        """
        self.alpha = alpha
        self.beta = beta
        self._nodes: Dict[str, NodeState] = {}
        self._queues: Dict[str, float] = {}  # 虚拟队列
        self._weights: Dict[str, float] = {}

    def register_node(self, node_id: str, capacity: float = 1.0) -> None:
        """注册节点"""
        self._nodes[node_id] = NodeState(
            node_id=node_id,
            capacity=capacity
        )
        self._queues[node_id] = 0.0
        self._weights[node_id] = 1.0 / len(self._nodes) if self._nodes else 1.0
        logger.info(f"注册节点: {node_id} (容量: {capacity})")

    def unregister_node(self, node_id: str) -> None:
        """注销节点"""
        self._nodes.pop(node_id, None)
        self._queues.pop(node_id, None)
        self._weights.pop(node_id, None)
        self._normalize_weights()

    def _normalize_weights(self) -> None:
        """归一化权重"""
        total = sum(self._weights.values())
        if total > 0:
            for node_id in self._weights:
                self._weights[node_id] /= total

    def update_load(self, node_id: str, load: float, latency_ms: float = 0.0) -> None:
        """更新节点负载"""
        if node_id not in self._nodes:
            return

        node = self._nodes[node_id]
        node.load = load
        node.latency_ms = latency_ms
        node.last_update = datetime.now()

        # 更新虚拟队列
        arrival_rate = load
        service_rate = node.capacity
        self._queues[node_id] = max(0, self._queues[node_id] + arrival_rate - service_rate)

    def route(self, task_weight: float = 1.0) -> Optional[str]:
        """
        路由任务到最佳节点
        
        使用 Lyapunov 稳定性原则选择节点：
        最小化队列长度平方和（Lyapunov 函数）
        """
        if not self._nodes:
            return None

        best_node = None
        best_score = float('inf')

        for node_id, node in self._nodes.items():
            # Lyapunov 函数：队列长度 + 延迟惩罚
            queue = self._queues.get(node_id, 0)
            latency_penalty = node.latency_ms / 100.0
            load_penalty = node.load / node.capacity

            # 稳定性得分（越小越好）
            score = queue * queue + latency_penalty + load_penalty

            if score < best_score:
                best_score = score
                best_node = node_id

        # 更新权重（梯度下降）
        if best_node:
            self._update_weights_lyapunov(best_node)

        return best_node

    def _update_weights_lyapunov(self, selected_node: str) -> None:
        """基于 Lyapunov 稳定性更新权重"""
        for node_id in self._weights:
            queue = self._queues.get(node_id, 0)
            
            if node_id == selected_node:
                # 选中的节点：增加权重
                gradient = -self.alpha * queue
            else:
                # 未选中的节点：减少权重
                gradient = self.alpha * queue

            # 动量更新
            self._weights[node_id] = self.beta * self._weights[node_id] + (1 - self.beta) * gradient

        self._normalize_weights()

    def get_node_stats(self) -> Dict[str, Dict[str, float]]:
        """获取节点统计"""
        return {
            node_id: {
                "load": node.load,
                "capacity": node.capacity,
                "queue": self._queues.get(node_id, 0),
                "weight": self._weights.get(node_id, 0),
                "latency_ms": node.latency_ms
            }
            for node_id, node in self._nodes.items()
        }

    def get_stability_metric(self) -> float:
        """
        获取系统稳定性指标
        
        基于 Lyapunov 函数：所有队列长度的平方和
        越小越稳定
        """
        return sum(q * q for q in self._queues.values())


# 全局路由器
lyapunov_router = LyapunovStableRouter()
