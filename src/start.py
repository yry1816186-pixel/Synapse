"""
Synapse 主启动入口
"""

import asyncio
import logging
import signal
import sys
from typing import Optional

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class SynapseApp:
    """Synapse 应用"""

    def __init__(self):
        self._initialized = False
        self._running = False
        self._shutdown_event = asyncio.Event()

    async def initialize(self) -> None:
        """初始化"""
        logger.info("=== Synapse 初始化 ===")

        # 导入模块
        from src.core.plugin_system import plugin_manager
        from src.core.event_bus import event_bus, EventType
        from src.core.config import config_manager
        from src.core.scheduler import task_scheduler
        from src.core.metrics import performance_monitor
        from src.core.health import health_checker
        from src.device_abstraction import device_registry
        from src.scene_engine import scene_engine
        from src.scene_engine.hope import hope
        from src.tenancy import tenant_manager

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

        # 运行健康检查
        health_results = await health_checker.run_all()
        for name, result in health_results.items():
            logger.info(f"健康检查 {name}: {result.status.value}")

        self._initialized = True
        logger.info("=== Synapse 初始化完成 ===")

    async def start(self) -> None:
        """启动"""
        if not self._initialized:
            await self.initialize()

        self._running = True

        # 发送系统启动事件
        from src.core.event_bus import event_bus, EventType
        await event_bus.emit(
            EventType.SYSTEM_START,
            source="synapse",
            data={"version": "3.0.0"}
        )

        logger.info("Synapse 已启动 - 等待关闭信号")

        # 等待关闭信号
        await self._shutdown_event.wait()

    async def stop(self) -> None:
        """停止"""
        logger.info("=== Synapse 停止中 ===")

        self._running = False

        # 发送系统停止事件
        from src.core.event_bus import event_bus, EventType
        await event_bus.emit(
            EventType.SYSTEM_STOP,
            source="synapse"
        )

        # 关闭模块
        from src.scene_engine.hope import hope
        from src.scene_engine import scene_engine
        from src.core.scheduler import task_scheduler
        from src.core.event_bus import event_bus

        await hope.shutdown()
        await scene_engine.stop()
        await task_scheduler.stop()
        await event_bus.stop()

        logger.info("=== Synapse 已停止 ===")

    def request_shutdown(self) -> None:
        """请求关闭"""
        self._shutdown_event.set()


async def main():
    """主函数"""
    app = SynapseApp()

    # 设置信号处理
    loop = asyncio.get_event_loop()

    def signal_handler():
        logger.info("收到关闭信号")
        app.request_shutdown()

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, signal_handler)

    try:
        await app.start()
    except KeyboardInterrupt:
        pass
    finally:
        await app.stop()


if __name__ == "__main__":
    asyncio.run(main())
