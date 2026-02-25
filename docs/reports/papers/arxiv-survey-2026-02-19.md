# arXiv 论文调研报告

**日期**: 2026年2月19日  
**主题**: IoT、边缘计算、分布式系统、机器学习最新进展  
**重点领域**: Nested Learning/持续学习、设备调度优化、多租户系统、边缘AI推理、消息队列优化

---

## 一、Nested Learning / 持续学习

### 1.1 Task-Agnostic Continual Learning for Chest Radiograph Classification (arXiv:2602.15811)
**发布时间**: 2026年2月17日  
**作者**: Muthu Subash Kavitha, Anas Zafar, Amgad Muneer, Jia Wu

**创新点**:
- 提出 **CARL-XRay** 框架，首个针对胸部X光片分类的任务无关持续学习方法
- 采用 **Adapter-based Routing** 策略，维护固定主干网络，增量分配轻量级任务特定适配器
- 引入 **潜在任务选择器**，利用紧凑原型和特征级经验重放保留历史上下文
- 在任务未知推理下实现 **75% 路由准确率**，相比联合训练的 62.5% 显著提升

**Synapse 集成评估**:
- ✅ **高优先级**: 适配器路由机制可应用于 Synapse 的模型版本管理和热更新场景
- ✅ **适用场景**: 边缘设备上的模型增量更新、多租户模型共享
- 💡 **建议**: 采用类似的适配器架构实现 Synapse 的"热插拔"模型能力

### 1.2 stable-worldmodel-v1: Reproducible World Modeling Research (arXiv:2602.08968)
**发布时间**: 2026年2月9日  
**作者**: Lucas Maes, Quentin Le Lidec, Dan Haramati, Yann LeCun 等

**创新点**:
- 提供 **模块化、可测试、有文档** 的世界模型研究生态系统
- 环境支持 **可控的变化因子**（视觉和物理属性），支持鲁棒性和持续学习研究
- 实现零样本鲁棒性测试框架，已在 DINO-WM 上验证

**Synapse 集成评估**:
- ⚠️ **中等优先级**: 世界模型概念可用于 Synapse 的预测性调度
- 💡 **建议**: 借鉴其模块化设计，构建 Synapse 的仿真测试环境

### 1.3 Horizon Imagination: Efficient On-Policy Rollout (arXiv:2602.08032)
**发布时间**: 2026年2月8日  
**作者**: Lior Cohen, Ofir Nabati, Kaixin Wang 等

**创新点**:
- 提出 **Horizon Imagination (HI)** 框架，用于扩散世界模型的高效策略想象
- 实现多未来观测的 **并行去噪**，结合稳定化机制和新型采样调度
- 支持 **子帧预算**，将去噪预算与有效视野解耦
- 在 Atari 100K 和 Craftium 上验证，保持控制性能的同时提升生成质量

**Synapse 集成评估**:
- ⚠️ **低优先级**: 主要针对强化学习场景，与 Synapse 当前需求关联较小
- 💡 **建议**: 可用于 Synapse 的智能决策模块长期规划

---

## 二、设备调度优化

### 2.1 IGAA: Intent-Driven General Agentic AI for Edge Services Scheduling (arXiv:2601.13702)
**发布时间**: 2026年1月20日  
**作者**: Yan Sun, Yinqiu Liu, Shaoyong Guo 等

**创新点**:
- 首个基于 **元学习范式** 的意图驱动通用代理 AI 调度框架
- **Network-Service-Intent 矩阵映射** 方法，支持代理模拟新场景生成训练数据
- **易到难泛化学习方案**：RCETL（资源因果效应感知迁移学习）和 APOTL（动作电位最优性感知迁移学习）
- **生成式意图重放 (GIR)** 机制，防止持续学习中的灾难性遗忘
- 意图满足率差距控制在 **3.81%** 以内

**Synapse 集成评估**:
- ✅ **高优先级**: 意图驱动调度与 Synapse 的目标导向设计高度契合
- ✅ **适用场景**: 动态资源分配、服务质量保障、跨域任务调度
- 💡 **建议**: 
  - 实现 Network-Service-Intent 三维矩阵建模
  - 采用元学习框架支持新场景快速适配
  - 集成 GIR 机制保护已学知识

### 2.2 A Scheduling Framework for Efficient MoE Inference on Edge GPU-NDP Systems (arXiv:2601.03992)
**发布时间**: 2026年1月7日  
**作者**: Qi Wu, Chao Fang, Jiayuan Chen 等

