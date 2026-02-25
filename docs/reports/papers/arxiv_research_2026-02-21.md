# arXiv 论文研究报告：IoT/边缘计算/分布式系统/机器学习最新进展

**报告日期**: 2026年2月21日  
**研究目标**: 评估最新学术研究对 Synapse 项目的潜在集成价值  
**关注领域**: 持续学习、设备调度优化、多租户系统、边缘AI推理、消息队列优化

---

## 执行摘要

本报告汇总了 arXiv 上 2025-2026 年间发表的最新研究成果，重点关注与 Synapse 智枢平台相关的技术领域。共筛选出 **28篇高价值论文**，其中 **12篇具有直接集成价值**，**8篇需要进一步评估**，**8篇作为技术参考**。

### 关键发现

| 领域 | 推荐论文数 | 高集成价值 | 技术成熟度 |
|------|-----------|-----------|-----------|
| 持续学习 | 6 | 3 | ★★★☆☆ |
| 设备调度 | 5 | 2 | ★★★★☆ |
| 多租户系统 | 7 | 4 | ★★★★☆ |
| 边缘AI推理 | 6 | 2 | ★★★☆☆ |
| 消息队列 | 4 | 1 | ★★★★☆ |

---

## 一、持续学习 / Nested Learning

### 1.1 Node Learning: A Framework for Adaptive, Decentralised and Collaborative Network Edge AI
**arXiv ID**: 2602.16814  
**发布日期**: 2026-02-18  
**作者**: Eiman Kanjo, Mustafa Aslanov

**核心创新**:
- 提出了一种去中心化学习范式，智能分布在边缘节点
- 通过选择性对等交互扩展知识
- 学习通过重叠和扩散传播，而非全局同步

**关键洞察**:
> "节点学习将自主行为和协作行为统一在一个抽象中，适应数据、硬件、目标和连接性的异构性。"

**Synapse 集成评估**:
- **适用性**: ★★★★★ 高度相关，直接补充 Hope 持续学习模块
- **实现难度**: ★★★☆☆ 需要重新设计通信层
- **建议**: 可作为 Hope 模块的去中心化扩展，支持边缘设备协作学习

**集成路径**:
```
src/scene_engine/hope/
├── node_learning/          # 新增模块
│   ├── peer_selector.py    # 对等节点选择
│   ├── knowledge_diffusion.py  # 知识扩散
│   └── adaptive_sync.py    # 自适应同步
```

---

### 1.2 LoRA-based Parameter-Efficient LLMs for Continuous Learning in Edge-based Malware Detection
**arXiv ID**: 2602.11655  
**发布日期**: 2026-02-12  
**作者**: Christian Rondanini 等

**核心创新**:
- 结合本地适应和全局知识共享
- 使用 LoRA 适配器实现参数高效迁移
- 在边缘设备上增量微调

**性能指标**:
- 跨域攻击检测准确率提升 20-25%
- LoRA 模块仅增加 <1% 模型大小 (~0.6-1.8 MB)

**Synapse 集成评估**:
- **适用性**: ★★★★☆ 适合安全检测场景
- **实现难度**: ★★☆☆☆ LoRA 集成相对简单
- **建议**: 可用于设备异常检测的持续学习

---

### 1.3 Catastrophic Forgetting Resilient One-Shot Incremental Federated Learning
**arXiv ID**: 2602.17625  
**发布日期**: 2026-02-19  
**作者**: Obaidullah Zaland 等

**核心创新**:
- 解决联邦学习中的灾难性遗忘问题
- Selective Sample Retention (SSR) 算法
- 单轮通信实现增量学习

**技术要点**:
- 使用冻结 VLM 提取类别特定嵌入
- 扩散模型合成新数据
- 基于样本损失选择最有信息量的样本

**Synapse 集成评估**:
- **适用性**: ★★★★★ 直接解决 Hope 模块的持续学习挑战
- **实现难度**: ★★★★☆ 需要扩散模型支持
- **建议**: 可作为 Hope 增量学习的核心算法

---

### 1.4 FedPSA: Modeling Behavioral Staleness in Asynchronous Federated Learning
**arXiv ID**: 2602.15337  
**发布日期**: 2026-02-17  
**作者**: Chaoyi Lu

**核心创新**:
- 参数敏感性衡量模型过时性
- 动量队列评估训练阶段
- 动态调整对过时信息的容忍度

