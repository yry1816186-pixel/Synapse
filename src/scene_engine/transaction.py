"""
事务性场景执行 - 借鉴 Atomix 论文
保证场景执行的原子性和一致性
"""

from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import asyncio
import logging

logger = logging.getLogger(__name__)


class TransactionState(Enum):
    """事务状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMMITTED = "committed"
    ABORTED = "aborted"
    ROLLING_BACK = "rolling_back"


@dataclass
class TransactionLog:
    """事务日志"""
    transaction_id: str
    action_id: str
    action_type: str
    state: TransactionState
    snapshot: Dict[str, Any] = field(default_factory=dict)  # 执行前快照
    result: Optional[Dict[str, Any]] = None
    timestamp: datetime = field(default_factory=datetime.now)


class SceneTransaction:
    """场景事务"""

    def __init__(self, transaction_id: str):
        self.transaction_id = transaction_id
        self._state = TransactionState.PENDING
        self._logs: List[TransactionLog] = []
        self._actions: List[Callable] = []
        self._rollback_actions: List[Callable] = []

    def add_action(self, action: Callable, rollback: Callable = None) -> None:
        """添加动作"""
        self._actions.append(action)
        self._rollback_actions.append(rollback)

    async def execute(self) -> bool:
        """执行事务"""
        self._state = TransactionState.RUNNING

        for i, action in enumerate(self._actions):
            try:
                # 记录执行前状态
                log = TransactionLog(
                    transaction_id=self.transaction_id,
                    action_id=f"action_{i}",
                    action_type=action.__name__ if hasattr(action, '__name__') else "unknown",
                    state=TransactionState.RUNNING
                )

                # 执行动作
                result = await action() if asyncio.iscoroutinefunction(action) else action()
                log.result = result
                log.state = TransactionState.COMMITTED
                self._logs.append(log)

            except Exception as e:
                logger.error(f"事务执行失败: {e}")
                log.state = TransactionState.ABORTED
                self._logs.append(log)

                # 回滚
                await self._rollback(i)
                self._state = TransactionState.ABORTED
                return False

        self._state = TransactionState.COMMITTED
        return True

    async def _rollback(self, failed_index: int) -> None:
        """回滚已执行的动作"""
        self._state = TransactionState.ROLLING_BACK

        for i in range(failed_index - 1, -1, -1):
            rollback = self._rollback_actions[i]
            if rollback:
                try:
                    log = self._logs[i]
                    if asyncio.iscoroutinefunction(rollback):
                        await rollback(log.snapshot)
                    else:
                        rollback(log.snapshot)
                    logger.info(f"回滚动作 {i}")
                except Exception as e:
                    logger.error(f"回滚失败: {e}")

    @property
    def state(self) -> TransactionState:
        return self._state

    @property
    def logs(self) -> List[TransactionLog]:
        return self._logs


class TransactionManager:
    """事务管理器"""

    def __init__(self):
        self._transactions: Dict[str, SceneTransaction] = {}
        self._transaction_counter = 0

    def begin_transaction(self) -> SceneTransaction:
        """开始新事务"""
        self._transaction_counter += 1
        tx_id = f"tx_{datetime.now().strftime('%Y%m%d%H%M%S')}_{self._transaction_counter}"

        transaction = SceneTransaction(tx_id)
        self._transactions[tx_id] = transaction

        logger.info(f"开始事务: {tx_id}")
        return transaction

    def get_transaction(self, tx_id: str) -> Optional[SceneTransaction]:
        """获取事务"""
        return self._transactions.get(tx_id)

    async def execute_atomic(self, actions: List[tuple]) -> bool:
        """原子执行多个动作

        actions: [(action, rollback), ...]
        """
        tx = self.begin_transaction()

        for action, rollback in actions:
            tx.add_action(action, rollback)

        return await tx.execute()

    def cleanup(self, max_age_hours: int = 24) -> int:
        """清理旧事务"""
        cutoff = datetime.now().timestamp() - max_age_hours * 3600

        to_remove = []
        for tx_id, tx in self._transactions.items():
            if tx.state in [TransactionState.COMMITTED, TransactionState.ABORTED]:
                if tx.logs and tx.logs[0].timestamp.timestamp() < cutoff:
                    to_remove.append(tx_id)

        for tx_id in to_remove:
            del self._transactions[tx_id]

        return len(to_remove)


# 全局事务管理器
transaction_manager = TransactionManager()
