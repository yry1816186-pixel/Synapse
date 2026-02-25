"""
协作网络 - 人机协作、设备协作、团队协作
"""

from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import asyncio
import logging

logger = logging.getLogger(__name__)


class CollaborationType(Enum):
    """协作类型"""
    HUMAN_MACHINE = "human_machine"    # 人机协作
    DEVICE_DEVICE = "device_device"    # 设备协作
    TEAM_TEAM = "team_team"            # 团队协作
    REGION_REGION = "region_region"    # 区域协作


@dataclass
class Collaborator:
    """协作者"""
    collaborator_id: str
    name: str
    collaborator_type: str  # "human", "device", "team", "region"
    capabilities: List[str] = field(default_factory=list)
    status: str = "available"
    current_task: Optional[str] = None


@dataclass
class CollaborationTask:
    """协作任务"""
    task_id: str
    name: str
    description: str = ""
    collaborators: List[str] = field(default_factory=list)
    status: str = "pending"
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None


@dataclass
class WorkflowStep:
    """工作流步骤"""
    step_id: str
    name: str
    assignee: str  # 协作者 ID
    action: str
    params: Dict[str, Any] = field(default_factory=dict)
    status: str = "pending"
    result: Optional[Dict[str, Any]] = None


class CollaborationNetwork:
    """
    协作网络
    
    实现人、设备、团队之间的协作
    """

    def __init__(self):
        self._collaborators: Dict[str, Collaborator] = {}
        self._tasks: Dict[str, CollaborationTask] = {}
        self._workflows: Dict[str, List[WorkflowStep]] = {}
        self._message_handlers: Dict[str, Callable] = {}

    async def register_collaborator(self, collaborator: Collaborator) -> None:
        """注册协作者"""
        self._collaborators[collaborator.collaborator_id] = collaborator
        logger.info(f"协作者注册: {collaborator.name} ({collaborator.collaborator_type})")

    async def create_task(self, task: CollaborationTask) -> None:
        """创建协作任务"""
        self._tasks[task.task_id] = task
        logger.info(f"任务创建: {task.name}")

        # 通知所有协作者
        for collab_id in task.collaborators:
            await self._notify(collab_id, {
                "type": "task_created",
                "task_id": task.task_id,
                "task_name": task.name
            })

    async def assign_task(self, task_id: str, collaborator_id: str) -> bool:
        """分配任务"""
        task = self._tasks.get(task_id)
        collab = self._collaborators.get(collaborator_id)

        if not task or not collab:
            return False

        if collaborator_id not in task.collaborators:
            task.collaborators.append(collaborator_id)

        collab.current_task = task_id
        logger.info(f"任务分配: {task.name} -> {collab.name}")

        return True

    async def complete_task(self, task_id: str, result: Dict[str, Any] = None) -> bool:
        """完成任务"""
        task = self._tasks.get(task_id)
        if not task:
            return False

        task.status = "completed"
        task.completed_at = datetime.now()

        # 释放协作者
        for collab_id in task.collaborators:
            collab = self._collaborators.get(collab_id)
            if collab and collab.current_task == task_id:
                collab.current_task = None

        logger.info(f"任务完成: {task.name}")
        return True

    async def create_workflow(self, workflow_id: str, steps: List[WorkflowStep]) -> None:
        """创建工作流"""
        self._workflows[workflow_id] = steps
        logger.info(f"工作流创建: {workflow_id} ({len(steps)} 步骤)")

    async def execute_workflow(self, workflow_id: str) -> bool:
        """执行工作流"""
        steps = self._workflows.get(workflow_id)
        if not steps:
            return False

        for step in steps:
            step.status = "running"
            
            # 获取协作者
            collab = self._collaborators.get(step.assignee)
            if not collab:
                step.status = "failed"
                continue

            # 执行动作
            result = await self._execute_step(step, collab)
            step.result = result
            step.status = "completed" if result.get("success") else "failed"

        logger.info(f"工作流执行完成: {workflow_id}")
        return True

    async def _execute_step(self, step: WorkflowStep, collab: Collaborator) -> Dict[str, Any]:
        """执行步骤"""
        # 根据协作者类型执行
        if collab.collaborator_type == "device":
            # 设备执行
            return {"success": True, "message": f"设备 {collab.name} 执行了 {step.action}"}
        elif collab.collaborator_type == "human":
            # 人工确认
            return {"success": True, "message": f"等待 {collab.name} 确认 {step.action}"}
        else:
            return {"success": True}

    async def _notify(self, collaborator_id: str, message: Dict[str, Any]) -> None:
        """通知协作者"""
        handler = self._message_handlers.get(collaborator_id)
        if handler:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(message)
                else:
                    handler(message)
            except Exception as e:
                logger.error(f"通知失败: {e}")

    def on_message(self, collaborator_id: str, handler: Callable) -> None:
        """注册消息处理器"""
        self._message_handlers[collaborator_id] = handler

    def get_available_collaborators(self, capability: str = None) -> List[Collaborator]:
        """获取可用协作者"""
        available = [
            c for c in self._collaborators.values()
            if c.status == "available" and not c.current_task
        ]

        if capability:
            available = [
                c for c in available
                if capability in c.capabilities
            ]

        return available

    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """获取任务状态"""
        task = self._tasks.get(task_id)
        if not task:
            return None

        return {
            "task_id": task.task_id,
            "name": task.name,
            "status": task.status,
            "collaborators": len(task.collaborators),
            "created_at": task.created_at.isoformat(),
            "completed_at": task.completed_at.isoformat() if task.completed_at else None
        }


# 全局协作网络
collaboration_network = CollaborationNetwork()