**创新点**:
- 首次探索 MoE 推理中的 **张量并行**，跨多个 NDP 单元同时分区计算大型专家参数
- **负载均衡感知调度** 算法，跨 NDP 单元和 GPU 分配专家计算
- **无数据集预取** 策略，主动加载高频访问专家最小化激活延迟
- 端到端延迟平均提升 **2.41x**，最高 **2.56x**

**Synapse 集成评估**:
- ✅ **高优先级**: MoE 架构在边缘 AI 推理中越来越重要
- ✅ **适用场景**: 大模型边缘部署、专家模型动态加载
- 💡 **建议**:
  - 实现 Synapse 的专家模型缓存和动态加载机制
  - 采用负载均衡感知调度优化多模型并发推理

### 2.3 FUSION: Forecast-Embedded Agent Scheduling (arXiv:2512.14323)
**发布时间**: 2025年12月16日  
**作者**: Houyi Qi, Minghui Liwang, Seyyedali Hosseinalipour 等

**创新点**:
- 首个 **预测驱动的分布式空地一体化网络** 服务供应框架
- **两阶段优化框架**：离线阶段（Liquid NN 预测 + 蚁群路由 + 拍卖激励合约）+ 在线阶段（势博弈调度）
- **人类-机器共存** 场景下的差异化 QoS 需求支持
- 在线阶段采用 **最佳响应动力学** 算法，收敛到纯策略纳什均衡

**Synapse 集成评估**:
- ✅ **高优先级**: 预测驱动的资源调度是 Synapse 核心需求
- ✅ **适用场景**: 多层级计算资源协调、动态负载预测
- 💡 **建议**:
  - 引入时序预测模块（如 Liquid NN）预测负载
  - 实现多目标优化调度算法

### 2.4 SLICE: SLO-Driven Scheduling for LLM Inference on Edge (arXiv:2510.18544)
**发布时间**: 2025年10月21日  
**作者**: Will Chow

**创新点**:
- 首个针对 **边缘计算场景** 的差异化 SLO 需求 LLM 调度方案
- **效用最大化请求调度算法** + **动态迭代生成速率控制** 机制
- 区分 TTFT（首个 Token 时间）和 TPOT（每输出 Token 时间）约束
- 相比 Orca 和 FastServe，SLO 达成率提升 **35x**，任务完成时间提升 **3.4x**

**Synapse 集成评估**:
- ✅ **高优先级**: SLO 驱动的调度对边缘 AI 服务至关重要
- ✅ **适用场景**: LLM 边缘推理、实时响应保障
- 💡 **建议**:
  - 实现 SLO 感知的任务队列管理
  - 支持多租户差异化 SLA

### 2.5 Online GPU Energy Optimization with Switching-Aware Bandits (arXiv:2410.11855)
**发布时间**: 2024年10月3日（2026年2月17日更新）  
**作者**: Xiongxiao Xu, Solomon Abera Bekele, Brice Videau 等

**创新点**:
- 首个 **纯在线 GPU 能量优化** 问题建模，基于 **多臂老虎机 (MAB)** 框架
- **EnergyUCB** 控制器：乐观初始化 + UCB 置信区间 + **切换感知 UCB 索引**
- 使用 **Core-to-Uncore 利用率比** 作为 GPU 吞吐量代理
- 在 Aurora 超级计算机真实工作负载上验证，显著节能同时保持性能预算

**Synapse 集成评估**:
- ✅ **高优先级**: 能量感知调度对边缘设备至关重要
- ✅ **适用场景**: GPU 资源管理、功耗优化
- 💡 **建议**:
  - 集成 UCB 框架进行在线资源决策
  - 实现切换成本感知的调度策略

### 2.6 Stable-MoE: Lyapunov-based Token Routing (arXiv:2512.06784)
**发布时间**: 2025年12月7日（2026年2月17日更新）  
**作者**: Long Shi, Bingyan Ou, Kang Wei 等

**创新点**:
- 基于 **Lyapunov 优化** 的 Token 路由框架，针对异构边缘网络
- 在线决策 Token 路由和计算频率利用，**无需未来系统状态知识**
- 确保 **Token 队列和能量队列** 的长期稳定性
- 系统吞吐量提升 **40%+**，测试准确率提升 **5%+**

**Synapse 集成评估**:
- ✅ **高优先级**: Lyapunov 优化提供理论保证的在线决策方法
- ✅ **适用场景**: 分布式训练、边缘推理路由
- 💡 **建议**:
  - 采用 Lyapunov 优化框架保证队列稳定性
  - 实现在线决策机制