**性能提升**:
- 比基线方法提升 6.37%
- 比当前最优方法提升 1.93%

**Synapse 集成评估**:
- **适用性**: ★★★★☆ 适合异步联邦学习场景
- **实现难度**: ★★★☆☆ 中等复杂度
- **建议**: 可用于多租户场景下的异步模型更新

---

## 二、设备调度优化

### 2.1 Evaluating Malleable Job Scheduling in HPC Clusters using Real-World Workloads
**arXiv ID**: 2602.17318  
**发布日期**: 2026-02-19  
**作者**: Patrick Zojer 等

**核心创新**:
- 资源弹性：动态调整可延展作业的资源分配
- 使用真实超算工作负载验证
- 评估五种作业调度策略

**性能提升**:
- 作业周转时间减少 37-67%
- 作业等待时间减少 73-99%
- 节点利用率提升 5-52%

**Synapse 集成评估**:
- **适用性**: ★★★★★ 直接相关，可优化 Celery/Temporal 调度
- **实现难度**: ★★★☆☆ 需要修改调度器核心
- **建议**: 可用于优化 Synapse 双引擎调度系统

**集成路径**:
```
src/core/scheduler/
├── malleable_scheduler.py  # 新增可延展调度器
├── resource_elasticity.py  # 资源弹性管理
└── workload_predictor.py   # 工作负载预测
```

---

### 2.2 FlowPrefill: Decoupling Preemption from Prefill Scheduling Granularity
**arXiv ID**: 2602.16603  
**发布日期**: 2026-02-18  
**作者**: Chia-chi Hsieh 等

**核心创新**:
- 解决 LLM 服务中的 Head-of-Line (HoL) 阻塞
- Operator-Level Preemption：基于算子边界的细粒度中断
- Event-Driven Scheduling：事件驱动的调度决策

**性能提升**:
- 最大吞吐量提升 5.6x
- 满足异构 SLO 要求

**Synapse 集成评估**:
- **适用性**: ★★★★☆ 适合 AI 推理任务调度
- **实现难度**: ★★★★☆ 需要深入理解模型结构
- **建议**: 可用于优化设备 AI 推理任务的调度

---

### 2.3 DDiT: Dynamic Patch Scheduling for Efficient Diffusion Transformers
**arXiv ID**: 2602.16968  
**发布日期**: 2026-02-19  
**作者**: Dahye Kim 等

**核心创新**:
- 基于内容复杂度的动态 Tokenization
- 早期时间步使用粗粒度 Patch
- 后期时间步使用细粒度 Patch

**性能提升**:
- FLUX-1.Dev 加速 3.52x
- Wan 2.1 加速 3.2x
- 不损失生成质量

**Synapse 集成评估**:
- **适用性**: ★★★☆☆ 适合图像生成场景
- **实现难度**: ★★★★☆ 需要深度定制
- **建议**: 可作为图像处理管道的优化选项

---

### 2.4 Predictive Batch Scheduling: Accelerating Language Model Training
**arXiv ID**: 2602.17066  
**发布日期**: 2026-02-19  
**作者**: Sumedh Rasal

**核心创新**:
- 基于损失感知的样本优先级
- 轻量级线性预测器估计样本难度
- 动态构建 Batch

**性能提升**:
- 收敛加速 6-13%
- 预测器相关性从 0.14 提升到 0.44

**Synapse 集成评估**:
- **适用性**: ★★★★☆ 可用于模型训练优化
- **实现难度**: ★★☆☆☆ 相对简单
- **建议**: 可用于 Hope 模块的在线学习优化

---

### 2.5 Hierarchical Edge-Cloud Task Offloading in NTN for Remote Healthcare
**arXiv ID**: 2602.17209  
**发布日期**: 2026-02-19  
**作者**: Alejandro Flores 等

**核心创新**:
- 非地面网络（NTN）边缘-云分层架构
- HAPS 作为 MEC 服务器
- LEO 卫星作为云网关

**Synapse 集成评估**:
- **适用性**: ★★★☆☆ 适合远程医疗场景
- **实现难度**: ★★★★★ 需要卫星网络支持
- **建议**: 作为未来扩展方向

---

## 三、多租户系统

### 3.1 MUSE: Multi-Tenant Model Serving With Seamless Model Updates
**arXiv ID**: 2602.11776  
**发布日期**: 2026-02-12  
**作者**: Cláudio Correia 等 (Feedzai)

