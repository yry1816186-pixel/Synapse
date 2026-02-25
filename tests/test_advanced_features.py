"""
Synapse 测试套件

全面的单元测试和集成测试
"""

import unittest
import asyncio
import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.advanced_features import (
    MoSEEngine, SlimmableExpert, ExpertWidth,
    SLICEScheduler, SLOSpec, LLMTRequest,
    VEDACache, KVCacheEntry,
    LIMEEngine, EdgeDevice,
    WISPEngine, SpeculativeCandidate,
    EdgeLoRAEngine, LoRAAdapter,
    TimeGNNEngine, TaskNode,
    AdaptiveResourceManager
)


class TestMoSEEngine(unittest.TestCase):
    """MoSE 引擎测试"""

    def setUp(self):
        self.engine = MoSEEngine(num_experts=8)

    def test_initialization(self):
        """测试初始化"""
        self.assertEqual(len(self.engine.experts), 8)
        stats = self.engine.get_stats()
        self.assertEqual(stats["num_experts"], 8)

    def test_routing(self):
        """测试路由"""
        input_data = {"key": "value"}
        expert_id = self.engine.route(input_data, compute_budget=0.5)
        self.assertIsNotNone(expert_id)
        self.assertIn(expert_id, self.engine.experts)

    def test_width_adjustment(self):
        """测试宽度调整"""
        input_data = {"key": "value"}

        # 低预算
        expert_id = self.engine.route(input_data, compute_budget=0.2)
        expert = self.engine.experts[expert_id]
        self.assertLessEqual(expert.current_width, expert.base_width * 0.2 + 64)

        # 高预算
        expert_id = self.engine.route(input_data, compute_budget=1.0)
        expert = self.engine.experts[expert_id]
        self.assertLessEqual(expert.current_width, expert.base_width)


class TestSLICEScheduler(unittest.TestCase):
    """SLICE 调度器测试"""

    def setUp(self):
        self.scheduler = SLICEScheduler()

    def test_submit_request(self):
        """测试提交请求"""
        request = LLMTRequest(
            request_id="req_1",
            prompt="Hello",
            slo=SLOSpec(max_latency_ms=100.0),
            arrival_time=0.0
        )
        self.scheduler.submit(request)
        self.assertEqual(len(self.scheduler.request_queue), 1)

    def test_schedule(self):
        """测试调度"""
        request = LLMTRequest(
            request_id="req_1",
            prompt="Hello",
            slo=SLOSpec(max_latency_ms=100000.0),  # 更大的 SLO
            arrival_time=time.time()
        )
        self.scheduler.submit(request)
        scheduled = self.scheduler.schedule()
        self.assertIsNotNone(scheduled)
        self.assertEqual(scheduled.request_id, "req_1")

    def test_priority_scheduling(self):
        """测试优先级调度"""
        now = time.time()
        low_priority = LLMTRequest(
            request_id="low",
            prompt="Low",
            slo=SLOSpec(max_latency_ms=100000.0),  # 更大的 SLO
            arrival_time=now,
            priority=0
        )
        high_priority = LLMTRequest(
            request_id="high",
            prompt="High",
            slo=SLOSpec(max_latency_ms=100000.0),  # 更大的 SLO
            arrival_time=now,
            priority=10
        )

        self.scheduler.submit(low_priority)
        self.scheduler.submit(high_priority)

        scheduled = self.scheduler.schedule()
        # 高优先级应该先被调度
        self.assertEqual(scheduled.request_id, "high")


