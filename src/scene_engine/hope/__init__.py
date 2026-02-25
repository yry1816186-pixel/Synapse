"""
Hope 持续学习模块 - 基于 Google Nested Learning
核心能力：持续学习、自我改进、智能记忆
"""

from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import asyncio
import logging
import json
from collections import defaultdict
import math

logger = logging.getLogger(__name__)


@dataclass
class MemoryEntry:
    """记忆条目"""
    key: str
    value: Any
    timestamp: datetime = field(default_factory=datetime.now)
    access_count: int = 0
    importance: float = 0.5
    decay_rate: float = 0.1
    metadata: Dict[str, Any] = field(default_factory=dict)

    def access(self) -> None:
        """访问记忆"""
        self.access_count += 1
        self.importance = min(1.0, self.importance + 0.1)

    def decay(self) -> float:
        """记忆衰减"""
        age = (datetime.now() - self.timestamp).total_seconds() / 3600  # 小时
        self.importance *= math.exp(-self.decay_rate * age)
        return self.importance


@dataclass
class LearningPattern:
    """学习模式"""
    pattern_id: str
    pattern_type: str  # "device_usage", "scene_trigger", "user_behavior"
    conditions: Dict[str, Any]
    action: Dict[str, Any]
    confidence: float = 0.0
    occurrence_count: int = 0
    last_occurrence: datetime = field(default_factory=datetime.now)


class MemorySystem:
    """记忆系统 - Continuum Memory"""

    def __init__(self, max_entries: int = 10000):
        self._memories: Dict[str, MemoryEntry] = {}
        self._max_entries = max_entries
        self._type_index: Dict[str, List[str]] = defaultdict(list)

    async def store(self, key: str, value: Any, memory_type: str = "general",
                   importance: float = 0.5, metadata: Dict[str, Any] = None) -> None:
        """存储记忆"""
        # 检查容量
        if len(self._memories) >= self._max_entries:
            await self._evict_low_importance()

        entry = MemoryEntry(
            key=key,
            value=value,
            importance=importance,
            metadata={"type": memory_type, **(metadata or {})}
        )

        self._memories[key] = entry
        self._type_index[memory_type].append(key)
        logger.debug(f"记忆已存储: {key}")

    async def recall(self, key: str) -> Optional[Any]:
        """回忆记忆"""
        if key not in self._memories:
            return None

        entry = self._memories[key]
        entry.access()
        return entry.value

    async def search(self, query: str, memory_type: str = None,
                    limit: int = 10) -> List[Tuple[str, Any, float]]:
        """搜索记忆"""
        results = []

        for key, entry in self._memories.items():
            if memory_type and entry.metadata.get("type") != memory_type:
                continue

            if query.lower() in key.lower() or query.lower() in str(entry.value).lower():
                results.append((key, entry.value, entry.importance))

        # 按重要性排序
        results.sort(key=lambda x: x[2], reverse=True)
        return results[:limit]

    async def _evict_low_importance(self) -> None:
        """驱逐低重要性记忆"""
        # 衰减所有记忆
        for entry in self._memories.values():
            entry.decay()

        # 找到最不重要的记忆
        sorted_entries = sorted(
            self._memories.items(),
            key=lambda x: x[1].importance
        )

        # 移除 10% 最不重要的
        to_remove = max(1, len(sorted_entries) // 10)
        for key, _ in sorted_entries[:to_remove]:
            del self._memories[key]

        logger.info(f"已驱逐 {to_remove} 条低重要性记忆")


class LearningEngine:
    """学习引擎"""

    def __init__(self):
        self._patterns: Dict[str, LearningPattern] = {}
        self._memory: MemorySystem = MemorySystem()
        self._learning_rate: float = 0.1
        self._min_confidence: float = 0.7

    async def observe(self, event_type: str, context: Dict[str, Any],
                     outcome: Dict[str, Any]) -> None:
        """观察事件"""
        # 存储观察
        await self._memory.store(
            key=f"obs_{datetime.now().isoformat()}",
            value={"event_type": event_type, "context": context, "outcome": outcome},
            memory_type="observation",
            importance=0.3
        )

        # 尝试识别模式
        await self._identify_pattern(event_type, context, outcome)

    async def _identify_pattern(self, event_type: str, context: Dict[str, Any],
                                outcome: Dict[str, Any]) -> Optional[LearningPattern]:
        """识别学习模式"""
        # 简单的模式识别逻辑
        pattern_key = f"{event_type}_{hash(frozenset(context.items()))}"

        if pattern_key in self._patterns:
            pattern = self._patterns[pattern_key]
            pattern.occurrence_count += 1
            pattern.last_occurrence = datetime.now()
            pattern.confidence = min(1.0, pattern.confidence + self._learning_rate)
        else:
            pattern = LearningPattern(
                pattern_id=pattern_key,
                pattern_type=event_type,
                conditions=context,
                action=outcome,
                confidence=0.1,
                occurrence_count=1
            )
            self._patterns[pattern_key] = pattern

        return pattern

    async def predict(self, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """预测最佳行动"""
        best_pattern = None
        best_confidence = 0

        for pattern in self._patterns.values():
            if self._matches_conditions(context, pattern.conditions):
                if pattern.confidence > best_confidence:
                    best_confidence = pattern.confidence
                    best_pattern = pattern

        if best_pattern and best_confidence >= self._min_confidence:
            return best_pattern.action

        return None

    def _matches_conditions(self, context: Dict[str, Any],
                           conditions: Dict[str, Any]) -> bool:
        """检查条件是否匹配"""
        for key, value in conditions.items():
            if key not in context or context[key] != value:
                return False
        return True

    async def get_recommendations(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """获取推荐"""
        recommendations = []

        for pattern in self._patterns.values():
            if self._matches_conditions(context, pattern.conditions):
                if pattern.confidence >= self._min_confidence:
                    recommendations.append({
                        "pattern_id": pattern.pattern_id,
                        "action": pattern.action,
                        "confidence": pattern.confidence,
                        "occurrence_count": pattern.occurrence_count
                    })

        recommendations.sort(key=lambda x: x["confidence"], reverse=True)
        return recommendations[:5]


class HopeModule:
    """Hope 持续学习模块 - 主入口"""

    def __init__(self):
        self._memory = MemorySystem()
        self._learning = LearningEngine()
        self._initialized = False

    async def initialize(self) -> None:
        """初始化"""
        self._initialized = True
        logger.info("Hope 持续学习模块已初始化")

    async def learn(self, event_type: str, context: Dict[str, Any],
                   outcome: Dict[str, Any]) -> None:
        """学习"""
        await self._learning.observe(event_type, context, outcome)

    async def remember(self, key: str, value: Any, **kwargs) -> None:
        """记忆"""
        await self._memory.store(key, value, **kwargs)

    async def recall(self, key: str) -> Optional[Any]:
        """回忆"""
        return await self._memory.recall(key)

    async def predict(self, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """预测"""
        return await self._learning.predict(context)

    async def recommend(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """推荐"""
        return await self._learning.get_recommendations(context)

    async def shutdown(self) -> None:
        """关闭"""
        self._initialized = False
        logger.info("Hope 持续学习模块已关闭")


# 全局 Hope 模块实例
hope = HopeModule()