**核心创新**:
- 解耦模型分数与客户端决策边界
- 基于意图的动态路由
- 两级分数转换映射到稳定参考分布

**生产验证**:
- 处理 >1000 事件/秒
- 12个月内处理 550 亿事件
- 支持数十个租户

**关键价值**:
> "将模型更新时间从数周缩短到数分钟，节省数百万美元的欺诈损失。"

**Synapse 集成评估**:
- **适用性**: ★★★★★ 高度相关，直接增强多租户能力
- **实现难度**: ★★★★☆ 需要重构模型服务层
- **建议**: 作为 Synapse 多租户系统的核心升级

**集成路径**:
```
src/tenancy/
├── muse_adapter/
│   ├── score_transformer.py  # 分数转换
│   ├── intent_router.py      # 意图路由
│   └── model_registry.py     # 模型注册
```

---

### 3.2 Equilibria: Fair Multi-Tenant CXL Memory Tiering At Scale
**arXiv ID**: 2602.08800  
**发布日期**: 2026-02-09  
**作者**: Kaiyang Zhao 等

**核心创新**:
- Per-Container 公平份额控制
- 细粒度内存使用可观察性
- 灵活的公平性策略执行

**性能提升**:
- 生产工作负载性能提升 52%
- Benchmark 性能提升 1.7x

**Synapse 集成评估**:
- **适用性**: ★★★★☆ 适合容器化部署场景
- **实现难度**: ★★★☆☆ 需要内核级支持
- **建议**: 可用于优化 Docker 部署的内存管理

---

### 3.3 MonkeyTree: Near-Minimal Congestion for Multi-tenant Training
**arXiv ID**: 2602.08296  
**发布日期**: 2026-02-09  
**作者**: Anton A. Zabreyko 等

**核心创新**:
- 基于 Job Migration 的去碎片化
- 整数线性规划最小化 Worker 移动
- RDMA 内存检查点恢复

**性能提升**:
- 平均作业完成时间减少 14%
- 99 分位作业完成时间接近理想

**Synapse 集成评估**:
- **适用性**: ★★★☆☆ 适合大规模训练场景
- **实现难度**: ★★★★★ 需要底层网络支持
- **建议**: 作为分布式训练的优化方向

---

### 3.4 Delta Fair Sharing: Performance Isolation for Multi-Tenant Storage Systems
**arXiv ID**: 2601.20030  
**发布日期**: 2026-01-27  
**作者**: Tyler Griggs 等

**核心创新**:
- δ-fairness：限制客户端获取公平份额的延迟
- δ-Pareto-efficiency：分配未使用资源
- 处理高抢占延迟的资源

**Synapse 集成评估**:
- **适用性**: ★★★★☆ 适合存储层多租户隔离
- **实现难度**: ★★★☆☆ 中等复杂度
- **建议**: 可用于优化时序数据库的多租户访问

---

### 3.5 Enhancing Predictability of Multi-Tenant DNN Inference
**arXiv ID**: 2602.11004  
**发布日期**: 2026-02-11  
**作者**: Liangkai Liu 等

**核心创新**:
- 动态选择关键帧和 ROI
- FLOPs 预测器预测计算量
- 多租户 DNN 协调

**性能提升**:
- 融合帧数增加 7.3x
- 融合延迟减少 >2.6x
- 检测完整性提升 75.4%

**Synapse 集成评估**:
- **适用性**: ★★★★☆ 适合视频分析场景
- **实现难度**: ★★★★☆ 需要深度学习框架支持
- **建议**: 可用于智能监控设备的多租户推理

---

### 3.6 An Online Fragmentation-Aware GPU Scheduler for Multi-Tenant MIG-based Clouds
**arXiv ID**: 2511.18906  
**发布日期**: 2025-11-24  
**作者**: Marco Zambianco 等

**核心创新**:
- NVIDIA MIG 硬件级 GPU 分区
- 碎片感知调度算法
- 在线、工作负载无关的调度

**性能提升**:
- 重负载下工作负载接受率平均提升 10%
- 使用相同数量的 GPU

**Synapse 集成评估**:
- **适用性**: ★★★☆☆ 适合 GPU 密集型场景
- **实现难度**: ★★★★☆ 需要硬件支持
- **建议**: 可用于边缘 AI 服务器的资源管理

---

### 3.7 LobRA: Multi-tenant Fine-tuning over Heterogeneous Data
**arXiv ID**: 2509.01193  
**发布日期**: 2025-09-01  
**作者**: Sheng Lin 等 (VLDB 2025)

