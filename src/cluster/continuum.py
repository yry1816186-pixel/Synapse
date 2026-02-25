"""
计算连续体服务编排 - 借鉴 Computing Continuum 论文
实现边缘到云的协同计算
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import asyncio
import logging

logger = logging.getLogger(__name__)


class ComputeTier(Enum):
    """计算层级"""
    EDGE = "edge"          # 边缘设备
    FOG = "fog"            # 雾计算节点
    CLOUD = "cloud"        # 云端
    HYBRID = "hybrid"      # 混合


@dataclass
class ComputeNode:
    """计算节点"""
    node_id: str
    name: str
    tier: ComputeTier
    cpu_cores: float
    memory_gb: float
    gpu_available: bool = False
    latency_to_cloud_ms: float = 100.0
    current_load: float = 0.0
    status: str = "available"


@dataclass
class ServiceSpec:
    """服务规格"""
    service_id: str
    name: str
    cpu_requirement: float
    memory_requirement: float
    gpu_required: bool = False
    max_latency_ms: float = 1000.0
    priority: int = 5
    data_locality: str = "any"  # any, edge, cloud


@dataclass
class PlacementDecision:
    """放置决策"""
    service_id: str
    node_id: str
    tier: ComputeTier
    estimated_latency_ms: float
    reason: str


class ComputingContinuumOrchestrator:
    """
    计算连续体编排器
    
    实现边缘到云的协同计算
    自动决定服务放置位置
    """

    def __init__(self):
        self._nodes: Dict[str, ComputeNode] = {}
        self._placements: Dict[str, str] = {}  # service_id -> node_id

    def register_node(self, node: ComputeNode) -> None:
        """注册计算节点"""
        self._nodes[node.node_id] = node
        logger.info(f"注册计算节点: {node.name} ({node.tier.value})")

    async def place_service(self, spec: ServiceSpec) -> Optional[PlacementDecision]:
        """放置服务"""
        candidates = []

        for node_id, node in self._nodes.items():
            if node.status != "available":
                continue

            # 检查资源
            if node.cpu_cores < spec.cpu_requirement:
                continue
            if node.memory_gb < spec.memory_requirement:
                continue
            if spec.gpu_required and not node.gpu_available:
                continue

            # 计算得分
            score = self._calculate_score(spec, node)
            candidates.append((node, score))

        if not candidates:
            logger.warning(f"无可用节点: {spec.name}")
            return None

        # 选择最佳节点
        candidates.sort(key=lambda x: x[1], reverse=True)
        best_node = candidates[0][0]

        # 确定层级
        tier = best_node.tier

        # 估算延迟
        if tier == ComputeTier.EDGE:
            latency = 10.0
        elif tier == ComputeTier.FOG:
            latency = 50.0
        else:
            latency = best_node.latency_to_cloud_ms

        decision = PlacementDecision(
            service_id=spec.service_id,
            node_id=best_node.node_id,
            tier=tier,
            estimated_latency_ms=latency,
            reason=f"最优节点: {best_node.name}, 得分: {candidates[0][1]:.2f}"
        )

        self._placements[spec.service_id] = best_node.node_id
        best_node.current_load += spec.cpu_requirement

        logger.info(f"服务放置: {spec.name} -> {best_node.name} ({tier.value})")
        return decision

    def _calculate_score(self, spec: ServiceSpec, node: ComputeNode) -> float:
        """计算节点得分"""
        score = 0.0

        # 延迟因素
        if spec.max_latency_ms < 100:
            # 低延迟需求，优先边缘
            if node.tier == ComputeTier.EDGE:
                score += 50
            elif node.tier == ComputeTier.FOG:
                score += 30
            else:
                score += 10
        elif spec.max_latency_ms < 500:
            # 中等延迟，优先雾
            if node.tier == ComputeTier.FOG:
                score += 40
            elif node.tier == ComputeTier.EDGE:
                score += 35
            else:
                score += 20
        else:
            # 高延迟容忍，优先资源
            if node.tier == ComputeTier.CLOUD:
                score += 30
            elif node.tier == ComputeTier.FOG:
                score += 25
            else:
                score += 20

        # 数据局部性
        if spec.data_locality == "edge" and node.tier == ComputeTier.EDGE:
            score += 30
        elif spec.data_locality == "cloud" and node.tier == ComputeTier.CLOUD:
            score += 30

        # 负载因素
        load_factor = 1.0 - (node.current_load / node.cpu_cores)
        score += load_factor * 20

        # GPU 需求
        if spec.gpu_required and node.gpu_available:
            score += 20

        return score

    async def migrate_service(self, service_id: str, target_node_id: str) -> bool:
        """迁移服务"""
        if service_id not in self._placements:
            return False

        current_node_id = self._placements[service_id]
        current_node = self._nodes.get(current_node_id)
        target_node = self._nodes.get(target_node_id)

        if not target_node:
            return False

        # 更新放置
        self._placements[service_id] = target_node_id

        # 更新负载
        if current_node:
            current_node.current_load = max(0, current_node.current_load - 1)
        target_node.current_load += 1

        logger.info(f"服务迁移: {service_id} -> {target_node.name}")
        return True

    def get_cluster_status(self) -> Dict[str, Any]:
        """获取集群状态"""
        edge_nodes = [n for n in self._nodes.values() if n.tier == ComputeTier.EDGE]
        fog_nodes = [n for n in self._nodes.values() if n.tier == ComputeTier.FOG]
        cloud_nodes = [n for n in self._nodes.values() if n.tier == ComputeTier.CLOUD]

        return {
            "total_nodes": len(self._nodes),
            "edge_nodes": len(edge_nodes),
            "fog_nodes": len(fog_nodes),
            "cloud_nodes": len(cloud_nodes),
            "services_deployed": len(self._placements),
            "tiers": {
                "edge": {"count": len(edge_nodes), "available": sum(1 for n in edge_nodes if n.status == "available")},
                "fog": {"count": len(fog_nodes), "available": sum(1 for n in fog_nodes if n.status == "available")},
                "cloud": {"count": len(cloud_nodes), "available": sum(1 for n in cloud_nodes if n.status == "available")}
            }
        }


# 全局编排器
continuum_orchestrator = ComputingContinuumOrchestrator()
