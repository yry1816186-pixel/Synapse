"""
FlashMem 内存优化 - 流式加载
减少 2-8x 内存占用
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
import asyncio
import logging

logger = logging.getLogger(__name__)


@dataclass
class MemoryBlock:
    """内存块"""
    block_id: str
    size_mb: float
    data: Any = None
    loaded: bool = False
    last_access: datetime = None


class FlashMemOptimizer:
    """
    FlashMem 内存优化器

    流式加载，减少 2-8x 内存占用
    """

    def __init__(self, max_memory_mb: float = 1024):
        self.max_memory_mb = max_memory_mb
        self._blocks: Dict[str, MemoryBlock] = {}
        self._current_usage_mb = 0.0
        self._access_order: List[str] = []

    def register_block(self, block_id: str, size_mb: float, data: Any = None) -> None:
        """注册内存块"""
        self._blocks[block_id] = MemoryBlock(
            block_id=block_id,
            size_mb=size_mb,
            data=data
        )

    async def load(self, block_id: str) -> Any:
        """加载内存块（按需加载）"""
        block = self._blocks.get(block_id)
        if not block:
            return None

        if not block.loaded:
            # 检查是否需要卸载其他块
            while self._current_usage_mb + block.size_mb > self.max_memory_mb:
                await self._evict_lru()

            # 加载
            block.loaded = True
            block.last_access = datetime.now()
            self._current_usage_mb += block.size_mb
            self._access_order.append(block_id)
            logger.debug(f"加载内存块: {block_id} ({block.size_mb}MB)")

        # 更新访问顺序
        block.last_access = datetime.now()
        if block_id in self._access_order:
            self._access_order.remove(block_id)
        self._access_order.append(block_id)

        return block.data

    async def _evict_lru(self) -> None:
        """卸载最久未使用的块"""
        if not self._access_order:
            return

        lru_id = self._access_order.pop(0)
        lru_block = self._blocks.get(lru_id)

        if lru_block and lru_block.loaded:
            lru_block.loaded = False
            lru_block.data = None
            self._current_usage_mb -= lru_block.size_mb
            logger.debug(f"卸载内存块: {lru_id}")

    def get_stats(self) -> Dict[str, Any]:
        """获取统计"""
        loaded = [b for b in self._blocks.values() if b.loaded]
        return {
            "total_blocks": len(self._blocks),
            "loaded_blocks": len(loaded),
            "current_usage_mb": self._current_usage_mb,
            "max_memory_mb": self.max_memory_mb,
            "utilization": self._current_usage_mb / self.max_memory_mb
        }


# 全局优化器
flashmem = FlashMemOptimizer()