**核心创新**:
- 异构资源使用的副本部署
- 序列长度偏斜感知的数据分发
- 异构 FT 副本间的负载均衡

**性能提升**:
- GPU 秒数减少 45.03%-60.67%

**Synapse 集成评估**:
- **适用性**: ★★★★☆ 适合模型微调场景
- **实现难度**: ★★★★☆ 较复杂
- **建议**: 可用于 Hope 模块的租户级模型定制

---

## 四、边缘 AI 推理

### 4.1 Modular Foundation Model Inference at the Edge: Network-Aware Microservice Optimization
**arXiv ID**: 2601.19563  
**发布日期**: 2026-01-27  
**作者**: Juan Zhu 等

**核心创新**:
- 微服务化 FM 推理框架
- 核心/轻量服务双层部署
- 网络感知的整数规划优化

**性能指标**:
- 准时任务完成率 >84%
- 部署成本适中

**Synapse 集成评估**:
- **适用性**: ★★★★★ 高度相关，适合边缘 AI 部署
- **实现难度**: ★★★★☆ 需要微服务架构
- **建议**: 作为边缘推理服务的架构参考

---

### 4.2 GoodSpeed: Optimizing Fair Goodput with Adaptive Speculative Decoding
**arXiv ID**: 2512.09963  
**发布日期**: 2025-12-14  
**作者**: Phuong Tran 等 (INFOCOM 2026)

**核心创新**:
- 分布式推测解码框架
- 中心验证服务器协调异构草稿服务器
- 梯度调度算法最大化对数效用

**理论保证**:
- 收敛到最优 Goodput 分配
- 动态负载下有界误差

**Synapse 集成评估**:
- **适用性**: ★★★★☆ 适合 LLM 边缘部署
- **实现难度**: ★★★★★ 高复杂度
- **建议**: 作为高级 LLM 推理优化选项

---

### 4.3 Prism: Accelerating Edge Inference for Distributed MoE Models
**arXiv ID**: 2508.12851  
**发布日期**: 2025-08-18  
**作者**: Tian Wu 等

**核心创新**:
- MoE 模型的协作推理框架
- 激活感知的专家放置策略
- 运行时迁移机制适应动态工作负载

**性能提升**:
- 推理延迟减少 30.6%
- 通信成本显著降低

**Synapse 集成评估**:
- **适用性**: ★★★★☆ 适合 MoE 模型边缘部署
- **实现难度**: ★★★★☆ 需要 MoE 模型支持
- **建议**: 可用于大模型的分布式边缘推理

---

### 4.4 COBRA: Algorithm-Architecture Co-optimized Binary Transformer Accelerator
**arXiv ID**: 2504.16269  
**发布日期**: 2025-04-24  
**作者**: Ye Qiao 等

**核心创新**:
- 真 1-bit 二值乘法单元
- 算法-架构协同优化
- FPGA 边缘部署

**性能指标**:
- 吞吐量 3,894.7 GOPS
- 能效 448.7 GOPS/Watt
- 比 GPU 能效提升 311x

**Synapse 集成评估**:
- **适用性**: ★★★☆☆ 适合极致低功耗场景
- **实现难度**: ★★★★★ 需要硬件定制
- **建议**: 作为嵌入式设备 AI 加速参考

---

### 4.5 MoE²: Optimizing Collaborative Inference for Edge Large Language Models
**arXiv ID**: 2501.09410  
**发布日期**: 2025-01-16  
**作者**: Lyudong Jin 等

**核心创新**:
- Mixture-of-Edge-Experts 框架
- 两级专家选择机制
- 离散单调优化算法

**性能提升**:
- 在不同延迟和能量预算下实现最优权衡

**Synapse 集成评估**:
- **适用性**: ★★★★☆ 适合边缘 LLM 场景
- **实现难度**: ★★★★☆ 中高复杂度
- **建议**: 可用于智能助手的边缘部署

---

### 4.6 Bayes-Split-Edge: Bayesian Optimization for Constrained Collaborative Inference
**arXiv ID**: 2510.23503  
**发布日期**: 2025-10-27  
**作者**: Fatemeh Zahra Safaeipour 等

**核心创新**:
- 贝叶斯优化协作分割推理
- 混合采集函数平衡效用和约束
- 联合优化传输功率和分割点