### 2.7 FlashMem: Supporting Modern DNN Workloads on Mobile (arXiv:2602.15379)
**发布时间**: 2026年2月17日  
**作者**: Zhihao Shu, Md Musfiqur Rahman Sanim 等

**创新点**:
- **内存流式框架**，替代权重预加载，按需动态流式加载
- 利用 **2.5D 纹理内存** 最小化数据转换，提升执行效率
- 支持 **大模型和 Multi-DNN 工作负载**，突破资源受限 GPU 限制
- 内存减少 **2.0x-8.4x**，加速 **1.7x-75.0x**

**Synapse 集成评估**:
- ✅ **高优先级**: 移动端大模型部署的关键技术
- ✅ **适用场景**: 边缘设备模型加载、多模型并发
- 💡 **建议**:
  - 实现模型参数的按需加载机制
  - 优化内存层级使用

---

## 三、多租户系统

### 3.1 MUSE: Multi-Tenant Model Serving With Seamless Model Updates (arXiv:2602.11776)
**发布时间**: 2026年2月12日  
**作者**: Cláudio Correia, Alberto E. A. Ferreira, Lucas Martins 等 (Feedzai)

**创新点**:
- 首个解决 **Score-as-a-Service 多租户环境** 中模型更新瓶颈的框架
- **两级分数变换**：将模型输出映射到稳定的参考分布
- **基于意图的动态路由**，实现基础设施复用优化
- **无缝模型更新**：模型上线时间从周级降至分钟级
- 已处理 **550 亿事件**，支持数十个租户，保持高可用和低延迟

**Synapse 集成评估**:
- ✅ **高优先级**: 多租户模型服务是 Synapse 核心需求
- ✅ **适用场景**: 多客户模型托管、零停机更新
- 💡 **建议**:
  - 实现分数变换层解耦模型和决策边界
  - 支持基于意图的路由

### 3.2 MonkeyTree: Near-Minimal Congestion for Multi-tenant Training (arXiv:2602.08296)
**发布时间**: 2026年2月9日  
**作者**: Anton A. Zabreyko, Weiyang Wang, Manya Ghobadi

**创新点**:
- 首个通过 **作业迁移去碎片化** 缓解多租户 GPU 集群网络拥塞
- 证明 **任何配置可去碎片化到最多 2 个跨机架碎片/ToR**
- 迁移实现：**内存检查点-恢复 over RDMA**，开销仅 9.02 秒/worker
- 平均作业完成时间提升 **14%**，在 16:1 过度订阅下 P99 保持 5% 以内

**Synapse 集成评估**:
- ⚠️ **中等优先级**: 主要针对大规模训练集群
- 💡 **建议**: 迁移策略可借鉴到 Synapse 的任务调度优化

### 3.3 Equilibria: Fair Multi-Tenant CXL Memory Tiering (arXiv:2602.08800)
**发布时间**: 2026年2月9日  
**作者**: Kaiyang Zhao, Neha Gholkar, Hasan Maruf 等

**创新点**:
- 首个支持 **公平多租户 CXL 分层内存** 的 OS 框架
- **Per-Container 控制**：内存公平共享分配 + 精细可观测性
- **灵活公平策略执行**：通过受监管的晋升和降级
- **噪声邻居干扰抑制**：抑制抖动
- 生产工作负载性能提升 **52%**，基准测试提升 **1.7x**
- 已合并到 **Linux 内核**

**Synapse 集成评估**:
- ✅ **高优先级**: 多租户资源隔离是 Synapse 关键需求
- ✅ **适用场景**: 内存分层管理、租户隔离
- 💡 **建议**:
  - 实现 per-tenant 内存配额和隔离
  - 集成公平调度算法

### 3.4 Delta Fair Sharing: Performance Isolation for Multi-Tenant Storage (arXiv:2601.20030)
**发布时间**: 2026年1月27日  
**作者**: Tyler Griggs, Soujanya Ponnapalli, Dev Bali 等 (Berkeley)

**创新点**:
- 解决存储系统 **高抢占延迟** 下的性能隔离问题
- **δ-公平性**：将客户端等待公平份额的延迟限制在 δ 时间单位内
- **δ-帕累托效率**：将未使用资源分配给有未满足需求的客户端
- **FairDB** 实现（基于 RocksDB），显著优于现有方案