class TestVEDACache(unittest.TestCase):
    """VEDA 缓存测试"""

    def setUp(self):
        self.cache = VEDACache(max_size_mb=1.0)

    def test_put_get(self):
        """测试存取"""
        self.cache.put("key1", "value1", 100)
        result = self.cache.get("key1")
        self.assertEqual(result, "value1")

    def test_cache_miss(self):
        """测试缓存未命中"""
        result = self.cache.get("nonexistent")
        self.assertIsNone(result)

    def test_eviction(self):
        """测试淘汰"""
        # 填满缓存
        for i in range(100):
            self.cache.put(f"key_{i}", f"value_{i}", 10000)

        # 确保缓存大小在限制内
        stats = self.cache.get_stats()
        self.assertLessEqual(stats["size_mb"], 1.0)

    def test_hit_rate(self):
        """测试命中率"""
        for i in range(10):
            self.cache.put(f"key_{i}", f"value_{i}", 1000)

        # 5 次命中
        for i in range(5):
            self.cache.get(f"key_{i}")

        # 5 次未命中
        for i in range(5):
            self.cache.get(f"miss_{i}")

        stats = self.cache.get_stats()
        self.assertEqual(stats["hits"], 5)
        self.assertEqual(stats["misses"], 5)
        self.assertAlmostEqual(stats["hit_rate"], 0.5, places=1)


class TestLIMEEngine(unittest.TestCase):
    """LIME 引擎测试"""

    def setUp(self):
        self.engine = LIMEEngine()

    def test_register_device(self):
        """测试设备注册"""
        device = EdgeDevice(
            device_id="device_1",
            name="Test Device",
            memory_mb=512,
            compute_capability=0.5
        )
        self.engine.register_device(device)
        self.assertEqual(len(self.engine.devices), 1)

    def test_layer_allocation(self):
        """测试层分配"""
        # 注册设备
        for i in range(3):
            self.engine.register_device(EdgeDevice(
                device_id=f"device_{i}",
                name=f"Device {i}",
                memory_mb=512,
                compute_capability=0.5
            ))

        # 设置模型
        self.engine.set_model(10, [100, 150, 200, 100, 150, 200, 100, 150, 200, 100])

        # 优化分配
        allocations = self.engine.optimize_allocation()
        self.assertGreater(len(allocations), 0)


class TestWISPEngine(unittest.TestCase):
    """WISP 引擎测试"""

    def setUp(self):
        self.engine = WISPEngine(num_draft_tokens=4)

    def test_add_draft_model(self):
        """测试添加草稿模型"""
        self.engine.add_draft_model("draft_1")
        self.assertEqual(len(self.engine.draft_models), 1)

    def test_speculate(self):
        """测试推测"""
        self.engine.add_draft_model("draft_1")
        candidates = self.engine.speculate("Hello")
        self.assertEqual(len(candidates), 4)

    def test_verify(self):
        """测试验证"""
        self.engine.add_draft_model("draft_1")
        candidates = self.engine.speculate("Hello")
        target_tokens = ["token_0", "token_1", "token_2", "token_3"]
        accepted = self.engine.verify(candidates, target_tokens)
        self.assertGreaterEqual(accepted, 0)


class TestEdgeLoRAEngine(unittest.TestCase):
    """EdgeLoRA 引擎测试"""

    def setUp(self):
        self.engine = EdgeLoRAEngine(max_memory_mb=100.0)

    def test_create_adapter(self):
        """测试创建适配器"""
        adapter_id = self.engine.create_adapter("tenant_1", rank=8)
        self.assertIsNotNone(adapter_id)
        self.assertEqual(len(self.engine.adapters), 1)

    def test_memory_limit(self):
        """测试内存限制"""
        # 创建多个适配器直到内存不足
        created = 0
        for i in range(1000):
            adapter_id = self.engine.create_adapter(f"tenant_{i}", rank=8)
            if adapter_id:
                created += 1
            else:
                break

        self.assertLess(created, 1000)
        stats = self.engine.get_stats()
        self.assertLessEqual(stats["memory_used_mb"], 100.0)

    def test_delete_adapter(self):
        """测试删除适配器"""
        adapter_id = self.engine.create_adapter("tenant_1")
        self.assertTrue(self.engine.delete_adapter(adapter_id))
        self.assertEqual(len(self.engine.adapters), 0)


