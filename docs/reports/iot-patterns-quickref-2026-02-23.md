# 物联网开源项目设计模式速查表

**更新日期**: 2026-02-23

---

## 项目核心特性速查

| 项目 | 语言 | 架构 | 许可证 | 核心优势 |
|------|------|------|--------|----------|
| **Home Assistant** | Python | 模块化单体 | Apache 2.0 | 2000+集成, 本地优先 |
| **OpenHAB** | Java 21 | OSGi模块化 | EPL-2.0 | 企业级, 热部署 |
| **Node-RED** | JavaScript | 事件驱动 | Apache 2.0 | 可视化编程 |
| **EdgeX Foundry** | Go | 微服务 | Apache 2.0 | 边缘计算中间件 |
| **KubeEdge** | Go | 云边协同 | Apache 2.0 | K8s原生边缘 |
| **EMQX** | Erlang/OTP | 分布式集群 | BSL 1.1 | 1亿+连接支持 |

---

## 设备抽象模式

### Home Assistant
```python
# Entity 抽象
entity_id: "sensor.temperature"
state: "23.5"
attributes:
  unit_of_measurement: "°C"
  device_class: "temperature"
```

### OpenHAB
```java
// 三层抽象
Thing → Channel → Item
// 举例
Thing: zigbee:device:temp_sensor
  └─ Channel: temperature
       └─ Item: Number:Temperature TempItem
```

### EdgeX Foundry
```go
// Device 资源映射
Device → DeviceResource → DeviceCommand
// 举例
Device: sensor-01
  └─ Resource: temperature
       └─ Command: Get → reading
```

### KubeEdge
```yaml
# CRD 设备定义
apiVersion: devices.kubeedge.io/v1alpha2
kind: Device
metadata:
  name: temperature-sensor
spec:
  deviceModelRef:
    name: sensor-model
  propertyVisitors:
  - propertyName: temperature
    visitorConfig:
      protocol: modbus
```

---

## 事件/消息模式

### Home Assistant - EventBus
```python
# 事件发布
hass.bus.fire("custom_event", {"key": "value"})

# 事件订阅
hass.bus.listen("custom_event", callback)
```

### Node-RED - Message Flow
```javascript
// 消息对象
msg = {
    payload: "data",
    topic: "sensor/temperature",
    _msgid: "unique-id"
}
```

### EMQX - MQTT Pub/Sub
```sql
-- 规则引擎
SELECT payload.temp as temperature
FROM "sensor/+/data"
WHERE payload.temp > 25
```

---

## 插件/扩展模式

### Home Assistant - Integration
```python
# 组件注册
DOMAIN = "my_integration"

async def async_setup(hass, config):
    hass.services.register(DOMAIN, "service_name", handler)
    return True
```

### OpenHAB - OSGi Bundle
```java
@ThingScope
public class MyHandler extends BaseThingHandler {
    @Override
    public void initialize() {
        updateStatus(ThingStatus.ONLINE);
    }
}
```

### Node-RED - Custom Node
```javascript
module.exports = function(RED) {
    function MyNode(config) {
        RED.nodes.createNode(this, config);
        this.on('input', function(msg) {
            this.send(msg);
        });
    }
    RED.nodes.registerType("my-node", MyNode);
};
```

### EMQX - Hook
```erlang
%% 注册钩子
emqx_hooks:add('client.connected', {?MODULE, on_client_connected, []}).

on_client_connected(ClientInfo) ->
    %% 处理连接事件
    ok.
```

---

## 配置管理最佳实践

### 目录结构
```
config/
├── main.yaml           # 主配置
├── devices/            # 设备配置
│   ├── sensors.yaml
│   └── actuators.yaml
├── automations/        # 自动化规则
├── integrations/       # 集成配置
└── secrets.yaml        # 敏感信息 (gitignore)
```

### 配置热重载
```yaml
# 推荐实现
automation:
  - id: reload_config
    trigger:
      platform: webhook
    action:
      service: reload_config
```

---

## 安全模式

