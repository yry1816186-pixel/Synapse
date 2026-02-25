# Synapse 智枢

企业级开源物联网平台（本地优先 + 云可选）

## 特性

- **插件化架构** - 32+ 生命周期 Hook，完全可扩展
- **设备抽象层** - 统一设备接口，支持 17+ 设备类型
- **场景引擎** - 触发器-条件-动作模型，YAML 声明式定义
- **Hope 持续学习** - 基于 Google Nested Learning，越用越懂你
- **多租户系统** - 企业级租户隔离，Casbin 权限控制
- **双引擎调度** - Celery（短期任务）+ Temporal（长期工作流）

## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 启动
python -m synapse.main

# 启动 API 服务
uvicorn synapse.api:app --host 0.0.0.0 --port 8000
```

## 项目结构

```
Synapse/
├── src/
│   ├── core/                 # 核心模块
│   │   ├── plugin_system/    # 插件系统
│   │   ├── event_bus/        # 事件总线
│   │   ├── config/           # 配置管理
│   │   └── scheduler/        # 调度系统
│   ├── device_abstraction/   # 设备抽象层
│   ├── scene_engine/         # 场景引擎
│   │   └── hope/             # 持续学习模块
│   ├── tenancy/              # 多租户系统
│   └── api/                  # RESTful API
├── tests/                    # 测试
├── docs/                     # 文档
└── config/                   # 配置文件
```

## API 文档

启动后访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 许可证

MIT License
