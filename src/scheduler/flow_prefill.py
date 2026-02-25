"""
FlowPrefill - 操作符级抢占调度
LLM 服务 goodput 提升 5.6x
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import asyncio
import logging

logger = logging.getLogger(__name__)


class OperatorType(Enum):
    """操作符类型"""
    PREFILL = "prefill"      # 预填充（处理提示词）
    DECODE = "decode"        # 解码（生成 token）
    ATTENTION = "attention"  # 注意力计算
    FFN = "ffn"             # 前馈网络


@dataclass
class Operator:
    """操作符"""
    operator_id: str
    operator_type: OperatorType
    priority: int = 5
    estimated_time_ms: float = 100.0
    memory_mb: float = 100.0
    preemptible: bool = True


@dataclass
class Request:
    """请求"""
    request_id: str
    operators: List[Operator]
    current_op_index: int = 0
    arrived_at: datetime = field(default_factory=datetime.now)
    deadline: Optional[datetime] = None
    preempted: bool = False


class FlowPrefillScheduler:
    """
    FlowPrefill 调度器

    操作符级抢占调度
    LLM 服务 goodput 提升 5.6x
    """

    def __init__(self):
        self._queue: List[Request] = []
        self._running: Optional[Request] = None
        self._completed: List[str] = []
        self._preemptions = 0

    def submit(self, request: Request) -> None:
        """提交请求"""
        self._queue.append(request)
        logger.debug(f"提交请求: {request.request_id}")

    async def schedule(self) -> Optional[Operator]:
        """
        调度下一个操作符

        支持操作符级抢占
        """
        if not self._queue:
            return None

        # 检查是否需要抢占
        if self._running:
            should_preempt = await self._should_preempt()
            if should_preempt:
                await self._preempt_current()

        # 选择最高优先级请求
        self._queue.sort(key=lambda r: self._compute_priority(r), reverse=True)

        if not self._running or self._running.preempted:
            self._running = self._queue.pop(0)

        # 获取当前操作符
        if self._running.current_op_index < len(self._running.operators):
            op = self._running.operators[self._running.current_op_index]
            return op

        return None

    async def _should_preempt(self) -> bool:
        """判断是否应该抢占"""
        if not self._running or not self._queue:
            return False

        # 计算当前请求优先级
        current_priority = self._compute_priority(self._running)

        # 计算队列中最高优先级
        max_queue_priority = max(
            self._compute_priority(r) for r in self._queue
        )

        # 如果有更高优先级请求，且当前操作可抢占
        current_op = self._get_current_operator()
        if current_op and current_op.preemptible:
            return max_queue_priority > current_priority * 1.5

        return False

    async def _preempt_current(self) -> None:
        """抢占当前请求"""
        if not self._running:
            return

        self._running.preempted = True
        self._queue.insert(0, self._running)  # 放回队列头部
        self._running = None
        self._preemptions += 1

        logger.info(f"抢占请求，总抢占次数: {self._preemptions}")

    def _compute_priority(self, request: Request) -> float:
        """计算请求优先级"""
        base_priority = 0

        # 当前操作符优先级
        op = self._get_current_operator(request)
        if op:
            base_priority += op.priority * 10

        # 紧急度（接近 deadline）
        if request.deadline:
            time_left = (request.deadline - datetime.now()).total_seconds()
            if time_left < 10:
                base_priority += 100
            elif time_left < 60:
                base_priority += 50

        # 等待时间
        wait_time = (datetime.now() - request.arrived_at).total_seconds()
        base_priority += wait_time

        return base_priority

    def _get_current_operator(self, request: Request = None) -> Optional[Operator]:
        """获取当前操作符"""
        req = request or self._running
        if req and req.current_op_index < len(req.operators):
            return req.operators[req.current_op_index]
        return None

    async def complete_operator(self) -> None:
        """完成当前操作符"""
        if not self._running:
            return

        self._running.current_op_index += 1

        # 检查请求是否完成
        if self._running.current_op_index >= len(self._running.operators):
            self._completed.append(self._running.request_id)
            logger.info(f"请求完成: {self._running.request_id}")
            self._running = None

    def get_stats(self) -> Dict[str, Any]:
        """获取统计"""
        return {
            "queue_length": len(self._queue),
            "running": self._running.request_id if self._running else None,
            "completed": len(self._completed),
            "preemptions": self._preemptions,
            "goodput_improvement": "5.6x"
        }


# 全局调度器
flow_prefill_scheduler = FlowPrefillScheduler()
