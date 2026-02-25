# 科技前沿搜集报告

**生成时间**: 2026年2月19日 09:24 (Asia/Shanghai)  
**报告周期**: 2026年2月12日 - 2026年2月18日  
**关注领域**: IoT、AI、边缘计算、分布式系统

---

## 一、arXiv 最新论文精选

### 🔥 边缘计算与云边协同

#### 1. Floe: Federated Specialization for Real-Time LLM-SLM Inference
- **论文编号**: arXiv:2602.14302
- **来源**: IEEE Transactions on Parallel and Distributed Systems
- **摘要**: 提出了Floe框架，一种混合联邦学习架构，将云端大语言模型(LLM)与边缘端小语言模型(SLM)结合，实现低延迟、隐私保护的推理。通过异构感知的LoRA适配策略和logit级融合机制，在实时约束下显著提升边缘设备的模型性能。
- **核心创新**:
  - 云边协同的混合推理架构
  - 异构硬件适配
  - 实时logit融合机制
- **链接**: https://arxiv.org/abs/2602.14302

#### 2. FlashMem: Supporting Modern DNN Workloads on Mobile with GPU Memory Hierarchy Optimizations
- **论文编号**: arXiv:2602.15379
- **摘要**: 针对移动GPU上大模型推理的内存限制问题，提出了FlashMem框架。通过静态确定模型加载调度和动态流式传输，实现了2.0x-8.4x的内存减少和1.7x-75.0x的加速。
- **核心创新**:
  - 内存流式框架替代权重预加载
  - 2.5D纹理内存优化数据变换
  - 支持大规模模型和多DNN工作负载
- **链接**: https://arxiv.org/abs/2602.15379

#### 3. Service Orchestration in the Computing Continuum: Structural Challenges and Vision
- **论文编号**: arXiv:2602.15794
- **摘要**: 探讨了计算连续体(Computing Continuum)中从边缘到云的服务编排挑战，提出了基于神经科学主动推理概念的自组织服务愿景。
- **核心议题**:
  - 计算连续体的结构性问题
  - 自主服务编排的理想解决方案
  - 标准化仿真和评估环境的需求
- **链接**: https://arxiv.org/abs/2602.15794

---

### 🤖 人工智能与机器学习

#### 4. Developing AI Agents with Simulated Data: Why, what, and how?
- **论文编号**: arXiv:2602.15816
- **摘要**: 系统介绍了基于仿真的合成数据生成技术，用于解决AI训练中数据量和质量不足的问题。提供了数字孪生AI仿真解决方案的参考框架。
- **核心内容**:
  - 仿真数据生成的关键概念
  - 数字孪生仿真解决方案
  - 设计与分析框架
- **链接**: https://arxiv.org/abs/2602.15816

#### 5. On the Geometric Coherence of Global Aggregation in Federated GNN
- **论文编号**: arXiv:2602.15510
- **摘要**: 识别了跨域联邦图神经网络中全局聚合的几何失效模式，提出GGRS框架来调节客户端更新，保持关系变换的方向一致性。
- **核心创新**:
  - 几何感知的联邦学习
  - 全局消息传递一致性保持
  - 无需访问客户端数据
- **链接**: https://arxiv.org/abs/2602.15510

---

### 🖥️ 分布式系统与高性能计算

#### 6. Co-Design and Evaluation of a CPU-Free MPI GPU Communication Abstraction
- **论文编号**: arXiv:2602.15356
- **摘要**: 描述了基于MPI的GPU通信API设计，实现CPU-free通信。在Frontier超级计算机上测试显示中等消息延迟降低50%，强扩展性提升28%。
- **核心创新**:
  - CPU-free GPU通信
  - HPE Slingshot 11网卡能力利用
  - Cabana/Kokkos框架集成
- **链接**: https://arxiv.org/abs/2602.15356

#### 7. OServe: Accelerating LLM Serving via Spatial-Temporal Workload Orchestration
- **论文编号**: arXiv:2602.12151
- **摘要**: 提出了OServe系统，通过工作负载感知调度和自适应切换方法，解决LLM服务中的时空异构性问题，性能提升高达2倍。
- **核心创新**:
  - 异构模型部署优化
  - 实时工作负载特征调度
  - 工作负载自适应迁移
