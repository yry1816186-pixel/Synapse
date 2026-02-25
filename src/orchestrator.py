"""
系统启动脚本 - 完整版
"""

import asyncio
import logging
import signal
import sys
import os
from typing import Any

# 添加路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class SynapseOrchestrator:
    """Synapse 编排器 - 管理所有组件"""

    def __init__(self):
        self._components = {}
        self._running = False
        self._shutdown_event = asyncio.Event()

    async def register(self, name: str, component: Any, start_func: str = "start",
                      stop_func: str = "stop") -> None:
        """注册组件"""
        self._components[name] = {
            "instance": component,
            "start": start_func,
            "stop": stop_func
        }
        logger.info(f"注册组件: {name}")

    async def start_all(self) -> None:
        """启动所有组件"""
        logger.info("=== 启动 Synapse ===")

        for name, comp in self._components.items():
            try:
                instance = comp["instance"]
                start_func = getattr(instance, comp["start"], None)

                if start_func and asyncio.iscoroutinefunction(start_func):
                    await start_func()
                elif start_func:
                    start_func()

                logger.info(f"✓ {name} 已启动")
            except Exception as e:
                logger.error(f"✗ {name} 启动失败: {e}")

        self._running = True
        logger.info("=== Synapse 已启动 ===")

    async def stop_all(self) -> None:
        """停止所有组件"""
        logger.info("=== 停止 Synapse ===")

        self._running = False

        for name, comp in reversed(list(self._components.items())):
            try:
                instance = comp["instance"]
                stop_func = getattr(instance, comp["stop"], None)

                if stop_func and asyncio.iscoroutinefunction(stop_func):
                    await stop_func()
                elif stop_func:
                    stop_func()

                logger.info(f"✓ {name} 已停止")
            except Exception as e:
                logger.error(f"✗ {name} 停止失败: {e}")

        logger.info("=== Synapse 已停止 ===")

    def request_shutdown(self) -> None:
        """请求关闭"""
        self._shutdown_event.set()


async def main():
    """主函数"""
    orchestrator = SynapseOrchestrator()

    # 注册核心组件
    from src.core.event_bus import event_bus
    from src.scene_engine import scene_engine
    from src.scene_engine.hope import hope

    await orchestrator.register("event_bus", event_bus)
    await orchestrator.register("scene_engine", scene_engine)
    await orchestrator.register("hope", hope)

    # 信号处理
    loop = asyncio.get_event_loop()

    def signal_handler():
        logger.info("收到关闭信号")
        orchestrator.request_shutdown()

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, signal_handler)

    try:
        await orchestrator.start_all()
        await orchestrator._shutdown_event.wait()
    finally:
        await orchestrator.stop_all()


if __name__ == "__main__":
    print("""
   _____                  __  __           
  / ___/___  ____  ____  / /_/ /___  _____  
  \\__ \\/ _ \\\\/ __ \\/ __ \\/ __/ / __ \\/ ___/
 ___/ /  __/ / / / / / / /_/ / /_/ (__  ) 
/____/\\___/_/ /_/_/ /_/\\__/_/\\____/____/  
                                          
  Synapse - Enterprise IoT Platform v3.0.0
""")
    asyncio.run(main())
