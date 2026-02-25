"""
Synapse - 性能基准测试
"""

import asyncio
import time
from typing import Dict, Any, List
from dataclasses import dataclass


@dataclass
class BenchmarkResult:
    """基准测试结果"""
    name: str
    iterations: int
    total_time_ms: float
    avg_time_ms: float
    min_time_ms: float
    max_time_ms: float
    ops_per_second: float


class Benchmark:
    """基准测试工具"""

    def __init__(self, name: str):
        self.name = name
        self._results: List[float] = []

    async def run(self, func, iterations: int = 1000) -> BenchmarkResult:
        """运行基准测试"""
        self._results = []

        for _ in range(iterations):
            start = time.perf_counter()
            
            if asyncio.iscoroutinefunction(func):
                await func()
            else:
                func()
            
            end = time.perf_counter()
            self._results.append((end - start) * 1000)

        total = sum(self._results)
        avg = total / iterations
        ops = 1000 / avg if avg > 0 else 0

        return BenchmarkResult(
            name=self.name,
            iterations=iterations,
            total_time_ms=total,
            avg_time_ms=avg,
            min_time_ms=min(self._results),
            max_time_ms=max(self._results),
            ops_per_second=ops
        )


async def benchmark_event_bus():
    """事件总线基准测试"""
    from synapse.src.core.event_bus import EventBus, Event, EventType

    bus = EventBus()
    await bus.start()

    received = []

    async def handler(event):
        received.append(event)

    bus.subscribe(EventType.DEVICE_DATA, handler)

    async def emit():
        await bus.emit(EventType.DEVICE_DATA, "benchmark")

    bench = Benchmark("event_bus")
    result = await bench.run(emit, 1000)

    await bus.stop()
    return result


async def benchmark_scene_engine():
    """场景引擎基准测试"""
    from synapse.src.scene_engine import SceneEngine, Scene, Action, ActionType

    engine = SceneEngine()
    await engine.start()

    scene = Scene(
        scene_id="bench_scene",
        name="Benchmark Scene",
        actions=[
            Action(action_type=ActionType.DELAY, config={"seconds": 0})
        ]
    )
    await engine.register_scene(scene)

    async def trigger():
        await engine.trigger_scene("bench_scene")

    bench = Benchmark("scene_engine")
    result = await bench.run(trigger, 100)

    await engine.stop()
    return result


async def benchmark_device_registry():
    """设备注册基准测试"""
    from synapse.src.device_abstraction import DeviceRegistry, VirtualDevice, DeviceType

    registry = DeviceRegistry()
    counter = [0]

    async def register():
        counter[0] += 1
        device = VirtualDevice(
            device_id=f"bench_{counter[0]}",
            name="Benchmark Device",
            device_type=DeviceType.SENSOR
        )
        await registry.register(device)

    bench = Benchmark("device_registry")
    result = await bench.run(register, 1000)

    return result


async def benchmark_hope_memory():
    """Hope 记忆基准测试"""
    from synapse.src.scene_engine.hope import HopeModule

    hope = HopeModule()
    await hope.initialize()

    counter = [0]

    async def remember():
        counter[0] += 1
        await hope.remember(f"key_{counter[0]}", f"value_{counter[0]}")

    bench = Benchmark("hope_memory")
    result = await bench.run(remember, 1000)

    return result


async def run_all_benchmarks():
    """运行所有基准测试"""
    print("=" * 50)
    print("Synapse 性能基准测试")
    print("=" * 50)

    results = []

    try:
        result = await benchmark_event_bus()
        results.append(result)
    except Exception as e:
        print(f"event_bus 测试失败: {e}")

    try:
        result = await benchmark_scene_engine()
        results.append(result)
    except Exception as e:
        print(f"scene_engine 测试失败: {e}")

    try:
        result = await benchmark_device_registry()
        results.append(result)
    except Exception as e:
        print(f"device_registry 测试失败: {e}")

    try:
        result = await benchmark_hope_memory()
        results.append(result)
    except Exception as e:
        print(f"hope_memory 测试失败: {e}")

    print("\n结果:")
    print("-" * 50)
    print(f"{'模块':<20} {'平均耗时':<12} {'最小耗时':<12} {'最大耗时':<12} {'OPS':<12}")
    print("-" * 50)

    for r in results:
        print(f"{r.name:<20} {r.avg_time_ms:<12.3f} {r.min_time_ms:<12.3f} {r.max_time_ms:<12.3f} {r.ops_per_second:<12.0f}")

    print("-" * 50)

    return results


if __name__ == "__main__":
    asyncio.run(run_all_benchmarks())
