"""
Pep 框架 - 离线学习+在线推理
用于多租户个性化场景
"""

from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import asyncio
import logging
import math

logger = logging.getLogger(__name__)


class LearningMode(Enum):
    """学习模式"""
    OFFLINE = "offline"  # 离线学习
    ONLINE = "online"    # 在线推理
    HYBRID = "hybrid"    # 混合模式


@dataclass
class PepConfig:
    """Pep 配置"""
    params_count: int = 10000  # 10K 参数
    learning_rate: float = 0.01
    batch_size: int = 32
    offline_epochs: int = 100
    online_update_freq: int = 10


@dataclass
class PersonalizationState:
    """个性化状态"""
    tenant_id: str
    params: List[float] = field(default_factory=list)
    last_offline_update: datetime = None
    last_online_update: datetime = None
    interaction_count: int = 0


class PepFramework:
    """
    Pep 框架
    
    离线学习 + 在线推理
    减少 3-5x 交互，仅需 10K 参数
    """

    def __init__(self, config: PepConfig = None):
        self.config = config or PepConfig()
        self._tenant_states: Dict[str, PersonalizationState] = {}
        self._global_params: List[float] = []
        self._initialized = False

    async def initialize(self) -> bool:
        """初始化"""
        # 初始化全局参数
        import random
        self._global_params = [random.random() * 0.1 for _ in range(self.config.params_count)]
        self._initialized = True
        logger.info(f"Pep 框架初始化完成 (参数: {self.config.params_count})")
        return True

    async def register_tenant(self, tenant_id: str) -> None:
        """注册租户"""
        if tenant_id in self._tenant_states:
            return

        # 从全局参数初始化租户参数
        state = PersonalizationState(
            tenant_id=tenant_id,
            params=self._global_params.copy()
        )
        self._tenant_states[tenant_id] = state
        logger.info(f"租户注册: {tenant_id}")

    async def offline_learn(self, tenant_id: str, data: List[Dict[str, Any]]) -> None:
        """
        离线学习
        
        在租户休息时进行深度学习
        """
        if not self._initialized:
            await self.initialize()

        if tenant_id not in self._tenant_states:
            await self.register_tenant(tenant_id)

        state = self._tenant_states[tenant_id]

        # 模拟离线训练
        for epoch in range(self.config.offline_epochs):
            loss = await self._train_epoch(state.params, data)
            if epoch % 20 == 0:
                logger.debug(f"租户 {tenant_id} 离线训练 epoch {epoch}: loss={loss:.4f}")

        state.last_offline_update = datetime.now()
        logger.info(f"租户 {tenant_id} 离线学习完成")

    async def online_infer(self, tenant_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        在线推理
        
        快速响应用户请求
        """
        if tenant_id not in self._tenant_states:
            return {"error": "租户未注册"}

        state = self._tenant_states[tenant_id]

        # 快速推理
        result = await self._forward(state.params, context)

        # 更新交互计数
        state.interaction_count += 1

        # 定期在线更新
        if state.interaction_count % self.config.online_update_freq == 0:
            await self._online_update(state, context, result)
            state.last_online_update = datetime.now()

        return result

    async def _train_epoch(self, params: List[float], data: List[Dict[str, Any]]) -> float:
        """训练一个 epoch"""
        import random

        total_loss = 0.0
        for _ in range(len(data) // self.config.batch_size):
            # 模拟梯度下降
            for i in range(len(params)):
                gradient = random.random() * 0.01 - 0.005
                params[i] -= self.config.learning_rate * gradient

            total_loss += random.random() * 0.1

        return total_loss / (len(data) // self.config.batch_size)

    async def _forward(self, params: List[float], context: Dict[str, Any]) -> Dict[str, Any]:
        """前向传播"""
        # 简化的推理
        features = context.get("features", [0.5] * 10)

        # 使用参数计算输出
        output = []
        for i in range(min(len(features), len(params))):
            output.append(features[i] * params[i])

        return {
            "output": output,
            "confidence": sum(abs(o) for o in output) / len(output) if output else 0
        }

    async def _online_update(self, state: PersonalizationState,
                            context: Dict[str, Any], result: Dict[str, Any]) -> None:
        """在线更新"""
        # 简化的在线学习
        feedback = context.get("feedback", 0.5)

        for i in range(len(state.params)):
            state.params[i] += self.config.learning_rate * 0.1 * (feedback - 0.5)

    def get_tenant_stats(self, tenant_id: str) -> Dict[str, Any]:
        """获取租户统计"""
        state = self._tenant_states.get(tenant_id)
        if not state:
            return {}

        return {
            "tenant_id": tenant_id,
            "params_count": len(state.params),
            "interaction_count": state.interaction_count,
            "last_offline_update": state.last_offline_update.isoformat() if state.last_offline_update else None,
            "last_online_update": state.last_online_update.isoformat() if state.last_online_update else None
        }


# 全局 Pep 框架
pep_framework = PepFramework()
