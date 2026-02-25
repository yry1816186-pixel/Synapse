# Synapse 智枢 v3.0

> 企业级开源物联网平台（本地优先 + 云可选）

## 快速开始

```bash
# 克隆项目
git clone https://github.com/synapse-iot/synapse.git
cd synapse

# 安装依赖
pip install -r requirements.txt

# 启动
python -m src.start
```

## 项目结构

```
Synapse/
├── src/
│   ├── core/           # 核心模块
│   ├── device_abstraction/  # 设备抽象层
│   ├── scene_engine/   # 场景引擎
│   ├── tenancy/        # 多租户系统
│   ├── ai/             # AI 模块
│   ├── edge/           # 边缘计算
│   ├── integrations/   # 第三方集成
│   ├── api/            # RESTful API
│   └── persistence/    # 数据持久化
├── frontend/           # Vue.js 前端
├── tests/              # 测试
├── docs/               # 文档
├── config/             # 配置
├── scripts/            # 脚本
└── docker/             # Docker
```

## 核心功能

| 模块 | 描述 |
|------|------|
| 插件系统 | 32+ 生命周期 Hook |
| 事件总线 | 发布-订阅模式 |
| 场景引擎 | 触发器-条件-动作 |
| Hope 模块 | 持续学习能力 |
| 边云协同 | 隐私优先推理 |
| 多租户 | 企业级隔离 |

## 技术栈

- **后端**: Python, FastAPI, SQLAlchemy
- **消息**: MQTT, Redis
- **前端**: Vue.js
- **部署**: Docker, docker-compose

## API 文档

启动后访问：
- Swagger: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 贡献

欢迎贡献！请查看 CONTRIBUTING.md

## 许可证

MIT License
