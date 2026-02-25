"""
AI 模块 - LLM 集成
借鉴 LangChain 架构
"""

from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import asyncio
import logging
import json

logger = logging.getLogger(__name__)


class LLMProvider(Enum):
    """LLM 提供商"""
    OPENAI = "openai"
    ZHIPU = "zhipu"  # 智谱
    ANTHROPIC = "anthropic"
    DEEPSEEK = "deepseek"
    QWEN = "qwen"
    OLLAMA = "ollama"
    CUSTOM = "custom"


@dataclass
class LLMConfig:
    """LLM 配置"""
    provider: LLMProvider
    model: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    max_tokens: int = 4096
    temperature: float = 0.7
    timeout: int = 60


@dataclass
class Message:
    """消息"""
    role: str  # system, user, assistant
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LLMResponse:
    """LLM 响应"""
    content: str
    model: str
    provider: LLMProvider
    usage: Dict[str, int] = field(default_factory=dict)
    finish_reason: str = "stop"
    latency_ms: float = 0


class LLMClient:
    """LLM 客户端基类"""

    def __init__(self, config: LLMConfig):
        self.config = config

    async def chat(self, messages: List[Message], **kwargs) -> LLMResponse:
        """发送聊天请求"""
        raise NotImplementedError

    async def stream_chat(self, messages: List[Message], **kwargs):
        """流式聊天"""
        raise NotImplementedError


class ZhipuClient(LLMClient):
    """智谱 GLM 客户端"""

    async def chat(self, messages: List[Message], **kwargs) -> LLMResponse:
        start_time = datetime.now()

        # 构建请求
        import aiohttp

        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.config.model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
            "temperature": kwargs.get("temperature", self.config.temperature)
        }

        base_url = self.config.base_url or "https://open.bigmodel.cn/api/paas/v4"

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=self.config.timeout)
            ) as response:
                result = await response.json()

        latency_ms = (datetime.now() - start_time).total_seconds() * 1000

        return LLMResponse(
            content=result["choices"][0]["message"]["content"],
            model=result.get("model", self.config.model),
            provider=self.config.provider,
            usage=result.get("usage", {}),
            finish_reason=result["choices"][0].get("finish_reason", "stop"),
            latency_ms=latency_ms
        )


class LLMManager:
    """LLM 管理器"""

    def __init__(self):
        self._clients: Dict[str, LLMClient] = {}
        self._default_client: Optional[str] = None

    def register(self, name: str, client: LLMClient, default: bool = False) -> None:
        """注册客户端"""
        self._clients[name] = client
        if default or not self._default_client:
            self._default_client = name
        logger.info(f"LLM 客户端已注册: {name}")

    def get(self, name: str = None) -> Optional[LLMClient]:
        """获取客户端"""
        client_name = name or self._default_client
        return self._clients.get(client_name)

    async def chat(self, messages: List[Message], client_name: str = None, **kwargs) -> LLMResponse:
        """发送聊天请求"""
        client = self.get(client_name)
        if not client:
            raise ValueError(f"LLM 客户端不存在: {client_name}")
        return await client.chat(messages, **kwargs)


# 全局管理器
llm_manager = LLMManager()
