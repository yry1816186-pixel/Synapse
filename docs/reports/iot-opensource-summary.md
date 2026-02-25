# 物联网开源项目分析摘要

**生成时间**: 2026-02-21

## 项目概览

| 项目 | 领域 | 技术栈 | 特点 |
|------|------|--------|------|
| Home Assistant | 智能家居 | Python | 本地优先、模块化集成、社区活跃 |
| OpenHAB | 智能家居 | Java/OSGi | 企业级、200+集成、Java 21 |
| Node-RED | 流程编排 | Node.js | 低代码、可视化、事件驱动 |
| EdgeX Foundry | 边缘计算 | Go | 微服务、零信任、Linux基金会 |
| KubeEdge | 云边协同 | Go/K8s | CNCF毕业、K8s原生、边缘自治 |
| EMQX | 消息中间件 | Erlang | 亿级连接、MQTT 5.0、规则引擎 |

## 核心设计模式

1. **模块化集成** - Home Assistant, OpenHAB
2. **事件驱动** - Home Assistant, Node-RED, EMQX  
3. **设备孪生** - KubeEdge, EdgeX Foundry
4. **云边协同** - KubeEdge, EdgeX Foundry
5. **规则引擎** - EMQX, Node-RED
6. **微服务网关** - EdgeX Foundry

## 架构选择指南

| 场景 | 推荐参考 |
|------|----------|
| 智能家居 | Home Assistant (Python + 事件驱动) |
| 工业边缘 | EdgeX Foundry (Go 微服务) |
| 云边协同 | KubeEdge (K8s 原生) |
| 消息平台 | EMQX (Erlang 高并发) |
| 流程编排 | Node-RED (低代码可视化) |

## 关键技术点

### Home Assistant
- 三层架构: OS → Supervisor → Core
- 集成系统: `DOMAIN` + `async_setup`
- 状态机: 统一的状态管理

### KubeEdge
- Cloud: CloudHub + EdgeController + DeviceController
- Edge: EdgeHub + MetaManager + Edged + EventBus
- 边缘自治: SQLite 本地存储

### EMQX
- 协议: MQTT 5.0 + MQTT over QUIC
- 规则引擎: SQL-based 数据处理
- 数据集成: 50+ 后端系统

### EdgeX Foundry
- 微服务: 独立部署的 Go 服务
- 消息总线: 可选 NATS
- 安全: OpenZiti 零信任

## 详细报告

完整分析请参阅: [iot-opensource-analysis-2026-02-21.md](./iot-opensource-analysis-2026-02-21.md)