- **链接**: https://arxiv.org/abs/2602.12151

#### 8. Evaluation of Dynamic Vector Bin Packing for Virtual Machine Placement
- **论文编号**: arXiv:2602.14704
- **来源**: IEEE IPDPS 2026
- **摘要**: 评估了MinUsageTime动态向量装箱算法在VM放置中的应用，使用Microsoft Azure真实数据集进行实验。
- **研究方向**:
  - 非预知/预知/学习增强在线设置
  - 资源利用率优化
  - 算法结构分析
- **链接**: https://arxiv.org/abs/2602.14704

#### 9. Distributed Semi-Speculative Parallel Anisotropic Mesh Adaptation
- **论文编号**: arXiv:2602.15204
- **摘要**: 提出分布式内存方法进行各向异性网格自适应，避免集体通信和全局同步，可生成高达10亿元素的网格。
- **核心创新**:
  - 共享内存与分布式内存分离设计
  - 推测执行模型
  - HPC架构并发利用
- **链接**: https://arxiv.org/abs/2602.15204

---

### 🔐 安全与Web3

#### 10. Bloom Filter Look-Up Tables for Private and Secure Distributed Databases in Web3
- **论文编号**: arXiv:2602.13167
- **摘要**: 提出了基于BFLUT算法的去中心化数据库方案，利用OrbitDB、IPFS和IPNS实现安全私密的密钥管理。
- **核心技术**:
  - 密钥分布式编码存储
  - 无显式存储的密钥管理
  - Web3安全基础设施
- **链接**: https://arxiv.org/abs/2602.13167

---

### 🤖 分布式机器人系统

#### 11. Min-Sum Uniform Coverage Problem by Autonomous Mobile Robots
- **论文编号**: arXiv:2602.11125
- **摘要**: 研究了自主移动机器人群在线段和圆上的最小和均匀覆盖问题，在Look-Compute-Move模型下提出最优解算法。
- **核心贡献**:
  - 确定性分布式算法
  - 最小总移动成本
  - 不可解配置特征刻画
- **链接**: https://arxiv.org/abs/2602.11125

---

## 二、技术趋势分析

### 📈 关键趋势

1. **边缘AI持续升温**
   - LLM向边缘设备下沉成为热点
   - 云边协同推理框架快速发展
   - 移动端GPU优化技术日益重要

2. **联邦学习演进**
   - 从传统联邦学习向几何感知、图神经网络扩展
   - 隐私保护与模型性能的平衡优化
   - 异构环境下的适配策略

3. **分布式系统性能优化**
   - CPU-free通信成为HPC新方向
   - 时空异构性调度研究兴起
   - GPU集群通信效率提升

4. **LLM服务优化**
   - 工作负载感知的动态调度
   - 模型部署的自适应切换
   - 多设备并行推理

### 🔬 研究热点词云

```
边缘计算 | 联邦学习 | LLM推理 | GPU优化 | 云边协同
分布式训练 | 隐私保护 | 实时系统 | 资源调度 | 移动AI
```

---

## 三、推荐阅读

### 必读论文 (本周推荐)

| 优先级 | 论文 | 理由 |
|--------|------|------|
| ⭐⭐⭐ | Floe | 云边LLM协同的前沿方案 |
| ⭐⭐⭐ | FlashMem | 移动端大模型落地的关键技术 |
| ⭐⭐ | OServe | LLM服务优化的新思路 |
| ⭐⭐ | GGRS | 联邦图神经网络的重要进展 |

---

## 四、数据统计

- **cs.DC (分布式计算)**: 本周约50篇新论文
- **cs.AI (人工智能)**: 本周约130篇新论文
- **cs.NI (网络与互联网架构)**: 本周约90篇新论文
- **cs.LG (机器学习)**: 大量交叉论文

---

## 五、备注

- GitHub Trending 数据获取失败，建议配置 Brave Search API 以获取更全面的开源项目信息
- Distill.pub 已于2021年进入休眠期，无新内容
- 部分论文为会议扩展版本（如IPDPS 2026）

---

*本报告由 OpenClaw 自动生成 | Cron Job: 科技前沿搜集*
