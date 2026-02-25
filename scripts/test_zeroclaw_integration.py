"""
Synapse + ZeroClaw 部署脚本
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.integrations.zeroclaw_client import ZeroClawIntegration, EdgeNode, EdgeNodeStatus


async def main():
    print("=" * 50)
    print("Synapse + ZeroClaw 边缘集成测试")
    print("=" * 50)

    # 创建集成实例
    integration = ZeroClawIntegration()
    await integration.start()

    # 注册模拟边缘节点
    print("\n[1] 注册边缘节点...")

    nodes = [
        EdgeNode(
            node_id="zeroclaw_rpi_01",
            name="树莓派 Zero 2W #1",
            endpoint="http://192.168.1.101:9527",
            status=EdgeNodeStatus.ONLINE,
            capabilities=["sensor", "actuator", "camera"],
            memory_mb=4.5,
            cpu_percent=12.5
        ),
        EdgeNode(
            node_id="zeroclaw_esp32_01",
            name="ESP32 #1",
            endpoint="http://192.168.1.102:9527",
            status=EdgeNodeStatus.ONLINE,
            capabilities=["sensor"],
            memory_mb=0.3,
            cpu_percent=25.0
        ),
    ]

    for node in nodes:
        integration.register_node(node)
        print(f"  ✓ {node.name} - {node.endpoint}")

    # 列出节点
    print("\n[2] 边缘节点列表:")
    for node in integration.list_nodes():
        print(f"  - {node.name}: {node.status.value} (内存: {node.memory_mb}MB)")

    # 发送任务
    print("\n[3] 发送任务...")

    # 读取传感器
    task_id = await integration.read_sensor("zeroclaw_rpi_01", "dht22_temperature")
    print(f"  ✓ 传感器读取任务: {task_id}")

    # 执行规则
    task_id = await integration.execute_rule(
        "zeroclaw_rpi_01",
        "rule_temp_control",
        {"temperature": 28.5}
    )
    print(f"  ✓ 规则执行任务: {task_id}")

    # 调用云端 API
    task_id = await integration.call_cloud_api(
        "zeroclaw_rpi_01",
        "openai_chat",
        {"prompt": "分析当前温度是否正常"}
    )
    print(f"  ✓ API 调用任务: {task_id}")

    # 健康检查
    print("\n[4] 健康检查:")
    for node in integration.list_nodes():
        health = await integration.health_check(node.node_id)
        print(f"  - {node.name}: {health['status']}")

    # 统计
    print("\n[5] 系统统计:")
    stats = integration.get_stats()
    print(f"  - 节点总数: {stats['total_nodes']}")
    print(f"  - 在线节点: {stats['online_nodes']}")
    print(f"  - 任务总数: {stats['total_tasks']}")

    # 停止
    await integration.stop()

    print("\n" + "=" * 50)
    print("测试完成")
    print("=" * 50)

    print("""
下一步:
1. 在真实树莓派上安装 ZeroClaw
2. 配置网络连接
3. 部署传感器和执行器
4. 测试实时数据流
    """)


if __name__ == "__main__":
    asyncio.run(main())