**Synapse 集成评估**:
- ✅ **高优先级**: 存储层性能隔离对多租户系统至关重要
- ✅ **适用场景**: 分布式存储、租户隔离
- 💡 **建议**:
  - 实现延迟受限的公平调度
  - 支持资源超额分配时的性能保障

### 3.5 LobRA: Multi-tenant Fine-tuning over Heterogeneous Data (arXiv:2509.01193)
**发布时间**: 2025年9月1日 (VLDB 2025)  
**作者**: Sheng Lin, Fangcheng Fu, Haoyang Li 等

**创新点**:
- 首个支持 **异构资源部署** 的多租户 LoRA 联合微调框架
- 解决 **序列长度变异** 和 **偏斜** 两大异构性问题
- **异构 FT 副本部署**：匹配不同资源配置
- **数据分派优化**：根据序列长度偏斜平衡工作负载
- GPU 秒减少 **45.03%-60.67%**

**Synapse 集成评估**:
- ✅ **高优先级**: 多租户模型微调是实际需求
- ✅ **适用场景**: 多客户模型定制、资源高效利用
- 💡 **建议**:
  - 支持异构资源的微调任务调度
  - 实现工作负载感知的数据分派

---

## 四、边缘 AI 推理

### 4.1 Compiler-Assisted Speculative Sampling for LLM Inference (arXiv:2602.08060)
**发布时间**: 2026年2月8日  
**作者**: Alejandro Ruiz y Mesa, Guilherme Korol 等

**创新点**:
- 首个 **编译器辅助推测采样** 框架，针对异构边缘设备
- **分析成本模型** 探索异构硬件配置，指导 LLM 子图粗粒度分区
- 在 Hexacore Cortex-A CPU + Mali GPU 上验证，翻译任务加速 **1.68x**
- 成本模型准确预测推测采样和异构执行的联合效益

**Synapse 集成评估**:
- ✅ **高优先级**: LLM 边缘推理加速是核心需求
- ✅ **适用场景**: 移动端 LLM 部署、异构硬件利用
- 💡 **建议**:
  - 集成编译器优化流程
  - 实现异构硬件感知的任务分区

### 4.2 QEIL: Quantifying Edge Intelligence via Inference-time Scaling (arXiv:2602.06057)
**发布时间**: 2026年1月23日  
**作者**: Satyam Kumar, Saurabh Jha

**创新点**:
- 首个统一框架量化边缘 AI 推理时间缩放行为
- 揭示 **幂律缩放行为**：延迟、能耗、任务覆盖范围
- **异构编排** 持续提升能效和覆盖范围
- 三大复合指标：**Intelligence per Watt**, **Energy Coverage Efficiency**, **Price Power Performance**
- **安全优先代理编排器**：动态工作负载分配 + 热约束 + 容错 + 对抗输入验证

**Synapse 集成评估**:
- ✅ **高优先级**: 边缘 AI 量化和优化框架
- ✅ **适用场景**: 多加速器协调、能效优化
- 💡 **建议**:
  - 采用复合指标评估系统效率
  - 实现安全感知的编排器

### 4.3 HybridFlow: Resource-Adaptive Edge-Cloud LLM Inference (arXiv:2512.22137)
**发布时间**: 2025年12月11日  
**作者**: Jiangwen Dong, Jiayu Li, Tianhang Zheng 等

**创新点**:
- **资源自适应边云推理框架**，构建依赖感知 DAG，并行执行解锁的子任务
- **学习效益-成本效用模型** 在线路由每个子任务到边或云
- 动态权衡 **准确率增益** vs **Token/API 和延迟预算**
- 在 GPQA, MMLU-Pro, AIME24, LiveBench-Reasoning 上验证

**Synapse 集成评估**:
- ✅ **高优先级**: 边云协同推理是 Synapse 关键场景
- ✅ **适用场景**: 混合推理、成本优化
- 💡 **建议**:
  - 实现依赖感知的任务 DAG
  - 集成效用模型进行动态路由

### 4.4 LQA: Lightweight Quantized-Adaptive Framework for VLMs on Edge (arXiv:2602.07849)
**发布时间**: 2026年2月8日  
**作者**: Xin Wang, Hong Jia, Hualin Zhou 等

**创新点**:
- **轻量级量化自适应框架**，结合 **模态感知量化** + **无梯度测试时适应**
- **选择性混合量化 (SHQ)** + 量化无梯度适应机制
- 相比基于梯度的 TTA 方法，内存使用降低 **19.9x**
- 整体适应性能提升 **4.5%**，内存少于全精度模型