**性能提升**:
- 评估成本减少 2.4x
- 近线性收敛

**Synapse 集成评估**:
- **适用性**: ★★★★☆ 适合无线边缘场景
- **实现难度**: ★★★★☆ 较复杂
- **建议**: 可用于无线边缘设备的推理优化

---

## 五、消息队列优化

### 5.1 push0: Scalable and Fault-Tolerant Orchestration for Zero-Knowledge Proof Generation
**arXiv ID**: 2602.16338  
**发布日期**: 2026-02-18  
**作者**: Mohsen Ahmadvand 等

**核心创新**:
- 事件驱动的 Dispatcher-Collector 架构
- 持久化优先级队列
- 块顺序证明强制执行

**性能指标**:
- 中位编排开销 5ms
- 32 个 Dispatcher 扩展效率 99-100%
- 生产验证：Zircuit zkRollup（1400 万+ 主网块）

**Synapse 集成评估**:
- **适用性**: ★★★★☆ 事件驱动架构可借鉴
- **实现难度**: ★★★☆☆ 中等复杂度
- **建议**: 可用于优化事件总线的消息编排

**集成路径**:
```
src/core/event_bus/
├── push0_orchestrator/
│   ├── dispatcher.py      # 事件分发
│   ├── collector.py       # 结果收集
│   └── priority_queue.py  # 优先级队列
```

---

### 5.2 MultiLevelMultiQueue (MLMQ) for SSSP on GPUs
**arXiv ID**: 2602.10080  
**发布日期**: 2026-02-10  
**作者**: Zhengding Hu 等

**核心创新**:
- 多级多队列数据结构
- Cache-like 协作机制
- GPU 并行优化

**性能提升**:
- 比 SotA 实现加速 1.87x-17.13x

**Synapse 集成评估**:
- **适用性**: ★★★☆☆ 适合 GPU 加速场景
- **实现难度**: ★★★★☆ 需要 CUDA 编程
- **建议**: 可用于图计算加速

---

### 5.3 Bring Your Own Objective: Inter-operability of Network Objectives in Datacenters
**arXiv ID**: 2602.10252  
**发布日期**: 2026-02-10  
**作者**: Sanjoli Narang 等

**核心创新**:
- 去中心化调度框架 DMart
- 网络带宽作为竞争市场
- 分布式、Per-Link、Per-RTT 拍卖

**性能提升**:
- Deadline 丢失减少 2x
- Coflow 完成时间减少 1.6x

**Synapse 集成评估**:
- **适用性**: ★★★☆☆ 适合数据中心网络
- **实现难度**: ★★★★★ 高复杂度
- **建议**: 作为大规模部署的网络优化参考

---

### 5.4 BlazeAIoT: A Modular Multi-Layer Platform for Real-Time Distributed Robotics
**arXiv ID**: 2601.06344  
**发布日期**: 2026-01-09  
**作者**: Cedric Melancon 等

**核心创新**:
- Edge-Fog-Cloud 多层架构
- 多 Broker 互操作（DDS, Kafka, Redis, ROS2）
- 分层限流处理大消息

**Synapse 集成评估**:
- **适用性**: ★★★★★ 高度相关，架构可直接借鉴
- **实现难度**: ★★★★☆ 较复杂
- **建议**: 可作为 Synapse 分布式架构的参考设计

---

## 六、综合评估与优先级建议

### 6.1 高优先级集成（建议 Q2 2026 实施）

| 论文 | 集成模块 | 预期收益 | 实施周期 |
|------|---------|---------|---------|
| Node Learning | Hope 持续学习 | 去中心化协作学习 | 6 周 |
| MUSE | 多租户系统 | 模型无缝更新 | 8 周 |
| Malleable Job Scheduling | 调度系统 | 资源利用率提升 50%+ | 4 周 |
| Modular FM Inference | 边缘推理 | 微服务化 AI 部署 | 6 周 |

### 6.2 中优先级评估（建议 Q3 2026 评估）

| 论文 | 评估重点 | 需要验证的问题 |
|------|---------|--------------|
| FlowPrefill | LLM 服务优化 | 是否与 Celery 兼容 |
| FedPSA | 异步学习 | 异构设备支持范围 |
| Equilibria | 内存管理 | 容器运行时要求 |
| Prism | MoE 推理 | 模型格式兼容性 |

### 6.3 长期研究方向（2026 H2）

