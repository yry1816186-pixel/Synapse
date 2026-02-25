"""
Synapse 主入口
"""

import asyncio
import logging
from typing import Optional

from .core.plugin_system import plugin_manager
from .core.event_bus import event_bus, EventType
from .core.config import config_manager
from .core.scheduler import task_scheduler
from .device_abstraction import device_registry
from .scene_engine import scene_engine
from .scene_engine.hope import hope
from .tenancy import tenant_manager

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class Synapse:
    """Synapse 应用"""

    def __init__(self):
        self._initialized = False
        self._running = False

    async def initialize(self, config_path: str = "./config") -> None:
        """初始化"""
        logger.info("正在初始化 Synapse...")

        # 加载配置
        config_manager.load()
        logger.info("配置加载完成")

        # 启动事件总线
        await event_bus.start()
        logger.info("事件总线已启动")

        # 启动调度器
        await task_scheduler.start()
        logger.info("调度器已启动")

        # 启动场景引擎
        await scene_engine.start()
        logger.info("场景引擎已启动")

        # 初始化 Hope 模块
        await hope.initialize()
        logger.info("Hope 持续学习模块已初始化")

        self._initialized = True
        logger.info("Synapse 初始化完成")

    async def start(self) -> None:
        """启动"""
        if not self._initialized:
            await self.initialize()

        self._running = True

        # 发送系统启动事件
        await event_bus.emit(
            EventType.SYSTEM_START,
            source="synapse",
            data={"version": "3.0.0"}
        )

        logger.info("Synapse 已启动")

        # 保持运行
        while self._running:
            await asyncio.sleep(1)

    async def stop(self) -> None:
        """停止"""
        logger.info("正在停止 Synapse...")

        self._running = False

        # 发送系统停止事件
        await event_bus.emit(
            EventType.SYSTEM_STOP,
            source="synapse"
        )

        # 关闭各模块
        await hope.shutdown()
        await scene_engine.stop()
        await task_scheduler.stop()
        await event_bus.stop()

        logger.info("Synapse 已停止")

    async def health_check(self) -> dict:
        """健康检查"""
        return {
            "initialized": self._initialized,
            "running": self._running,
            "modules": {
                "event_bus": event_bus._running,
                "scene_engine": scene_engine._state.value,
                "devices": len(device_registry.list_all()),
                "scenes": len(scene_engine.list_scenes()),
                "plugins": len(plugin_manager.list_plugins())
            }
        }


# 全局应用实例
app = Synapse()


async def main():
    """主函数"""
    try:
        await app.start()
    except KeyboardInterrupt:
        await app.stop()


if __name__ == "__main__":
    asyncio.run(main())
