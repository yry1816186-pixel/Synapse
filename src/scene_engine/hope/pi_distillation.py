"""
PI Distillation - 借鉴 PI Distillation 论文
用于 Hope 持续学习模块
"""

from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from datetime import datetime
import asyncio
import logging
import math
import random

logger = logging.getLogger(__name__)


@dataclass
class DistillationConfig:
    """蒸馏配置"""
    temperature: float = 2.0
    alpha: float = 0.7  # 蒸馏损失权重
    beta: float = 0.3   # 硬标签损失权重
    learning_rate: float = 0.01


@dataclass
class KnowledgeState:
    """知识状态"""
    state_id: str
    features: List[float] = field(default_factory=list)
    logits: List[float] = field(default_factory=list)
    confidence: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)


class PrivilegedInformationDistillation:
    """
    特权信息蒸馏
    
    借鉴 PI Distillation 论文
    用于 Hope 模块的知识迁移
    """

    def __init__(self, config: DistillationConfig = None):
        self.config = config or DistillationConfig()
        self._teacher_state: Optional[KnowledgeState] = None
        self._student_state: Optional[KnowledgeState] = None
        self._training_history: List[float] = []

    def set_teacher(self, state: KnowledgeState) -> None:
        """设置教师模型状态"""
        self._teacher_state = state

    async def distill(self, student_features: List[float],
                     hard_labels: List[float] = None) -> KnowledgeState:
        """
        蒸馏知识
        
        将教师模型的特权信息迁移到学生模型
        """
        if not self._teacher_state:
            # 无教师，直接返回
            return KnowledgeState(
                state_id="student",
                features=student_features
            )

        # 软标签（教师输出）
        soft_labels = self._teacher_state.logits

        # 硬标签（如果有）
        if hard_labels is None:
            hard_labels = [0.0] * len(soft_labels)

        # 蒸馏训练
        student_logits = await self._forward(student_features)

        # 计算蒸馏损失
        distill_loss = self._distillation_loss(student_logits, soft_labels)
        hard_loss = self._hard_loss(student_logits, hard_labels)

        # 总损失
        total_loss = (self.config.alpha * distill_loss + 
                      self.config.beta * hard_loss)

        # 记录训练历史
        self._training_history.append(total_loss)

        # 更新学生状态
        self._student_state = KnowledgeState(
            state_id="student",
            features=student_features,
            logits=student_logits,
            confidence=1.0 - min(total_loss, 1.0)
        )

        return self._student_state

    async def _forward(self, features: List[float]) -> List[float]:
        """前向传播"""
        # 简化的前向传播
        # 实际应用中替换为神经网络
        dim = len(self._teacher_state.logits) if self._teacher_state else 10

        logits = []
        for i in range(dim):
            # 基于特征计算 logit
            logit = sum(features) / max(len(features), 1) * (1 + 0.1 * random.random())
            logits.append(logit)

        return logits

    def _distillation_loss(self, student_logits: List[float],
                          teacher_logits: List[float]) -> float:
        """
        蒸馏损失（KL 散度）
        
        使用温度缩放的软标签
        """
        if not student_logits or not teacher_logits:
            return 0.0

        # 温度缩放
        temp = self.config.temperature
        student_soft = self._softmax([l / temp for l in student_logits])
        teacher_soft = self._softmax([l / temp for l in teacher_logits])

        # KL 散度
        kl_div = 0.0
        for s, t in zip(student_soft, teacher_soft):
            if t > 0 and s > 0:
                kl_div += t * math.log(t / s)

        return kl_div

    def _hard_loss(self, logits: List[float], labels: List[float]) -> float:
        """硬标签损失（交叉熵）"""
        if not logits or not labels:
            return 0.0

        probs = self._softmax(logits)
        loss = 0.0

        for p, l in zip(probs, labels):
            if l > 0 and p > 0:
                loss -= l * math.log(p)

        return loss

    def _softmax(self, logits: List[float]) -> List[float]:
        """Softmax"""
        max_logit = max(logits) if logits else 0
        exp_logits = [math.exp(l - max_logit) for l in logits]
        sum_exp = sum(exp_logits)

        if sum_exp == 0:
            return [1.0 / len(logits)] * len(logits)

        return [e / sum_exp for e in exp_logits]

    def get_training_stats(self) -> Dict[str, Any]:
        """获取训练统计"""
        if not self._training_history:
            return {"epochs": 0}

        return {
            "epochs": len(self._training_history),
            "last_loss": self._training_history[-1],
            "avg_loss": sum(self._training_history) / len(self._training_history),
            "min_loss": min(self._training_history),
            "trend": "improving" if len(self._training_history) > 1 and 
                     self._training_history[-1] < self._training_history[-2] else "stable"
        }


# 全局蒸馏器
pi_distillation = PrivilegedInformationDistillation()
