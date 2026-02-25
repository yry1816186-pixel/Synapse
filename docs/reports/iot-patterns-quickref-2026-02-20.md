# IoT开源项目设计模式速查表

**日期**: 2026年2月20日  
**用途**: 快速查阅核心设计模式和代码结构

---

## 一、核心设计模式速览

### 1. 事件驱动模式

**Home Assistant风格** (Python)
```python
class EventBus:
    def __init__(self):
        self._listeners = defaultdict(list)
    
    def listen(self, event_type, listener):
        self._listeners[event_type].append(listener)
    
    async def fire(self, event_type, data=None):
        event = {'event_type': event_type, 'data': data}
        await asyncio.gather(*[
            listener(event) 
            for listener in self._listeners[event_type]
        ])
```

**适用场景**: 所有IoT平台的核心通信机制

---

### 2. 状态机模式

**集中式状态管理**
```python
class StateMachine:
    def __init__(self, event_bus):
        self._states = {}
        self._event_bus = event_bus
    
    async def async_set(self, entity_id, new_state, attributes=None):
        old_state = self._states.get(entity_id)
        state = State(entity_id, new_state, attributes)
        self._states[entity_id] = state
        
        await self._event_bus.fire('state_changed', {
            'entity_id': entity_id,
            'old_state': old_state,
            'new_state': state
        })
```

**适用场景**: 设备状态集中管理

---

### 3. 设备抽象模式

**Entity Platform Pattern**
```python
from abc import ABC, abstractmethod

class Entity(ABC):
    _attr_name: str = None
    _attr_unique_id: str = None
    
    @property
    @abstractmethod
    def state(self) -> str:
        raise NotImplementedError
    
    @property
    def state_attributes(self) -> dict:
        return {}

class LightEntity(Entity):
    async def async_turn_on(self, **kwargs):
        raise NotImplementedError
    
    async def async_turn_off(self, **kwargs):
        raise NotImplementedError
```

**适用场景**: 统一设备接口、插件化设备集成

---

### 4. 数字孪生模式

**期望-实际状态分离**
```go
type DeviceTwin struct {
    DeviceID   string
    Properties map[string]*Property
}

type Property struct {
    Name     string
    Expected interface{}  // 云端设置
    Actual   interface{}  // 设备上报
    Version  string
}

func (dt *DeviceTwin) UpdateExpected(name string, value interface{}) {
    prop := dt.Properties[name]
    prop.Expected = value
    prop.Version = uuid.New().String()
    dt.sendToDevice(name, value)
}
```

**适用场景**: 云边协同、设备状态同步

---

### 5. 规则引擎模式

**SQL-based规则**
```sql
SELECT
    payload.temperature as temp,
    clientid as device_id
FROM "sensor/+/data"
WHERE payload.temperature > 30
```

**动作定义**
```json
{
  "actions": [
    {"type": "kafka", "topic": "alerts"},
    {"type": "webhook", "url": "https://api.example.com/alert"}
  ]
}
```

**适用场景**: 消息过滤、路由、转换

---

### 6. 边缘存储模式

**SQLite轻量级持久化**
```go
type MetaManager struct {
    db *sql.DB
}

func (m *MetaManager) SavePod(pod *v1.Pod) error {
    data, _ := json.Marshal(pod)
    _, err := m.db.Exec(
        "INSERT OR REPLACE INTO meta VALUES(?, ?, ?)",
        pod.UID, "pod", data
    )
    return err
}

func (m *MetaManager) GetPod(uid string) (*v1.Pod, error) {
    var data string
    err := m.db.QueryRow("SELECT value FROM meta WHERE key = ?", uid).Scan(&data)
    var pod v1.Pod
    json.Unmarshal([]byte(data), &pod)
    return &pod, err
}
```

**适用场景**: 边缘离线自治

---

## 二、协议适配器模式

### Device Service抽象

```go
type DeviceService interface {
    Discover() ([]Device, error)
    Get(deviceName, resourceName string) (interface{}, error)
    Set(deviceName, resourceName string, value interface{}) error
    Start() error
    Stop() error
}

// Modbus实现示例
type ModbusDeviceService struct {
    client *ModbusClient
}

func (s *ModbusDeviceService) Get(deviceName, resourceName string) (interface{}, error) {
    switch resourceName {
    case "temperature":
        value, err := s.client.ReadHoldingRegister(slaveID, 0, 1)
        return float64(value[0]) / 10.0, err
    }
    return nil, fmt.Errorf("unknown resource")
}
```

---

## 三、数据集成模式

### Sink/Source抽象

```hocon
# Kafka Sink
bridges.kafka.my_producer {
    bootstrap_hosts = "kafka:9092"
    topic = "iot_telemetry"
    key = "${clientid}"
    value = "${payload}"
}

# TimescaleDB Sink
bridges.timescale.my_tsdb {
    server = "postgres:5432"
    database = "iot_data"
    sql = """
        INSERT INTO sensor_data (time, device_id, temperature)
        VALUES (to_timestamp(${timestamp}/1000), '${clientid}', 
                ${payload.temperature})
    """
}
```

---

## 四、配置流模式

