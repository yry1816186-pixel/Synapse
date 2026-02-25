# arXiv 调研速查表

**日期:** 2026-02-19 | **完整报告:** [2026-02-19-arXiv-IoT-Edge-Distributed-ML-Survey.md](./2026-02-19-arXiv-IoT-Edge-Distributed-ML-Survey.md)

---

## 🎯 核心发现 (Top 5 推荐)

| # | 论文 | 技术 | Synapse适用性 |
|---|------|------|--------------|
| 1 | IGAA | Agentic AI + 元学习调度 | ⭐⭐⭐⭐⭐ 智能调度引擎 |
| 2 | EdgeLoRA | 多租户LLM边缘服务 | ⭐⭐⭐⭐⭐ 多租户架构 |
| 3 | HQP | 混合量化+剪枝 | ⭐⭐⭐⭐⭐ 推理压缩 |
| 4 | Kafka-ML | 流式ML推理 | ⭐⭐⭐⭐⭐ 消息集成 |
| 5 | LoRA-based CL | 边缘持续学习 | ⭐⭐⭐⭐⭐ 模型热更新 |

---

## 📊 领域热度分布

```
持续学习    ████████████████  6篇高相关
调度优化    ████████████████████  9篇高相关
多租户      ██████████████  7篇高相关
边缘推理    ████████████████████  8篇高相关
消息队列    ████████  5篇相关
```

---

## ⚡ Synapse集成优先级

### P0 - 立即实施 (4-12周)
- [ ] **IGAA调度器** - Agentic AI驱动的智能调度
- [ ] **EdgeLoRA多租户** - LoRA适配器池 + 资源隔离
- [ ] **LoRA持续学习** - 边缘模型热更新机制
- [ ] **Kafka-ML集成** - 流式数据→ML推理管道

### P1 - 短期规划 (4-6周)
- [ ] **HQP压缩** - 敏感度感知的量化+剪枝
- [ ] **多租户隔离** - QoS保障的资源管理
- [ ] **公平性推理** - Multi-Agent公平调度

### P2 - 研究储备
- [ ] 神经形态计算 (硬件加速)
- [ ] 轨道边缘计算 (卫星扩展)
- [ ] 区块链数据溯源

---

## 🔑 关键技术标签

```
#AgenticAI  #LoRA  #MetaLearning  #MultiTenant
#EdgeInference  #Quantization  #Pruning  #Kafka
#ContinualLearning  #MARL  #TimeGNN  #MQTT
```

---

## 📌 快速参考链接

- IGAA: 搜索 "IGAA Agentic AI Edge Scheduling"
- EdgeLoRA: 搜索 "EdgeLoRA Multi-Tenant LLM"
- HQP: 搜索 "HQP Hybrid Quantization Pruning"
- Kafka-ML: arXiv 2020, Martín et al.
- TD-MQTT: 2024 IEEE SETIT Conference
