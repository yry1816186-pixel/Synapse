"""
D-Optimal TTA - 测试时适应
零计算开销的边缘设备自适应推理
"""

from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import asyncio
import logging
import math
import random

logger = logging.getLogger(__name__)


@dataclass
class TTAStatistics:
    """TTA 统计信息"""
    batch_size: int
    mean: List[float]
    variance: List[float]
    samples_seen: int = 0


@dataclass
class AdaptationResult:
    """适应结果"""
    adapted: bool
    confidence: float
    statistics: Optional[TTAStatistics] = None


class DOptimalTTA:
    """
    D-Optimal 测试时适应

    零计算开销的边缘设备自适应推理
    通过 D-Optimal 统计稳定 TTA
    """

    def __init__(self, feature_dim: int = 768, momentum: float = 0.9):
        self.feature_dim = feature_dim
        self.momentum = momentum
        self._running_mean: Optional[List[float]] = None
        self._running_var: Optional[List[float]] = None
        self._samples_seen = 0
        self._determinant_history: List[float] = []

    def initialize(self, pretrain_stats: Tuple[List[float], List[float]] = None) -> None:
        """初始化"""
        if pretrain_stats:
            self._running_mean, self._running_var = pretrain_stats
        else:
            # 默认初始化
            self._running_mean = [0.0] * self.feature_dim
            self._running_var = [1.0] * self.feature_dim

        logger.info("D-Optimal TTA 初始化完成")

    async def adapt(self, features: List[List[float]]) -> AdaptationResult:
        """
        自适应更新

        使用 D-Optimal 统计选择最优批次大小
        """
        if not features:
            return AdaptationResult(adapted=False, confidence=0.0)

        batch_size = len(features)
        feature_dim = len(features[0]) if features else 0

        # 计算批次统计
        batch_mean = self._compute_mean(features)
        batch_var = self._compute_variance(features, batch_mean)

        # D-Optimal 准则：最大化协方差矩阵行列式
        determinant = self._compute_determinant(batch_var)
        self._determinant_history.append(determinant)

        # 检查是否应该更新
        should_update = self._d_optimal_check(batch_size, determinant)

        if should_update:
            # EMA 更新
            for i in range(min(feature_dim, self.feature_dim)):
                self._running_mean[i] = (
                    self.momentum * self._running_mean[i] +
                    (1 - self.momentum) * batch_mean[i]
                )
                self._running_var[i] = (
                    self.momentum * self._running_var[i] +
                    (1 - self.momentum) * batch_var[i]
                )

            self._samples_seen += batch_size

        confidence = self._compute_confidence(determinant)

        return AdaptationResult(
            adapted=should_update,
            confidence=confidence,
            statistics=TTAStatistics(
                batch_size=batch_size,
                mean=batch_mean,
                variance=batch_var,
                samples_seen=self._samples_seen
            )
        )

    def _compute_mean(self, features: List[List[float]]) -> List[float]:
        """计算均值"""
        if not features:
            return [0.0] * self.feature_dim

        dim = len(features[0])
        mean = [0.0] * dim

        for feature in features:
            for i in range(dim):
                mean[i] += feature[i]

        return [m / len(features) for m in mean]

    def _compute_variance(self, features: List[List[float]], mean: List[float]) -> List[float]:
        """计算方差"""
        if len(features) < 2:
            return [1.0] * len(mean)

        dim = len(mean)
        var = [0.0] * dim

        for feature in features:
            for i in range(dim):
                var[i] += (feature[i] - mean[i]) ** 2

        return [v / (len(features) - 1) for v in var]

    def _compute_determinant(self, variance: List[float]) -> float:
        """计算 D-Optimal 准则（协方差行列式的近似）"""
        # 简化：使用对角协方差
        log_det = sum(math.log(max(v, 1e-10)) for v in variance)
        return log_det

    def _d_optimal_check(self, batch_size: int, determinant: float) -> bool:
        """D-Optimal 检查：是否应该更新"""
        if len(self._determinant_history) < 3:
            return True

        # 检查行列式是否在增加（信息量增加）
        recent = self._determinant_history[-3:]
        trend = recent[-1] > recent[0]

        # 批次大小越大，更新越激进
        threshold = 0.5 + 0.05 * min(batch_size, 10)

        return trend and random.random() < threshold

    def _compute_confidence(self, determinant: float) -> float:
        """计算置信度"""
        if not self._determinant_history:
            return 0.5

        # 基于行列式变化计算置信度
        avg = sum(self._determinant_history[-10:]) / min(10, len(self._determinant_history))
        if avg == 0:
            return 0.5

        ratio = determinant / avg
        return min(1.0, max(0.0, 0.5 + 0.1 * (ratio - 1)))

    def normalize(self, features: List[float]) -> List[float]:
        """使用当前统计归一化"""
        if not self._running_mean or not self._running_var:
            return features

        normalized = []
        for i, f in enumerate(features):
            if i < len(self._running_var) and self._running_var[i] > 0:
                normalized.append((f - self._running_mean[i]) / math.sqrt(self._running_var[i]))
            else:
                normalized.append(f)

        return normalized

    def get_stats(self) -> Dict[str, Any]:
        """获取统计"""
        return {
            "samples_seen": self._samples_seen,
            "determinant_history": len(self._determinant_history),
            "feature_dim": self.feature_dim
        }


# 全局 TTA 实例
d_optimal_tta = DOptimalTTA()