**多步骤配置向导**
```python
class ConfigFlow:
    async def async_step_user(self, user_input=None):
        if user_input:
            self._init_data = user_input
            return await self.async_step_choose_devices()
        
        return self._show_form(
            step_id='user',
            data_schema=vol.Schema({
                vol.Required('host'): str,
                vol.Required('port', default=80): int,
            })
        )
    
    async def async_step_choose_devices(self, user_input=None):
        if user_input:
            return self._create_entry(
                title="My Device",
                data={**self._init_data, **user_input}
            )
        
        devices = await self._discover_devices()
        return self._show_form(
            step_id='choose_devices',
            data_schema=vol.Schema({
                vol.Required('devices'): vol.All(cv.ensure_list, [vol.In(devices)])
            })
        )
```

---

## 五、消息传递模式

### Node-RED风格

**标准消息结构**
```javascript
{
    topic: "sensor/temperature",
    payload: 23.5,
    timestamp: 1708334400000,
    _msgid: "abc123",
    device_id: "sensor_001"
}
```

**多输出路由**
```javascript
node.on('input', function(msg) {
    if (msg.payload > 30) {
        node.send([msg, null]);  // 输出口1
    } else {
        node.send([null, msg]);  // 输出口2
    }
});
```

**Context存储**
```javascript
// Node Context
node.context().set('counter', 0);

// Flow Context
flow.set('device_states', {sensor1: 23.5});

// Global Context
global.set('system_config', {interval: 5000});
```

---

## 六、云边协同模式

**KubeEdge风格**
```go
// CloudHub - 云端
type CloudHub struct {
    clients     map[string]*ClientConnection
    messageChan chan *Message
}

func (ch *CloudHub) dispatchMessages() {
    for msg := range ch.messageChan {
        nodeName := msg.GetResource()
        if client, exists := ch.clients[nodeName]; exists {
            client.Send(msg)
        }
    }
}

// EdgeHub - 边缘端
type EdgeHub struct {
    cloudClient *CloudClient
    metaManager *MetaManager
}

func (eh *EdgeHub) syncToCloud() {
    for {
        msg := eh.metaManager.GetPendingMessage()
        if msg != nil {
            eh.cloudClient.Send(msg)
        }
    }
}
```

---

## 七、技术选型速查

| 需求 | 推荐方案 | 参考项目 |
|------|---------|---------|
| **事件总线** | asyncio + EventBus | Home Assistant |
| **状态管理** | StateMachine + Event Bus | Home Assistant |
| **设备抽象** | Entity Platform | Home Assistant |
| **协议适配** | Device Service | EdgeX, KubeEdge |
| **消息通信** | MQTT 5.0 | EMQX |
| **规则引擎** | SQL-based | EMQX |
| **边缘存储** | SQLite | KubeEdge |
| **云边协同** | WebSocket + MQTT | KubeEdge |
| **数据集成** | Sink/Source | EMQX |
| **可视化编排** | Flow Designer | Node-RED |

---

## 八、项目实施检查清单

### MVP核心功能
- [ ] Event Bus实现
- [ ] State Machine实现
- [ ] Entity抽象基类
- [ ] 设备注册中心
- [ ] 基础REST API
- [ ] MQTT集成
- [ ] 规则引擎基础版
- [ ] Web UI (设备列表)

### Phase 2扩展
- [ ] Python插件系统
- [ ] 协议适配器（Zigbee, Modbus）
- [ ] 设备自动发现
- [ ] Config Flow UI

### Phase 3高级功能
- [ ] 可视化Flow Designer
- [ ] 数据导出（Kafka, TimescaleDB）
- [ ] 边缘运行时（可选）
- [ ] 云边同步（可选）

---

## 九、性能优化要点

### 并发处理
- **Erlang/OTP**: 百万级连接（EMQX）
- **asyncio**: 异步非阻塞（Home Assistant）
- **Go协程**: 轻量级并发（KubeEdge, EdgeX）

### 存储优化
- **SQLite**: 边缘轻量级存储
- **TimescaleDB**: 时序数据优化
- **RocksDB**: 高性能KV存储

### 网络优化
- **MQTT over QUIC**: 弱网环境优化
- **WebSocket长连接**: 实时通信
- **消息压缩**: GZIP减少传输

---

## 十、最佳实践总结

### 架构设计
1. **事件驱动优先**: 所有操作异步化
2. **分层解耦**: 设备-服务-UI三层分离
3. **插件化**: 易于扩展新设备
4. **配置即代码**: YAML/JSON配置

### 代码组织
1. **Entity抽象**: 统一设备接口
2. **Protocol Adapter**: 协议适配器模式
3. **Coordinator**: 定期数据更新管理
4. **Error Recovery**: 自动重连和降级

### 性能优化
1. **懒加载**: 按需加载集成
2. **批量处理**: 减少API调用
3. **本地缓存**: SQLite边缘存储
4. **消息队列**: 削峰填谷

---

**快速链接**:
- 详细报告: `iot-opensource-analysis-2026-02-20.md`
- 代码示例: 见完整报告第1-6节
- 架构图: 见完整报告附录
