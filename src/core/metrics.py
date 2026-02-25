"""
性能监控模块
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
import asyncio
import logging
import time
from collections import defaultdict

logger = logging.getLogger(__name__)


@dataclass
class MetricPoint:
    """指标点"""
    name: str
    value: float
    timestamp: datetime = field(default_factory=datetime.now)
    tags: Dict[str, str] = field(default_factory=dict)


class MetricsCollector:
    """指标收集器"""

    def __init__(self):
        self._metrics: Dict[str, List[MetricPoint]] = defaultdict(list)
        self._max_points: int = 10000
        self._counters: Dict[str, float] = defaultdict(float)
        self._gauges: Dict[str, float] = {}
        self._histograms: Dict[str, List[float]] = defaultdict(list)

    def counter(self, name: str, value: float = 1, tags: Dict[str, str] = None) -> None:
        """计数器"""
        key = self._make_key(name, tags)
        self._counters[key] += value
        self._record(name, self._counters[key], tags)

    def gauge(self, name: str, value: float, tags: Dict[str, str] = None) -> None:
        """仪表"""
        key = self._make_key(name, tags)
        self._gauges[key] = value
        self._record(name, value, tags)

    def histogram(self, name: str, value: float, tags: Dict[str, str] = None) -> None:
        """直方图"""
        key = self._make_key(name, tags)
        self._histograms[key].append(value)
        if len(self._histograms[key]) > 1000:
            self._histograms[key] = self._histograms[key][-1000:]
        self._record(name, value, tags)

    def timing(self, name: str, duration_ms: float, tags: Dict[str, str] = None) -> None:
        """计时"""
        self.histogram(name, duration_ms, tags)

    def _record(self, name: str, value: float, tags: Dict[str, str] = None) -> None:
        """记录指标"""
        point = MetricPoint(name=name, value=value, tags=tags or {})
        self._metrics[name].append(point)

        # 限制数量
        if len(self._metrics[name]) > self._max_points:
            self._metrics[name] = self._metrics[name][-self._max_points:]

    def _make_key(self, name: str, tags: Dict[str, str] = None) -> str:
        """生成键"""
        if not tags:
            return name
        tag_str = ",".join(f"{k}={v}" for k, v in sorted(tags.items()))
        return f"{name}:{tag_str}"

    def get_counter(self, name: str, tags: Dict[str, str] = None) -> float:
        """获取计数器值"""
        key = self._make_key(name, tags)
        return self._counters.get(key, 0)

    def get_gauge(self, name: str, tags: Dict[str, str] = None) -> float:
        """获取仪表值"""
        key = self._make_key(name, tags)
        return self._gauges.get(key, 0)

    def get_histogram_stats(self, name: str, tags: Dict[str, str] = None) -> Dict[str, float]:
        """获取直方图统计"""
        key = self._make_key(name, tags)
        values = self._histograms.get(key, [])

        if not values:
            return {"count": 0, "mean": 0, "min": 0, "max": 0, "p50": 0, "p95": 0, "p99": 0}

        sorted_values = sorted(values)
        count = len(sorted_values)

        return {
            "count": count,
            "mean": sum(values) / count,
            "min": sorted_values[0],
            "max": sorted_values[-1],
            "p50": sorted_values[int(count * 0.5)],
            "p95": sorted_values[int(count * 0.95)],
            "p99": sorted_values[int(count * 0.99)]
        }

    def get_metrics(self, name: str = None) -> Dict[str, Any]:
        """获取所有指标"""
        if name:
            return {name: [m.__dict__ for m in self._metrics.get(name, [])]}

        return {name: [m.__dict__ for m in points] for name, points in self._metrics.items()}


class PerformanceMonitor:
    """性能监控器"""

    def __init__(self):
        self.metrics = MetricsCollector()
        self._start_times: Dict[str, float] = {}

    def start_timer(self, name: str) -> None:
        """开始计时"""
        self._start_times[name] = time.time()

    def stop_timer(self, name: str, tags: Dict[str, str] = None) -> float:
        """停止计时"""
        start = self._start_times.pop(name, None)
        if start is None:
            return 0

        duration_ms = (time.time() - start) * 1000
        self.metrics.timing(name, duration_ms, tags)
        return duration_ms

    def record_request(self, endpoint: str, status_code: int, duration_ms: float) -> None:
        """记录请求"""
        self.metrics.counter("requests_total", 1, {"endpoint": endpoint, "status": str(status_code)})
        self.metrics.timing("request_duration", duration_ms, {"endpoint": endpoint})

    def record_device_operation(self, device_id: str, operation: str, success: bool, duration_ms: float) -> None:
        """记录设备操作"""
        self.metrics.counter("device_operations_total", 1, {
            "device": device_id,
            "operation": operation,
            "success": str(success)
        })
        self.metrics.timing("device_operation_duration", duration_ms, {"operation": operation})

    def record_scene_execution(self, scene_id: str, success: bool, duration_ms: float) -> None:
        """记录场景执行"""
        self.metrics.counter("scene_executions_total", 1, {
            "scene": scene_id,
            "success": str(success)
        })
        self.metrics.timing("scene_execution_duration", duration_ms)

    def set_system_metrics(self, cpu: float, memory: float, connections: int) -> None:
        """设置系统指标"""
        self.metrics.gauge("system_cpu_percent", cpu)
        self.metrics.gauge("system_memory_percent", memory)
        self.metrics.gauge("system_connections", connections)

    def get_summary(self) -> Dict[str, Any]:
        """获取摘要"""
        return {
            "requests": self.metrics.get_histogram_stats("request_duration"),
            "device_operations": self.metrics.get_histogram_stats("device_operation_duration"),
            "scene_executions": self.metrics.get_histogram_stats("scene_execution_duration"),
            "counters": {
                "requests_total": self.metrics.get_counter("requests_total"),
                "device_operations_total": self.metrics.get_counter("device_operations_total"),
                "scene_executions_total": self.metrics.get_counter("scene_executions_total")
            }
        }


# 全局监控器
performance_monitor = PerformanceMonitor()
