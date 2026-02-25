"""
Sphere Encoder - 借鉴 Sphere Encoder 论文
用于边缘快速推理
"""

from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import asyncio
import logging
import math

logger = logging.getLogger(__name__)


class EncoderType(Enum):
    """编码器类型"""
    SPHERE = "sphere"
    STANDARD = "standard"
    QUANTIZED = "quantized"


@dataclass
class EncoderConfig:
    """编码器配置"""
    encoder_type: EncoderType = EncoderType.SPHERE
    input_dim: int = 768
    output_dim: int = 256
    normalize: bool = True
    quantize: bool = False


@dataclass
class EncoderResult:
    """编码结果"""
    vector: List[float]
    encoder_type: EncoderType
    latency_ms: float
    dimensions: int


class SphereEncoder:
    """
    Sphere Encoder
    
    借鉴 Sphere Encoder 论文的单步生成编码
    实现低延迟边缘推理
    """

    def __init__(self, config: EncoderConfig = None):
        self.config = config or EncoderConfig()
        self._initialized = False

    async def initialize(self) -> bool:
        """初始化编码器"""
        logger.info(f"初始化 Sphere Encoder (dim: {self.config.input_dim} -> {self.config.output_dim})")
        self._initialized = True
        return True

    async def encode(self, input_vector: List[float]) -> EncoderResult:
        """
        编码向量
        
        使用球面投影实现单步编码
        """
        if not self._initialized:
            await self.initialize()

        start_time = datetime.now()

        # 球面投影编码
        if self.config.encoder_type == EncoderType.SPHERE:
            output = self._sphere_project(input_vector)
        else:
            output = self._standard_encode(input_vector)

        # 归一化
        if self.config.normalize:
            output = self._normalize(output)

        # 量化
        if self.config.quantize:
            output = self._quantize(output)

        latency_ms = (datetime.now() - start_time).total_seconds() * 1000

        return EncoderResult(
            vector=output,
            encoder_type=self.config.encoder_type,
            latency_ms=latency_ms,
            dimensions=len(output)
        )

    def _sphere_project(self, input_vector: List[float]) -> List[float]:
        """
        球面投影
        
        将输入向量投影到超球面
        实现降维同时保持几何结构
        """
        input_dim = len(input_vector)
        output_dim = self.config.output_dim

        if input_dim <= output_dim:
            return input_vector.copy()

        result = []
        step = input_dim / output_dim

        for i in range(output_dim):
            # 球面采样点
            center = int(i * step)
            radius = int(step / 2)

            # 加权平均
            total = 0.0
            weight_sum = 0.0

            for j in range(max(0, center - radius), min(input_dim, center + radius + 1)):
                # 高斯权重
                dist = abs(j - center)
                weight = math.exp(-dist * dist / (2 * radius * radius)) if radius > 0 else 1.0
                total += input_vector[j] * weight
                weight_sum += weight

            result.append(total / weight_sum if weight_sum > 0 else 0.0)

        return result

    def _standard_encode(self, input_vector: List[float]) -> List[float]:
        """标准编码（截断）"""
        output_dim = self.config.output_dim
        if len(input_vector) <= output_dim:
            return input_vector.copy()
        return input_vector[:output_dim]

    def _normalize(self, vector: List[float]) -> List[float]:
        """L2 归一化"""
        norm = math.sqrt(sum(x * x for x in vector))
        if norm > 0:
            return [x / norm for x in vector]
        return vector

    def _quantize(self, vector: List[float]) -> List[float]:
        """量化（8位）"""
        # 简单的线性量化
        min_val = min(vector)
        max_val = max(vector)
        range_val = max_val - min_val if max_val != min_val else 1.0

        return [round((x - min_val) / range_val * 255) / 255.0 * range_val + min_val
                for x in vector]


class FastEncoderPipeline:
    """快速编码流水线"""

    def __init__(self, encoder: SphereEncoder = None):
        self.encoder = encoder or SphereEncoder()
        self._cache: Dict[str, List[float]] = {}
        self._cache_hits = 0
        self._cache_misses = 0

    async def encode_with_cache(self, key: str, input_vector: List[float]) -> EncoderResult:
        """带缓存的编码"""
        # 检查缓存
        cache_key = self._make_cache_key(key, input_vector)
        if cache_key in self._cache:
            self._cache_hits += 1
            return EncoderResult(
                vector=self._cache[cache_key],
                encoder_type=self.encoder.config.encoder_type,
                latency_ms=0.1,
                dimensions=len(self._cache[cache_key])
            )

        self._cache_misses += 1

        # 编码
        result = await self.encoder.encode(input_vector)

        # 缓存结果
        self._cache[cache_key] = result.vector

        return result

    def _make_cache_key(self, key: str, vector: List[float]) -> str:
        """生成缓存键"""
        # 使用向量的哈希
        vec_hash = hash(tuple(round(x, 3) for x in vector[:10]))
        return f"{key}:{vec_hash}"

    def clear_cache(self) -> None:
        """清除缓存"""
        self._cache.clear()
        self._cache_hits = 0
        self._cache_misses = 0

    def get_cache_stats(self) -> Dict[str, int]:
        """获取缓存统计"""
        total = self._cache_hits + self._cache_misses
        hit_rate = self._cache_hits / total if total > 0 else 0
        return {
            "hits": self._cache_hits,
            "misses": self._cache_misses,
            "hit_rate": hit_rate,
            "cache_size": len(self._cache)
        }


# 全局编码器
sphere_encoder = SphereEncoder()
fast_encoder_pipeline = FastEncoderPipeline()