class TestTimeGNNEngine(unittest.TestCase):
    """TimeGNN 引擎测试"""

    def setUp(self):
        self.engine = TimeGNNEngine()

    def test_add_task(self):
        """测试添加任务"""
        task = TaskNode(
            task_id="task_1",
            dependencies=[],
            compute_cost=1.0,
            data_size=100.0
        )
        self.engine.add_task(task)
        self.assertEqual(len(self.engine.tasks), 1)

    def test_partition(self):
        """测试分区"""
        # 添加设备
        self.engine.add_device("device_1", 1.0)
        self.engine.add_device("device_2", 0.8)

        # 添加任务
        self.engine.add_task(TaskNode("t1", [], 1.0, 100.0))
        self.engine.add_task(TaskNode("t2", ["t1"], 2.0, 200.0))
        self.engine.add_task(TaskNode("t3", ["t1"], 1.5, 150.0))

        assignment = self.engine.partition()
        self.assertEqual(len(assignment), 3)

    def test_topological_sort(self):
        """测试拓扑排序"""
        self.engine.add_task(TaskNode("t1", [], 1.0, 100.0))
        self.engine.add_task(TaskNode("t2", ["t1"], 1.0, 100.0))
        self.engine.add_task(TaskNode("t3", ["t2"], 1.0, 100.0))

        sorted_tasks = self.engine._topological_sort()
        self.assertEqual(sorted_tasks, ["t1", "t2", "t3"])


class TestAdaptiveResourceManager(unittest.TestCase):
    """自适应资源管理器测试"""

    def setUp(self):
        self.manager = AdaptiveResourceManager()

    def test_initialization(self):
        """测试初始化"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.manager.initialize())
        self.assertTrue(self.manager._initialized)

    def test_full_stats(self):
        """测试完整统计"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.manager.initialize())

        stats = self.manager.get_full_stats()
        self.assertIn("mose", stats)
        self.assertIn("slice", stats)
        self.assertIn("veda", stats)
        self.assertIn("lime", stats)
        self.assertIn("wisp", stats)
        self.assertIn("edgelora", stats)
        self.assertIn("timegnn", stats)


class TestIntegration(unittest.TestCase):
    """集成测试"""

    def test_full_workflow(self):
        """测试完整工作流"""
        # 初始化
        manager = AdaptiveResourceManager()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(manager.initialize())

        # MoSE 路由
        expert_id = manager.mose.route({"input": "test"}, compute_budget=0.5)
        self.assertIsNotNone(expert_id)

        # SLICE 调度
        request = LLMTRequest(
            request_id="req_1",
            prompt="test",
            slo=SLOSpec(max_latency_ms=100000.0),  # 更大的 SLO
            arrival_time=time.time()
        )
        manager.slice_scheduler.submit(request)
        scheduled = manager.slice_scheduler.schedule()
        self.assertIsNotNone(scheduled)

        # VEDA 缓存
        manager.veda_cache.put("key", "value", 100)
        result = manager.veda_cache.get("key")
        self.assertEqual(result, "value")

        # EdgeLoRA
        adapter_id = manager.edgelora.create_adapter("tenant_1")
        self.assertIsNotNone(adapter_id)

        # 验证统计
        stats = manager.get_full_stats()
        self.assertEqual(stats["mose"]["total_usage"], 1)
        self.assertEqual(stats["veda"]["hits"], 1)
        self.assertEqual(stats["edgelora"]["total_adapters"], 1)


def run_tests():
    """运行所有测试"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TestMoSEEngine))
    suite.addTests(loader.loadTestsFromTestCase(TestSLICEScheduler))
    suite.addTests(loader.loadTestsFromTestCase(TestVEDACache))
    suite.addTests(loader.loadTestsFromTestCase(TestLIMEEngine))
    suite.addTests(loader.loadTestsFromTestCase(TestWISPEngine))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeLoRAEngine))
    suite.addTests(loader.loadTestsFromTestCase(TestTimeGNNEngine))
    suite.addTests(loader.loadTestsFromTestCase(TestAdaptiveResourceManager))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result


if __name__ == "__main__":
    result = run_tests()
    sys.exit(0 if result.wasSuccessful() else 1)