### 认证层次
```
┌─────────────────────────────────────┐
│  1. 传输层安全 (TLS/SSL)            │
├─────────────────────────────────────┤
│  2. 设备认证 (证书/令牌/密码)       │
├─────────────────────────────────────┤
│  3. 访问控制 (ACL/授权策略)         │
├─────────────────────────────────────┤
│  4. 数据加密 (端到端加密)           │
└─────────────────────────────────────┘
```

### EMQX ACL 示例
```erlang
%% ACL 规则
{allow, {user, "dashboard"}, subscribe, ["$SYS/#"]}.
{allow, {user, "admin"}, pubsub, ["#"]}.
{deny, all, subscribe, ["$SYS/#", "#"]}.
```

---

## 边缘自治模式

### KubeEdge 架构
```
Cloud                          Edge
───────                        ───────
CloudHub ←──WebSocket──→ EdgeHub
    │                              │
    ├── EdgeController             ├── Edged (容器运行时)
    │                              │
    └── DeviceController           └── MetaManager (SQLite)
                                          │
                                          ├── DeviceTwin
                                          └── EventBus (MQTT)
```

### 断网处理策略
1. **元数据本地持久化** (SQLite/RocksDB)
2. **消息队列缓存** (断网期间缓存)
3. **本地规则引擎** (边缘自治决策)
4. **状态同步** (重连后增量同步)

---

## 规则引擎模式

### 触发-条件-动作 (TCA)
```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Trigger    │ →   │  Condition  │ →   │   Action    │
│  (触发器)   │     │  (条件判断) │     │  (执行动作) │
└─────────────┘     └─────────────┘     └─────────────┘
```

### Home Assistant YAML
```yaml
automation:
  trigger:
    - platform: state
      entity_id: sensor.motion
      to: "on"
  condition:
    - condition: state
      entity_id: sun.sun
      state: "below_horizon"
  action:
    - service: light.turn_on
      target:
        entity_id: light.living_room
```

### EMQX SQL
```sql
SELECT
  payload.device_id as device,
  payload.value as reading
FROM "sensors/#"
WHERE payload.value > threshold
```

---

## 性能优化要点

### 连接管理
- 使用连接池
- 心跳保活优化
- 断线重连策略

### 消息处理
- 批量处理 (Batching)
- 背压控制 (Backpressure)
- 异步非阻塞

### 数据存储
- 时序数据库 (InfluxDB/TimescaleDB)
- 分区策略
- 数据保留策略 (TTL)

---

## 快速选型决策树

```
需求: 物联网平台选型
         │
         ▼
    ┌────────────────┐
    │ 需要MQTT消息？ │
    └───────┬────────┘
       Yes  │  No
            │
    ┌───────┴────────┐
    │                │
    ▼                ▼
  EMQX          ┌──────────────┐
               │ 需要边缘计算？ │
               └───────┬────────┘
                  Yes  │  No
                       │
               ┌───────┴────────┐
               │                │
               ▼                ▼
          ┌─────────┐      ┌──────────────┐
          │KubeEdge │      │ 使用K8s管理？│
          │EdgeX    │      └───────┬──────┘
          └─────────┘         Yes  │  No
                              │
                      ┌───────┴────────┐
                      │                │
                      ▼                ▼
                  KubeEdge        ┌──────────────┐
                                  │ 需要可视化？ │
                                  └───────┬──────┘
                                     Yes  │  No
                                          │
                                  ┌───────┴────────┐
                                  │                │
                                  ▼                ▼
                              Node-RED      ┌──────────────┐
                                           │ 企业级需求？ │
                                           └───────┬──────┘
                                              Yes  │  No
                                                    │
                                           ┌────────┴────────┐
                                           │                 │
                                           ▼                 ▼
                                        OpenHAB       Home Assistant
```

---

## 参考链接

- Home Assistant: https://github.com/home-assistant/core
- OpenHAB: https://github.com/openhab/openhab-core
- Node-RED: https://github.com/node-red/node-red
- EdgeX Foundry: https://github.com/edgexfoundry/edgex-go
- KubeEdge: https://github.com/kubeedge/kubeedge
- EMQX: https://github.com/emqx/emqx

---

*Generated: 2026-02-23*
