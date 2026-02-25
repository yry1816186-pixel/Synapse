"""
热力学启发的集群治理 - 借鉴 TEG 论文
用于大规模分布式系统管理
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import asyncio
import logging
import math
import random

logger = logging.getLogger(__name__)


class NodeState(Enum):
    """节点状态"""
    HOT = "hot"       # 高负载
    WARM = "warm"     # 中等负载
    COOL = "cool"     # 低负载
    COLD = "cold"     # 空闲


@dataclass
class ThermalNode:
    """热力学节点"""
    node_id: str
    name: str
    temperature: float = 0.5  # 0-1, 0=冷, 1=热
    entropy: float = 0.0
    energy: float = 1.0
    state: NodeState = NodeState.COOL


@dataclass
class ThermalBalance:
    """热平衡状态"""
    total_energy: float
    average_temperature: float
    entropy: float
    equilibrium: bool


class ThermodynamicGovernance:
    """
    热力学启发的集群治理

    借鉴 TEG 论文
    用热力学原理管理分布式系统
    """

    def __init__(self, target_temperature: float = 0.5):
        self.target_temperature = target_temperature
        self._nodes: Dict[str, ThermalNode] = {}
        self._heat_transfer_rate = 0.1

    def register_node(self, node: ThermalNode) -> None:
        """注册节点"""
        self._nodes[node.node_id] = node
        logger.info(f"注册热力学节点: {node.name}")

    async def update_temperature(self, node_id: str, load: float) -> None:
        """更新节点温度"""
        node = self._nodes.get(node_id)
        if not node:
            return

        # 温度 = 负载 * 热量
        node.temperature = min(1.0, max(0.0, load))

        # 更新状态
        if node.temperature > 0.8:
            node.state = NodeState.HOT
        elif node.temperature > 0.5:
            node.state = NodeState.WARM
        elif node.temperature > 0.2:
            node.state = NodeState.COOL
        else:
            node.state = NodeState.COLD

        # 计算熵
        node.entropy = -node.temperature * math.log(node.temperature + 0.001) if node.temperature > 0 else 0

    async def transfer_heat(self) -> None:
        """热量传递 - 实现热平衡"""
        if len(self._nodes) < 2:
            return

        # 计算平均温度
        avg_temp = sum(n.temperature for n in self._nodes.values()) / len(self._nodes)

        # 热量从高温流向低温
        for node in self._nodes.values():
            diff = avg_temp - node.temperature
            node.temperature += diff * self._heat_transfer_rate
            node.temperature = min(1.0, max(0.0, node.temperature))

    async def rebalance(self) -> ThermalBalance:
        """重新平衡"""
        # 执行热量传递
        await self.transfer_heat()

        # 计算系统状态
        total_energy = sum(n.energy for n in self._nodes.values())
        avg_temp = sum(n.temperature for n in self._nodes.values()) / len(self._nodes)
        total_entropy = sum(n.entropy for n in self._nodes.values())

        # 检查是否平衡
        equilibrium = all(
            abs(n.temperature - self.target_temperature) < 0.2
            for n in self._nodes.values()
        )

        return ThermalBalance(
            total_energy=total_energy,
            average_temperature=avg_temp,
            entropy=total_entropy,
            equilibrium=equilibrium
        )

    def get_hottest_nodes(self, count: int = 3) -> List[ThermalNode]:
        """获取最热节点"""
        sorted_nodes = sorted(
            self._nodes.values(),
            key=lambda n: n.temperature,
            reverse=True
        )
        return sorted_nodes[:count]

    def get_coldest_nodes(self, count: int = 3) -> List[ThermalNode]:
        """获取最冷节点"""
        sorted_nodes = sorted(
            self._nodes.values(),
            key=lambda n: n.temperature
        )
        return sorted_nodes[:count]

    def suggest_migration(self) -> Optional[Dict[str, str]]:
        """建议迁移"""
        hot = self.get_hottest_nodes(1)
        cold = self.get_coldest_nodes(1)

        if hot and cold and hot[0].temperature - cold[0].temperature > 0.3:
            return {
                "from": hot[0].node_id,
                "to": cold[0].node_id,
                "reason": f"热平衡: {hot[0].temperature:.2f} -> {cold[0].temperature:.2f}"
            }

        return None

    def get_status(self) -> Dict[str, Any]:
        """获取状态"""
        # 简化：直接计算，不调用异步方法
        avg_temp = sum(n.temperature for n in self._nodes.values()) / len(self._nodes) if self._nodes else 0

        return {
            "nodes": len(self._nodes),
            "average_temperature": avg_temp,
            "hottest": [n.node_id for n in self.get_hottest_nodes()],
            "coldest": [n.node_id for n in self.get_coldest_nodes()],
            "equilibrium": True  # 简化
        }


# 全局治理器
thermal_governance = ThermodynamicGovernance()