**Synapse 集成评估**:
- ✅ **高优先级**: VLM 边缘部署量化技术
- ✅ **适用场景**: 多模态模型边缘推理
- 💡 **建议**:
  - 集成模态感知量化策略
  - 支持无梯度在线适应

### 4.5 HQP: Sensitivity-Aware Hybrid Quantization and Pruning (arXiv:2602.06069)
**发布时间**: 2026年2月2日  
**作者**: Dinesh Gopalan, Ratul Ali

**创新点**:
- **敏感度感知结构化剪枝**，使用 **Fisher 信息矩阵** 高效近似
- 动态权重敏感度指标指导冗余滤波器迭代移除
- 剪枝条件性执行：严格遵守最大允许精度下降
- 推理加速 **3.12x**，模型大小减少 **55%**，精度下降 < 1.5%

**Synapse 集成评估**:
- ✅ **高优先级**: 模型压缩是边缘部署必备技术
- ✅ **适用场景**: 模型优化、资源受限部署
- 💡 **建议**:
  - 实现敏感度感知的剪枝-量化协同优化
  - 支持用户定义精度约束

### 4.6 FastUSP: Multi-Level Collaborative Acceleration for Distributed Diffusion (arXiv:2602.10940)
**发布时间**: 2026年2月11日  
**作者**: Guandong Li

**创新点**:
- **三层优化框架**：编译级（CUDA Graphs + 计算通信重排序）+ 通信级（FP8 量化）+ 算子级（双缓冲流水线 Ring Attention）
- 识别 **内核启动开销**（而非通信延迟）是现代高带宽 GPU 互连的主要瓶颈
- 在 FLUX (12B) 上实现 **1.12x-1.16x** 端到端加速

**Synapse 集成评估**:
- ⚠️ **中等优先级**: 主要针对扩散模型
- 💡 **建议**: 编译级优化技术可借鉴到 Synapse

---

## 五、消息队列优化

### 5.1 Stable-MoE: Lyapunov-based Token Routing (arXiv:2512.06784)
（已在调度优化部分详述）

**消息队列相关创新**:
- 确保 **Token 队列和能量队列** 的长期稳定性
- 将长期优化转化为每时隙子问题，无需未来状态知识

**Synapse 集成评估**:
- ✅ **高优先级**: 队列稳定性对消息系统至关重要
- 💡 **建议**: 采用 Lyapunov 漂移加惩罚方法管理消息队列

### 5.2 Latency-aware Human-in-the-Loop RL for Semantic Communications (arXiv:2602.15640)
**发布时间**: 2026年2月17日  
**作者**: Peizheng Li, Xinyi Lin, Adnan Aijaz

**创新点**:
- **时间约束人机回环强化学习 (TC-HITL-RL)** 框架
- 状态捕获 **语义质量、人类偏好、队列松弛、信道动态**
- 动作屏蔽 + 延迟感知奖励整形
- 稳定资源消耗，满足异构截止期限

**Synapse 集成评估**:
- ⚠️ **中等优先级**: 主要针对语义通信
- 💡 **建议**: 队列松弛概念可用于消息优先级调度

### 5.3 FedPSA: Modeling Behavioral Staleness in Asynchronous FL (arXiv:2602.15337)
**发布时间**: 2026年2月17日  
**作者**: Chaoyi Lu

**创新点**:
- 首个利用 **参数敏感度** 测量模型过时性的细粒度 AFL 框架
- **动态动量队列** 实时评估当前训练阶段
- 动态调整对过时信息的容忍度
- 比基线提升 **6.37%**，比 SOTA 提升 **1.93%**

**Synapse 集成评估**:
- ⚠️ **中等优先级**: 主要针对联邦学习
- 💡 **建议**: 过时性建模可应用于消息队列中的陈旧消息处理

---

## 六、Synapse 集成建议汇总

### 6.1 高优先级集成项

| 技术 | 来源论文 | 适用场景 | 实现建议 |
|------|----------|----------|----------|
| **适配器路由机制** | CARL-XRay | 模型版本管理、热更新 | 实现适配器架构支持模型热插拔 |
| **意图驱动调度** | IGAA | 动态资源分配、QoS 保障 | 实现 Network-Service-Intent 矩阵 + 元学习框架 |
| **Lyapunov 优化队列** | Stable-MoE | 队列稳定性保证 | 采用漂移加惩罚方法管理消息队列 |
| **多租户模型服务** | MUSE | 多客户模型托管 | 两级分数变换 + 意图路由 |
| **CXL 内存分层** | Equilibria | 租户内存隔离 | per-tenant 配额 + 公平调度 |
| **边云协同推理** | HybridFlow | 混合推理路由 | 依赖感知 DAG + 效用模型 |
| **SLO 驱动调度** | SLICE | LLM 边缘推理 | 区分 TTFT/TPOT 约束 + 效用最大化 |

