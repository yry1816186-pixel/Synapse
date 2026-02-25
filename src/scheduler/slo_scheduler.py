"""
SLO 驱动调度器 - 借鉴 SLICE 论文
实现可预测的推理延迟
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import asyncio
import logging
import math

logger = logging.getLogger(__name__)


class Priority(Enum):
    """优先级"""
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4


@dataclass
class SLO:
    """服务级别目标"""
    max_latency_ms: float
    min_throughput: float = 1.0
    availability: float = 0.99


@dataclass
class Task:
    """任务"""
    task_id: str
    name: str
    estimated_duration_ms: float
    priority: Priority = Priority.NORMAL
    slo: Optional[SLO] = None
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


@dataclass
class Worker:
    """工作节点"""
    worker_id: str
    name: str
    capacity: float = 1.0
    current_load: float = 0.0
    avg_latency_ms: float = 100.0
    status: str = "idle"


class SLODrivenScheduler:
    """
    SLO 驱动调度器
    
    借鉴 SLICE 论文
    实现可预测的推理延迟
    """

    def __init__(self):
        self._tasks: Dict[str, Task] = {}
        self._workers: Dict[str, Worker] = {}
        self._queue: List[str] = []
        self._assignments: Dict[str, str] = {}  # task_id -> worker_id
        self._running = False

    def register_worker(self, worker: Worker) -> None:
        """注册工作节点"""
        self._workers[worker.worker_id] = worker
        logger.info(f"注册工作节点: {worker.name}")

    def submit_task(self, task: Task) -> None:
        """提交任务"""
        self._tasks[task.task_id] = task

        # 按优先级插入队列
        inserted = False
        for i, tid in enumerate(self._queue):
            if task.priority.value < self._tasks[tid].priority.value:
                self._queue.insert(i, task.task_id)
                inserted = True
                break

        if not inserted:
            self._queue.append(task.task_id)

        logger.debug(f"任务提交: {task.name} (优先级: {task.priority.name})")

    async def schedule(self) -> Dict[str, str]:
        """执行调度"""
        assignments = {}

        for task_id in self._queue[:]:
            task = self._tasks.get(task_id)
            if not task:
                self._queue.remove(task_id)
                continue

            # 找到最佳工作节点
            best_worker = self._find_best_worker(task)

            if best_worker:
                # 检查 SLO 是否可满足
                if self._can_satisfy_slo(task, best_worker):
                    self._assignments[task_id] = best_worker.worker_id
                    assignments[task_id] = best_worker.worker_id

                    # 更新负载
                    best_worker.current_load += 1
                    best_worker.status = "busy"

                    self._queue.remove(task_id)
                    logger.debug(f"任务分配: {task.name} -> {best_worker.name}")

        return assignments

    def _find_best_worker(self, task: Task) -> Optional[Worker]:
        """找到最佳工作节点"""
        best = None
        best_score = -1

        for worker in self._workers.values():
            # 计算得分
            load_score = 1.0 - (worker.current_load / worker.capacity)
            latency_score = 1.0 - (worker.avg_latency_ms / 1000)

            score = load_score * 0.6 + latency_score * 0.4

            if score > best_score:
                best_score = score
                best = worker

        return best

    def _can_satisfy_slo(self, task: Task, worker: Worker) -> bool:
        """检查 SLO 是否可满足"""
        if not task.slo:
            return True

        # 预估延迟
        estimated_latency = task.estimated_duration_ms + worker.avg_latency_ms

        # 检查最大延迟
        if estimated_latency > task.slo.max_latency_ms:
            return False

        return True

    def task_started(self, task_id: str) -> None:
        """任务开始"""
        task = self._tasks.get(task_id)
        if task:
            task.started_at = datetime.now()

    def task_completed(self, task_id: str, actual_duration_ms: float) -> None:
        """任务完成"""
        task = self._tasks.get(task_id)
        if not task:
            return

        task.completed_at = datetime.now()

        # 更新工作节点延迟估计
        worker_id = self._assignments.get(task_id)
        if worker_id:
            worker = self._workers.get(worker_id)
            if worker:
                # 指数移动平均
                alpha = 0.3
                worker.avg_latency_ms = alpha * actual_duration_ms + (1 - alpha) * worker.avg_latency_ms
                worker.current_load = max(0, worker.current_load - 1)

                if worker.current_load == 0:
                    worker.status = "idle"

    def get_stats(self) -> Dict[str, Any]:
        """获取统计"""
        return {
            "queue_length": len(self._queue),
            "total_tasks": len(self._tasks),
            "total_workers": len(self._workers),
            "active_workers": sum(1 for w in self._workers.values() if w.status == "busy"),
            "assignments": len(self._assignments)
        }

    def get_queue(self) -> List[Dict[str, Any]]:
        """获取队列"""
        return [
            {
                "task_id": tid,
                "name": self._tasks[tid].name,
                "priority": self._tasks[tid].priority.name,
                "estimated_duration_ms": self._tasks[tid].estimated_duration_ms
            }
            for tid in self._queue
            if tid in self._tasks
        ]


# 全局调度器
slo_scheduler = SLODrivenScheduler()
