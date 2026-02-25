"""
边云协同推理 - 基于最新论文优化
借鉴 Floe、ML-ECS 架构
"""

from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import asyncio
import logging
import json

logger = logging.getLogger(__name__)


class InferenceLocation(Enum):
    """推理位置"""
    EDGE = "edge"      # 边缘端（本地）
    CLOUD = "cloud"    # 云端
    AUTO = "auto"      # 自动选择


@dataclass
class InferenceRequest:
    """推理请求"""
    request_id: str
    model: str
    input_data: Any
    max_latency_ms: float = 500.0
    privacy_level: str = "normal"  # low, normal, high
    priority: int = 5
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class InferenceResult:
    """推理结果"""
    request_id: str
    output: Any
    location: InferenceLocation
    latency_ms: float
    confidence: float = 1.0
    model: str = ""
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class EdgeModel:
    """边缘模型"""
    name: str
    model_type: str  # "detection", "classification", "nlp"
    size_mb: float
    inference_time_ms: float
    accuracy: float
    memory_mb: float
    loaded: bool = False


class EdgeInferenceEngine:
    """边缘推理引擎"""

    def __init__(self):
        self._models: Dict[str, EdgeModel] = {}
        self._memory_limit_mb: float = 4096  # 4GB
        self._current_memory_mb: float = 0

    def register_model(self, model: EdgeModel) -> bool:
        """注册边缘模型"""
        if model.memory_mb + self._current_memory_mb > self._memory_limit_mb:
            logger.warning(f"内存不足，无法加载模型: {model.name}")
            return False

        self._models[model.name] = model
        self._current_memory_mb += model.memory_mb
        logger.info(f"注册边缘模型: {model.name} ({model.size_mb}MB)")
        return True

    async def infer(self, request: InferenceRequest) -> Optional[InferenceResult]:
        """边缘推理"""
        model = self._models.get(request.model)
        if not model:
            return None

        start_time = datetime.now()

        # 模拟推理
        await asyncio.sleep(model.inference_time_ms / 1000)

        latency_ms = (datetime.now() - start_time).total_seconds() * 1000

        return InferenceResult(
            request_id=request.request_id,
            output={"result": "edge_inference"},
            location=InferenceLocation.EDGE,
            latency_ms=latency_ms,
            model=model.name
        )

    def can_handle(self, model_name: str) -> bool:
        """检查是否能处理"""
        return model_name in self._models

    @property
    def available_models(self) -> List[str]:
        return list(self._models.keys())


class CloudInferenceClient:
    """云端推理客户端"""

    def __init__(self, endpoint: str = None):
        self.endpoint = endpoint or "https://api.zhipu.ai"
        self._api_key: Optional[str] = None

    def set_api_key(self, api_key: str) -> None:
        self._api_key = api_key

    async def infer(self, request: InferenceRequest) -> Optional[InferenceResult]:
        """云端推理"""
        import aiohttp

        start_time = datetime.now()

        # 模拟云端推理
        await asyncio.sleep(0.2)  # 网络延迟

        latency_ms = (datetime.now() - start_time).total_seconds() * 1000

        return InferenceResult(
            request_id=request.request_id,
            output={"result": "cloud_inference"},
            location=InferenceLocation.CLOUD,
            latency_ms=latency_ms,
            model=request.model
        )


class EdgeCloudRouter:
    """边云协同路由器 - 借鉴 Floe 论文"""

    def __init__(self):
        self._edge_engine = EdgeInferenceEngine()
        self._cloud_client = CloudInferenceClient()
        self._latency_threshold_ms: float = 200.0
        self._privacy_sensitive_models: List[str] = []

    def configure(self, latency_threshold_ms: float = 200.0,
                  privacy_models: List[str] = None) -> None:
        """配置路由策略"""
        self._latency_threshold_ms = latency_threshold_ms
        self._privacy_sensitive_models = privacy_models or []

    def route(self, request: InferenceRequest) -> InferenceLocation:
        """路由决策"""
        # 1. 隐私优先：敏感数据强制边缘
        if request.privacy_level == "high":
            return InferenceLocation.EDGE

        if request.model in self._privacy_sensitive_models:
            return InferenceLocation.EDGE

        # 2. 延迟优先：低延迟要求检查边缘
        if request.max_latency_ms <= self._latency_threshold_ms:
            if self._edge_engine.can_handle(request.model):
                return InferenceLocation.EDGE

        # 3. 模型可用性：边缘有模型优先
        if self._edge_engine.can_handle(request.model):
            return InferenceLocation.EDGE

        # 4. 默认云端
        return InferenceLocation.CLOUD

    async def infer(self, request: InferenceRequest) -> InferenceResult:
        """执行推理（自动路由）"""
        location = self.route(request)

        if location == InferenceLocation.EDGE:
            result = await self._edge_engine.infer(request)
            if result:
                return result
            # 边缘失败，回退云端
            logger.info("边缘推理失败，回退云端")
            location = InferenceLocation.CLOUD

        return await self._cloud_client.infer(request)

    def register_edge_model(self, model: EdgeModel) -> bool:
        """注册边缘模型"""
        return self._edge_engine.register_model(model)

    @property
    def edge_models(self) -> List[str]:
        return self._edge_engine.available_models


# 全局路由器
edge_cloud_router = EdgeCloudRouter()