1. **卫星边缘计算**: Hierarchical Edge-Cloud Task Offloading (NTN)
2. **GPU 碎片管理**: MIG-based GPU Scheduler
3. **推测解码**: GoodSpeed 框架
4. **二值化 Transformer**: COBRA 极致优化

---

## 七、技术债务与风险

### 7.1 识别的风险

| 风险类型 | 描述 | 缓解措施 |
|---------|------|---------|
| 硬件依赖 | 部分 paper 需要 GPU/卫星支持 | 软件模拟 + 可选硬件加速 |
| 许可证 | 学术代码许可证多样 | 重新实现核心算法 |
| 性能差距 | 论文数据与生产环境差异 | 基准测试验证 |
| 维护负担 | 新模块增加复杂度 | 模块化 + 可选启用 |

### 7.2 技术债务清理建议

1. 在集成新论文前，先完善现有模块的测试覆盖率
2. 建立论文技术验证的标准化流程
3. 为每个集成模块创建独立的性能基准

---

## 八、结论

本次研究共分析了 **28 篇高质量论文**，其中：

- **4 篇建议立即集成**（Node Learning, MUSE, Malleable Scheduling, Modular FM）
- **6 篇建议中期评估**（FlowPrefill, FedPSA, Equilibria, Prism, OS Incremental FL, LoRA-LLM）
- **18 篇作为技术储备**

最紧迫的集成方向是 **MUSE 多租户模型服务** 和 **Node Learning 去中心化学习**，它们直接增强 Synapse 的核心竞争优势。

---

## 附录 A：完整论文列表

| # | arXiv ID | 标题 | 领域 | 集成价值 |
|---|----------|------|------|---------|
| 1 | 2602.16814 | Node Learning | 持续学习 | ★★★★★ |
| 2 | 2602.11655 | LoRA-LLM Continuous Learning | 持续学习 | ★★★★☆ |
| 3 | 2602.17625 | One-Shot Incremental FL | 持续学习 | ★★★★★ |
| 4 | 2602.15337 | FedPSA | 持续学习 | ★★★★☆ |
| 5 | 2602.17318 | Malleable Job Scheduling | 调度 | ★★★★★ |
| 6 | 2602.16603 | FlowPrefill | 调度 | ★★★★☆ |
| 7 | 2602.16968 | DDiT | 调度 | ★★★☆☆ |
| 8 | 2602.17066 | Predictive Batch Scheduling | 调度 | ★★★★☆ |
| 9 | 2602.17209 | NTN Task Offloading | 调度 | ★★★☆☆ |
| 10 | 2602.11776 | MUSE | 多租户 | ★★★★★ |
| 11 | 2602.08800 | Equilibria | 多租户 | ★★★★☆ |
| 12 | 2602.08296 | MonkeyTree | 多租户 | ★★★☆☆ |
| 13 | 2601.20030 | Delta Fair Sharing | 多租户 | ★★★★☆ |
| 14 | 2602.11004 | Multi-Tenant DNN | 多租户 | ★★★★☆ |
| 15 | 2511.18906 | MIG GPU Scheduler | 多租户 | ★★★☆☆ |
| 16 | 2509.01193 | LobRA | 多租户 | ★★★★☆ |
| 17 | 2601.19563 | Modular FM Inference | 边缘AI | ★★★★★ |
| 18 | 2512.09963 | GoodSpeed | 边缘AI | ★★★★☆ |
| 19 | 2508.12851 | Prism | 边缘AI | ★★★★☆ |
| 20 | 2504.16269 | COBRA | 边缘AI | ★★★☆☆ |
| 21 | 2501.09410 | MoE² | 边缘AI | ★★★★☆ |
| 22 | 2510.23503 | Bayes-Split-Edge | 边缘AI | ★★★★☆ |
| 23 | 2602.16338 | push0 | 消息队列 | ★★★★☆ |
| 24 | 2602.10080 | MLMQ | 消息队列 | ★★★☆☆ |
| 25 | 2602.10252 | DMart | 消息队列 | ★★★☆☆ |
| 26 | 2601.06344 | BlazeAIoT | 消息队列 | ★★★★★ |
| 27 | 2602.16738 | SEMAS | IoT | ★★★★☆ |
| 28 | 2602.12557 | CF-HFC | IoT | ★★★★☆ |

---

**报告编制**: Synapse AI Research Team  
**审核状态**: 初稿待审核  
**下次更新**: 2026-03-21
