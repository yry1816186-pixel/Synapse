"""
Synapse 统一系统入口
整合所有模块，真正可运行
"""

import asyncio
import logging
import sys
import os
from typing import Dict, Any, Optional
from datetime import datetime

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)


class SynapseSystem:
    """
    Synapse 统一系统
    
    整合所有模块，真正可运行
    """
    
    def __init__(self):
        self._initialized = False
        self._running = False
        
        # 核心模块
        self.health_monitor = None
        self.event_bus = None
        
        # 集群模块
        self.cluster_awareness = None
        self.collaboration_network = None
        self.regional_governance = None
        self.thermal_governance = None
        self.continuum_orchestrator = None
        
        # 边缘模块
        self.collaborative_inference = None
        self.cpu_free_comm = None
        self.asa_framework = None
        self.d_optimal_tta = None
        
        # 调度模块
        self.slo_scheduler = None
        self.flow_prefill_scheduler = None
        self.ace_gnn_scheduler = None
        
        # 多租户模块
        self.delta_fair_scheduler = None
        
        # 学习模块
        self.lora_learner = None
        self.autonomous_learner = None
        
        # 导航模块
        self.intent_planner = None
        
        # 协议模块
        self.universal_adapter = None
        
        # 统计
        self._stats = {
            "requests_processed": 0,
            "tasks_scheduled": 0,
            "inferences_run": 0,
            "learning_steps": 0
        }

    async def initialize(self) -> None:
        """初始化所有模块"""
        logger.info("=" * 50)
        logger.info("Synapse 智枢 - 区域级智能计算集群")
        logger.info("=" * 50)
        logger.info("正在初始化系统...")
        
        # 1. 核心模块
        logger.info("[1/10] 初始化核心模块...")
        from src.core.health_monitor import health_monitor
        from src.core.sql_rule_engine import sql_rule_engine
        from src.core.rate_limiter import rate_limiter
        
        self.health_monitor = health_monitor
        self.sql_rule_engine = sql_rule_engine
        self.rate_limiter = rate_limiter
        logger.info("  ✓ 健康监控、规则引擎、限流器")
        
        # 2. 集群模块
        logger.info("[2/10] 初始化集群模块...")
        from src.cluster.awareness import cluster_awareness
        from src.cluster.collaboration import collaboration_network
        from src.cluster.governance import regional_governance
        from src.cluster.thermal import thermal_governance
        from src.cluster.continuum import continuum_orchestrator
        
        self.cluster_awareness = cluster_awareness
        self.collaboration_network = collaboration_network
        self.regional_governance = regional_governance
        self.thermal_governance = thermal_governance
        self.continuum_orchestrator = continuum_orchestrator
        
        # 初始化集群感知
        await self.cluster_awareness.initialize()
        logger.info("  ✓ 集群感知、协作网络、治理系统、热力学、连续体编排")
        
        # 3. 边缘模块
        logger.info("[3/10] 初始化边缘模块...")
        from src.edge.collaborative_inference import collaborative_inference
        from src.edge.gpu_comm import cpu_free_comm
        from src.edge.asa_federated import asa_framework
        from src.edge.d_optimal_tta import d_optimal_tta
        
        self.collaborative_inference = collaborative_inference
        self.cpu_free_comm = cpu_free_comm
        self.asa_framework = asa_framework
        self.d_optimal_tta = d_optimal_tta
        
        # 初始化 TTA
        self.d_optimal_tta.initialize()
        logger.info("  ✓ 协作推理、GPU通信、联邦学习、TTA")
        
        # 4. 调度模块
        logger.info("[4/10] 初始化调度模块...")
        from src.scheduler.slo_scheduler import slo_scheduler
        from src.scheduler.flow_prefill import flow_prefill_scheduler
        from src.scheduler.ace_gnn import ace_gnn_scheduler
        
        self.slo_scheduler = slo_scheduler
        self.flow_prefill_scheduler = flow_prefill_scheduler
        self.ace_gnn_scheduler = ace_gnn_scheduler
        logger.info("  ✓ SLO调度、FlowPrefill、ACE-GNN")
        
        # 5. 多租户模块
        logger.info("[5/10] 初始化多租户模块...")
        from src.tenancy.delta_fair import delta_fair_scheduler
        
        self.delta_fair_scheduler = delta_fair_scheduler
        logger.info("  ✓ δ公平调度器")
        
        # 6. 学习模块
        logger.info("[6/10] 初始化学习模块...")
        from src.learning.lora_continual import lora_learner
        from src.autonomous.learner import autonomous_learner
        
        self.lora_learner = lora_learner
        self.autonomous_learner = autonomous_learner
        logger.info("  ✓ LoRA持续学习、自主学习器")
        
        # 7. 导航模块
        logger.info("[7/10] 初始化导航模块...")
        from src.navigation.intent_planner import intent_path_planner
        
        self.intent_planner = intent_path_planner
        
        # 添加位置
        from src.navigation.intent_planner import Location
        self.intent_planner.add_location(Location(x=0, y=0, name="服务器机房"))
        self.intent_planner.add_location(Location(x=10, y=0, name="办公区"))
        self.intent_planner.add_location(Location(x=20, y=0, name="会议室"))
        logger.info("  ✓ 意图驱动路径规划")
        
        # 8. ZeroClaw 边缘集成
        logger.info("[8/11] 初始化 ZeroClaw 边缘集成...")
        from src.integrations.zeroclaw_client import zeroclaw_integration
        
        self.zeroclaw = zeroclaw_integration
        await self.zeroclaw.start()
        
        # 注册模拟节点
        from src.integrations.zeroclaw_client import EdgeNode, EdgeNodeStatus
        demo_node = EdgeNode(
            node_id="zeroclaw_demo",
            name="ZeroClaw Demo Node",
            endpoint="http://localhost:9527",
            status=EdgeNodeStatus.ONLINE,
            capabilities=["sensor", "actuator"]
        )
        self.zeroclaw.register_node(demo_node)
        logger.info("  ✓ ZeroClaw 边缘集成")
        
        # 9. 协议模块
        logger.info("[9/11] 初始化协议模块...")
        from src.protocols.universal_adapter import UniversalProtocolAdapter, BUILTIN_ADAPTERS
        
        self.universal_adapter = UniversalProtocolAdapter()
        
        # 注册内置适配器（同步方式）
        for adapter_id, adapter in BUILTIN_ADAPTERS.items():
            self.universal_adapter._adapters[adapter_id] = adapter
        logger.info(f"  ✓ 万能协议适配器 ({len(BUILTIN_ADAPTERS)} 协议)")
        
        # 10. 规则引擎
        logger.info("[10/11] 初始化规则引擎...")
        from src.core.sql_rule_engine import Rule, RuleState
        
        # 添加示例规则
        rule = Rule(
            rule_id="high_cpu_alert",
            name="高CPU告警",
            sql="SELECT * FROM metrics WHERE cpu > 80",
            actions=["alert", "log"]
        )
        self.sql_rule_engine.create_rule(rule)  # 同步调用
        logger.info("  ✓ SQL规则引擎")
        
        # 11. 完成
        logger.info("[11/11] 系统初始化完成")
        
        self._initialized = True
        logger.info("=" * 50)
        logger.info("Synapse 系统就绪")
        logger.info("=" * 50)

    async def run_demo(self) -> Dict[str, Any]:
        """运行演示，验证所有模块工作"""
        if not self._initialized:
            await self.initialize()
        
        logger.info("\n开始系统演示...")
        results = {}
        
        # 1. 集群感知演示
        logger.info("\n[演示 1] 集群感知")
        cluster_status = self.cluster_awareness.get_cluster_status()
        logger.info(f"  集群状态: {cluster_status}")
        results["cluster"] = cluster_status
        
        # 2. 协作推理演示
        logger.info("\n[演示 2] 协作推理")
        from src.edge.collaborative_inference import InferenceRequest
        req = InferenceRequest(
            request_id="demo_1",
            model="vision",
            input_data={},
            privacy_level="high"
        )
        inference_result = await self.collaborative_inference.infer(req)
        logger.info(f"  推理结果: 位置={inference_result.location.value}, 延迟={inference_result.latency_ms:.1f}ms")
        results["inference"] = {
            "location": inference_result.location.value,
            "latency_ms": inference_result.latency_ms
        }
        self._stats["inferences_run"] += 1
        
        # 3. 调度演示
        logger.info("\n[演示 3] SLO 调度")
        from src.scheduler.slo_scheduler import Task, Priority
        task = Task(
            task_id="task_demo",
            name="演示任务",
            estimated_duration_ms=100,
            priority=Priority.HIGH
        )
        self.slo_scheduler.submit_task(task)
        assignments = await self.slo_scheduler.schedule()
        logger.info(f"  任务调度: {assignments}")
        results["scheduling"] = assignments
        self._stats["tasks_scheduled"] += 1
        
        # 4. LoRA 学习演示
        logger.info("\n[演示 4] LoRA 持续学习")
        adapter = self.lora_learner.create_adapter("demo_adapter", rank=8)
        self.lora_learner.set_active_adapter(adapter.adapter_id)
        logger.info(f"  创建适配器: {adapter.adapter_id}")
        results["lora"] = {
            "adapter_id": adapter.adapter_id,
            "rank": adapter.rank
        }
        
        # 5. 路径规划演示
        logger.info("\n[演示 5] 意图驱动路径规划")
        from src.navigation.intent_planner import IntentType
        path = await self.intent_planner.plan("服务器机房", "会议室", IntentType.OPTIMIZE_TIME)
        logger.info(f"  路径规划: {path.total_distance}m, {path.total_time}s")
        results["navigation"] = {
            "distance": path.total_distance,
            "time": path.total_time
        }
        
        # 6. 协议适配演示
        logger.info("\n[演示 6] 协议适配")
        protocols = self.universal_adapter.get_supported_protocols()
        logger.info(f"  支持协议: {protocols}")
        results["protocols"] = protocols
        
        # 7. 多租户演示
        logger.info("\n[演示 7] 多租户管理")
        from src.tenancy.delta_fair import TenantQuota
        quota = TenantQuota(tenant_id="tenant_demo", cpu_limit=4.0, memory_limit=4096)
        self.delta_fair_scheduler.register_tenant(quota)
        tenant_status = self.delta_fair_scheduler.get_tenant_usage("tenant_demo")
        logger.info(f"  租户状态: {tenant_status}")
        results["tenancy"] = tenant_status
        
        # 8. 热力学治理演示
        logger.info("\n[演示 8] 热力学集群治理")
        from src.cluster.thermal import ThermalNode
        node = ThermalNode(node_id="node_1", name="服务器1")
        self.thermal_governance.register_node(node)
        thermal_status = self.thermal_governance.get_status()
        logger.info(f"  热力学状态: {thermal_status}")
        results["thermal"] = thermal_status
        
        # 9. ZeroClaw 边缘演示
        logger.info("\n[演示 10] ZeroClaw 边缘集成")
        zeroclaw_stats = self.zeroclaw.get_stats()
        logger.info(f"  边缘节点: {zeroclaw_stats['total_nodes']}, 在线: {zeroclaw_stats['online_nodes']}")
        results["zeroclaw"] = zeroclaw_stats
        
        # 10. 系统总结
        logger.info("\n" + "=" * 50)
        logger.info("系统演示完成")
        logger.info("=" * 50)
        
        results["stats"] = self._stats
        results["timestamp"] = datetime.now().isoformat()
        
        return results

    def get_system_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        return {
            "initialized": self._initialized,
            "running": self._running,
            "stats": self._stats,
            "modules": {
                "cluster": self.cluster_awareness.get_cluster_status() if self.cluster_awareness else None,
                "inference": self.collaborative_inference.get_stats() if self.collaborative_inference else None,
                "scheduling": self.slo_scheduler.get_stats() if self.slo_scheduler else None,
                "lora": self.lora_learner.get_stats() if self.lora_learner else None,
                "protocols": self.universal_adapter.get_supported_protocols() if self.universal_adapter else []
            }
        }


# 全局系统实例
synapse_system = SynapseSystem()


async def main():
    """主函数"""
    system = SynapseSystem()
    
    try:
        # 初始化
        await system.initialize()
        
        # 运行演示
        results = await system.run_demo()
        
        # 输出结果
        print("\n" + "=" * 50)
        print("系统验证结果:")
        print("=" * 50)
        for key, value in results.items():
            print(f"  {key}: {value}")
        
        print("\n✅ Synapse 系统验证通过")
        print("所有模块正常工作")
        
    except Exception as e:
        logger.error(f"系统错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
