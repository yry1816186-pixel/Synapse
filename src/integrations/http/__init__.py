"""
HTTP 集成 - RESTful/Webhook 支持
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
import asyncio
import logging
import json

logger = logging.getLogger(__name__)


@dataclass
class WebhookConfig:
    """Webhook 配置"""
    url: str
    method: str = "POST"
    headers: Dict[str, str] = field(default_factory=dict)
    timeout: int = 30
    retry_count: int = 3
    retry_delay: int = 1


@dataclass
class WebhookLog:
    """Webhook 日志"""
    webhook_id: str
    url: str
    status_code: int
    duration_ms: float
    success: bool
    error: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)


class HTTPClient:
    """HTTP 客户端"""

    def __init__(self):
        self._session = None

    async def request(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
        """发送 HTTP 请求"""
        import aiohttp

        timeout = kwargs.pop("timeout", 30)

        try:
            async with aiohttp.ClientSession() as session:
                async with session.request(
                    method, url, timeout=aiohttp.ClientTimeout(total=timeout), **kwargs
                ) as response:
                    body = await response.text()
                    return {
                        "status_code": response.status,
                        "headers": dict(response.headers),
                        "body": body,
                        "success": 200 <= response.status < 300
                    }
        except asyncio.TimeoutError:
            return {"success": False, "error": "timeout"}
        except Exception as e:
            return {"success": False, "error": str(e)}


class WebhookManager:
    """Webhook 管理器"""

    def __init__(self):
        self._webhooks: Dict[str, WebhookConfig] = {}
        self._logs: List[WebhookLog] = []
        self._http_client = HTTPClient()

    async def register(self, webhook_id: str, config: WebhookConfig) -> bool:
        """注册 Webhook"""
        self._webhooks[webhook_id] = config
        logger.info(f"Webhook 已注册: {webhook_id} -> {config.url}")
        return True

    async def trigger(self, webhook_id: str, payload: Dict[str, Any]) -> WebhookLog:
        """触发 Webhook"""
        config = self._webhooks.get(webhook_id)
        if not config:
            return WebhookLog(
                webhook_id=webhook_id, url="", status_code=0,
                duration_ms=0, success=False, error="webhook not found"
            )

        start_time = datetime.now()

        # 带重试的发送
        for attempt in range(config.retry_count):
            result = await self._http_client.request(
                method=config.method,
                url=config.url,
                headers=config.headers,
                json=payload,
                timeout=config.timeout
            )

            if result.get("success"):
                break

            if attempt < config.retry_count - 1:
                await asyncio.sleep(config.retry_delay)

        duration_ms = (datetime.now() - start_time).total_seconds() * 1000

        log = WebhookLog(
            webhook_id=webhook_id,
            url=config.url,
            status_code=result.get("status_code", 0),
            duration_ms=duration_ms,
            success=result.get("success", False),
            error=result.get("error")
        )

        self._logs.append(log)
        logger.info(f"Webhook 触发: {webhook_id} - {log.status_code}")

        return log

    async def trigger_all(self, payload: Dict[str, Any]) -> List[WebhookLog]:
        """触发所有 Webhook"""
        tasks = [self.trigger(wid, payload) for wid in self._webhooks]
        return await asyncio.gather(*tasks)

    def get_logs(self, webhook_id: str = None, limit: int = 100) -> List[WebhookLog]:
        """获取日志"""
        logs = self._logs
        if webhook_id:
            logs = [l for l in logs if l.webhook_id == webhook_id]
        return logs[-limit:]


# 全局管理器
webhook_manager = WebhookManager()