### 6.2 架构设计建议

1. **调度层**:
   - 采用 **Lyapunov 优化** 作为底层调度理论框架
   - 集成 **UCB/Bandit** 进行在线资源决策
   - 实现 **意图驱动** 的抽象调度接口

2. **多租户层**:
   - 实现 **两级分数变换** 解耦模型和决策边界
   - 支持 **per-tenant 配额和隔离**
   - 集成 **δ-公平性** 算法保障性能隔离

3. **推理层**:
   - 支持 **MoE 专家缓存和动态加载**
   - 实现 **边云协同推理路由**
   - 集成 **量化-剪枝协同优化**

4. **消息层**:
   - 采用 **Lyapunov 漂移** 保证队列稳定性
   - 支持 **延迟感知** 的消息优先级调度
   - 实现 **过时性感知** 的消息处理

### 6.3 技术栈建议

```yaml
调度核心:
  - Lyapunov 优化框架
  - UCB/Bandit 在线决策
  - 元学习快速适配

多租户支持:
  - per-tenant 资源隔离
  - 公平调度算法
  - 意图驱动路由

推理优化:
  - MoE 专家管理
  - 量化-剪枝协同
  - 边云协同路由

消息系统:
  - 队列稳定性保证
  - 延迟感知调度
  - 过时性建模
```

---

## 七、参考文献

1. Kavitha et al., "Task-Agnostic Continual Learning for Chest Radiograph Classification," arXiv:2602.15811, 2026
2. Maes et al., "stable-worldmodel-v1: Reproducible World Modeling Research," arXiv:2602.08968, 2026
3. Sun et al., "IGAA: Intent-Driven General Agentic AI for Edge Services Scheduling," arXiv:2601.13702, 2026
4. Wu et al., "A Scheduling Framework for Efficient MoE Inference on Edge GPU-NDP Systems," arXiv:2601.03992, 2026
5. Qi et al., "FUSION: Forecast-Embedded Agent Scheduling," arXiv:2512.14323, 2025
6. Chow, "SLICE: SLO-Driven Scheduling for LLM Inference on Edge," arXiv:2510.18544, 2025
7. Xu et al., "Online GPU Energy Optimization with Switching-Aware Bandits," arXiv:2410.11855, 2024
8. Shi et al., "Stable-MoE: Lyapunov-based Token Routing," arXiv:2512.06784, 2025
9. Correia et al., "MUSE: Multi-Tenant Model Serving," arXiv:2602.11776, 2026
10. Zabreyko et al., "MonkeyTree: Near-Minimal Congestion for Multi-tenant Training," arXiv:2602.08296, 2026
11. Zhao et al., "Equilibria: Fair Multi-Tenant CXL Memory Tiering," arXiv:2602.08800, 2026
12. Griggs et al., "Delta Fair Sharing: Performance Isolation for Multi-Tenant Storage," arXiv:2601.20030, 2026
13. Lin et al., "LobRA: Multi-tenant Fine-tuning over Heterogeneous Data," arXiv:2509.01193, 2025
14. Ruiz y Mesa et al., "Compiler-Assisted Speculative Sampling," arXiv:2602.08060, 2026
15. Kumar & Jha, "QEIL: Quantifying Edge Intelligence," arXiv:2602.06057, 2026
16. Dong et al., "HybridFlow: Resource-Adaptive Edge-Cloud LLM Inference," arXiv:2512.22137, 2025
17. Wang et al., "LQA: Lightweight Quantized-Adaptive Framework for VLMs," arXiv:2602.07849, 2026
18. Gopalan & Ali, "HQP: Sensitivity-Aware Hybrid Quantization and Pruning," arXiv:2602.06069, 2026
19. Shu et al., "FlashMem: Supporting Modern DNN Workloads on Mobile," arXiv:2602.15379, 2026
20. Li, "FastUSP: Multi-Level Collaborative Acceleration for Distributed Diffusion," arXiv:2602.10940, 2026

---

**报告完成时间**: 2026年2月19日 07:38 (Asia/Shanghai)  
**下次更新建议**: 2026年3月
