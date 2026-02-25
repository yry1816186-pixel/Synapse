"""
DRAMA - 动态自适应模块分配
用于能源效率优化
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import asyncio
import logging
import math

logger = logging.getLogger(__name__)


class ModuleState(Enum):
    """模块状态"""
    ACTIVE = "active"
    IDLE = "idle"
    SLEEP = "sleep"


@dataclass
class Module:
    """模块"""
    module_id: str
    name: str
    state: ModuleState = ModuleState.IDLE
    power_consumption: float = 1.0  # 瓦特
    importance: float = 0.5
    last_active: datetime = None


@dataclass
class DRAMAConfig:
    """DRAMA 配置"""
    power_budget: float = 100.0  # 瓦特
    activation_threshold: float = 0.3
    deactivation_threshold: float = 0.1
    min_active_time: float = 5.0  # 秒


class DRAMAManager:
    """
    DRAMA - 动态自适应模块分配
    
    自适应门控，动态模块分配
    提升能源效率
    """

    def __init__(self, config: DRAMAConfig = None):
        self.config = config or DRAMAConfig()
        self._modules: Dict[str, Module] = {}
        self._gates: Dict[str, float] = {}  # 门控值
        self._power_history: List[float] = []

    def register_module(self, module: Module) -> None:
        """注册模块"""
        self._modules[module.module_id] = module
        self._gates[module.module_id] = 0.0
        logger.info(f"注册模块: {module.name}")

    async def allocate(self, context: Dict[str, Any]) -> Dict[str, ModuleState]:
        """
        动态分配模块
        
        根据上下文和能源预算决定模块状态
        """
        # 计算每个模块的重要性
        importance = await self._compute_importance(context)

        # 更新门控值
        for module_id, imp in importance.items():
            if module_id in self._gates:
                # 平滑更新
                self._gates[module_id] = 0.9 * self._gates[module_id] + 0.1 * imp

        # 分配模块状态
        allocation = {}
        total_power = 0.0

        # 按重要性排序
        sorted_modules = sorted(
            self._modules.items(),
            key=lambda x: importance.get(x[0], 0),
            reverse=True
        )

        for module_id, module in sorted_modules:
            gate = self._gates.get(module_id, 0)

            if gate >= self.config.activation_threshold:
                # 激活模块
                if total_power + module.power_consumption <= self.config.power_budget:
                    module.state = ModuleState.ACTIVE
                    total_power += module.power_consumption
                else:
                    module.state = ModuleState.IDLE
            elif gate >= self.config.deactivation_threshold:
                module.state = ModuleState.IDLE
            else:
                module.state = ModuleState.SLEEP

            allocation[module_id] = module.state
            module.last_active = datetime.now()

        self._power_history.append(total_power)

        return allocation

    async def _compute_importance(self, context: Dict[str, Any]) -> Dict[str, float]:
        """计算模块重要性"""
        importance = {}

        for module_id, module in self._modules.items():
            # 基于上下文计算重要性
            base_importance = module.importance

            # 根据设备类型调整
            device_type = context.get("device_type", "")
            if device_type in module.name.lower():
                base_importance += 0.3

            # 根据时间调整
            hour = datetime.now().hour
            if 6 <= hour <= 22:  # 白天
                if "security" in module.name.lower():
                    base_importance += 0.2

            importance[module_id] = min(1.0, base_importance)

        return importance

    def get_power_stats(self) -> Dict[str, Any]:
        """获取能耗统计"""
        if not self._power_history:
            return {"samples": 0}

        active_modules = sum(1 for m in self._modules.values()
                            if m.state == ModuleState.ACTIVE)
        idle_modules = sum(1 for m in self._modules.values()
                          if m.state == ModuleState.IDLE)
        sleep_modules = sum(1 for m in self._modules.values()
                           if m.state == ModuleState.SLEEP)

        return {
            "samples": len(self._power_history),
            "avg_power": sum(self._power_history) / len(self._power_history),
            "last_power": self._power_history[-1],
            "power_budget": self.config.power_budget,
            "active_modules": active_modules,
            "idle_modules": idle_modules,
            "sleep_modules": sleep_modules,
            "efficiency": self._power_history[-1] / self.config.power_budget * 100
        }

    async def optimize(self) -> Dict[str, Any]:
        """优化能耗"""
        # 获取当前统计
        stats = self.get_power_stats()

        # 调整阈值以优化
        if stats.get("efficiency", 0) > 90:
            # 能耗过高，提高激活阈值
            self.config.activation_threshold = min(0.8, self.config.activation_threshold + 0.05)
            logger.info("提高激活阈值以节省能源")
        elif stats.get("efficiency", 0) < 50:
            # 能耗较低，降低激活阈值
            self.config.activation_threshold = max(0.1, self.config.activation_threshold - 0.05)
            logger.info("降低激活阈值以提高性能")

        return {
            "optimization": "completed",
            "new_threshold": self.config.activation_threshold
        }


# 全局 DRAMA 管理器
drama_manager = DRAMAManager()
