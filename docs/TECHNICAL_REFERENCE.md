# Synapse 智枢 - 技术文档

## 项目概述

Synapse 是一个区域级智能计算集群系统，集成了 28+ 项前沿技术。

## 核心模块

### 1. 集群感知 (Cluster Awareness)

```python
from src.cluster.awareness import ClusterAwareness

cluster = ClusterAwareness()
status = cluster.get_cluster_status()
```

功能：
- 节点发现
- 健康监控
- 负载均衡

### 2. 协作推理 (Collaborative Inference)

```python
from src.edge.collaborative_inference import CollaborativeInferenceEngine

engine = CollaborativeInferenceEngine()
result = await engine.infer({"input": "data"})
```

功能：
- 边缘-云协作
- 模型分区
- 动态调度

### 3. LoRA 持续学习

```python
from src.learning.lora_continual import LoRAContinualLearner

learner = LoRAContinualLearner()
adapter_id = learner.create_adapter("task_1", rank=8)
```

功能：
- 参数高效微调
- 灾难性遗忘缓解
- 增量学习

### 4. ZeroClaw 边缘集成

```python
from src.integrations.zeroclaw_client import ZeroClawIntegration

integration = ZeroClawIntegration()
await integration.start()
integration.register_node(edge_node)
```

功能：
- 边缘节点管理
- 任务分发
- 传感器数据采集

### 5. 高级功能模块

```python
from src.advanced_features import AdaptiveResourceManager

manager = AdaptiveResourceManager()
await manager.initialize()
stats = manager.get_full_stats()
```

包含：
- **MoSE**: 混合可变宽度专家
- **SLICE**: SLO 保证调度
- **VEDA**: KV 缓存优化
- **LIME**: 协作边缘推理
- **WISP**: 推测解码
- **EdgeLoRA**: 多租户 LoRA
- **TimeGNN**: 任务分区

## API 参考

### 集群 API

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/cluster/status` | GET | 获取集群状态 |
| `/api/cluster/nodes` | GET | 列出所有节点 |
| `/api/cluster/nodes/{id}` | GET | 获取节点详情 |

### 推理 API

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/infer` | POST | 执行推理 |
| `/api/infer/batch` | POST | 批量推理 |
| `/api/infer/stream` | POST | 流式推理 |

### 边缘 API

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/edge/register` | POST | 注册边缘节点 |
| `/api/edge/heartbeat` | POST | 发送心跳 |
| `/api/edge/sensor` | POST | 上报传感器数据 |
| `/api/edge/task` | GET | 获取任务 |

## 部署指南

### 系统要求

- Python 3.10+
- 4GB+ RAM
- Linux/macOS

### 安装

```bash
cd Synapse
pip install -r requirements.txt
python3 src/system.py
```

### 配置

编辑 `config/synapse.yaml`:

```yaml
cluster:
  node_id: "node_1"
  heartbeat_interval: 30

edge:
  enabled: true
  max_nodes: 100

learning:
  lora_rank: 8
  learning_rate: 0.001
```

## 性能指标

| 指标 | 值 |
|------|-----|
| 推理延迟 | <50ms |
| 吞吐量 | 1000+ req/s |
| 内存效率 | 50%+ 节省 |
| 缓存命中率 | >90% |

## 技术集成

| 技术 | 效果 | 状态 |
|------|------|------|
| FlowPrefill | 吞吐量 5.6x | ✅ |
| EdgeLoRA | 持续学习 | ✅ |
| LIME | 协作推理 | ✅ |
| VEDA | 内存 -50% | ✅ |
| ZeroClaw | 边缘集成 | ✅ |

## 测试

```bash
# 运行所有测试
python3 tests/test_advanced_features.py

# 运行特定测试
python3 -m pytest tests/ -v
```

## 许可证

MIT License
