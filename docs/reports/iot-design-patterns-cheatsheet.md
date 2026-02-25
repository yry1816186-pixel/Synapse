# IoT 开源项目设计模式速查表

快速参考：从顶级IoT开源项目中提取的设计模式和代码结构

---

## 📦 设备抽象模式 (Device Abstraction)

**来源**: Home Assistant, OpenHAB

```python
from abc import ABC, abstractmethod
from typing import Optional
from enum import Enum

class DeviceState(Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    UNAVAILABLE = "unavailable"

class BaseDevice(ABC):
    """所有设备的抽象基类"""
    
    def __init__(self, device_id: str, name: str):
        self.device_id = device_id
        self.name = name
        self._state = DeviceState.OFFLINE
        self._attributes = {}
    
    @property
    def state(self) -> DeviceState:
        return self._state
    
    @property
    def available(self) -> bool:
        return self._state == DeviceState.ONLINE
    
    @abstractmethod
    async def connect(self) -> bool:
        """连接设备"""
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """断开连接"""
        pass
    
    async def update_state(self) -> None:
        """更新设备状态"""
        pass


class SensorDevice(BaseDevice):
    """传感器设备"""
    
    def __init__(self, device_id: str, name: str, unit: str):
        super().__init__(device_id, name)
        self.unit = unit
        self._value = None
    
    @property
    def value(self) -> Optional[float]:
        return self._value


class SwitchDevice(BaseDevice):
    """开关设备"""
    
    def __init__(self, device_id: str, name: str):
        super().__init__(device_id, name)
        self._is_on = False
    
    @property
    def is_on(self) -> bool:
        return self._is_on
    
    async def turn_on(self) -> None:
        self._is_on = True
    
    async def turn_off(self) -> None:
        self._is_on = False
    
    async def toggle(self) -> None:
        if self._is_on:
            await self.turn_off()
        else:
            await self.turn_on()
```

---

## 🔌 集成注册模式 (Integration Registry)

**来源**: Home Assistant, OpenHAB

```python
from typing import Dict, Type, Callable, Any
import asyncio

class IntegrationRegistry:
    """集成注册中心"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._integrations = {}
            cls._instance._platforms = {}
        return cls._instance
    
    def register(self, domain: str) -> Callable:
        """装饰器：注册集成"""
        def decorator(cls: Type) -> Type:
            self._integrations[domain] = cls
            return cls
        return decorator
    
    def register_platform(self, domain: str, platform: str) -> Callable:
        """装饰器：注册平台"""
        def decorator(cls: Type) -> Type:
            if domain not in self._platforms:
                self._platforms[domain] = {}
            self._platforms[domain][platform] = cls
            return cls
        return decorator
    
    async def async_setup_integration(
        self, 
        domain: str, 
        config: Dict[str, Any]
    ) -> bool:
        """初始化集成"""
        if domain not in self._integrations:
            return False
        
        integration_cls = self._integrations[domain]
        integration = integration_cls()
        return await integration.async_setup(config)
    
    def get_platforms(self, domain: str) -> Dict[str, Type]:
        """获取平台"""
        return self._platforms.get(domain, {})


# 使用示例
registry = IntegrationRegistry()

@registry.register("mqtt")
class MQTTIntegration:
    async def async_setup(self, config):
        self.client = MQTTClient(config['broker'])
        await self.client.connect()
        return True

@registry.register_platform("mqtt", "light")
class MqttLight:
    pass
```

---

## 🌊 流程编排模式 (Flow Orchestration)

**来源**: Node-RED

```javascript
// 节点定义
class FlowNode {
    constructor(config, RED) {
        this.RED = RED;
        this.id = config.id;
        this.type = config.type;
        this.name = config.name;
        this.wires = config.wires || [];  // 连接的下游节点
    }
    
    // 处理输入消息
    onInput(msg, send, done) {
        try {
            const result = this.process(msg);
            send(result);
            done();
        } catch (error) {
            done(error);
        }
    }
    
    // 子类实现具体逻辑
    process(msg) {
        return msg;
    }
    
    // 清理资源
    onClose() {
        // 清理逻辑
    }
}

// 消息定义
const MessageSchema = {
    payload: {},      // 主要数据
    topic: String,    // 主题
    _msgid: String,   // 消息ID（追踪用）
    parts: Object,    // 分片信息（流处理）
    // 自定义字段...
};

// 流程上下文
class FlowContext {
    constructor() {
        this.flow = {};    // 流程级共享数据
        this.global = {};  // 全局共享数据
    }
    
    get(key, scope = 'flow') {
        return this[scope][key];
    }
    
    set(key, value, scope = 'flow') {
        this[scope][key] = value;
    }
}
```

---

## ☁️ 云边同步模式 (Cloud-Edge Sync)

**来源**: KubeEdge

```go
package cloudedge

import (
    "context"
    "encoding/json"
    "sync"
    "time"
    
    "github.com/gorilla/websocket"
)

// 边缘消息
type EdgeMessage struct {
    MessageType string          `json:"messageType"`
    Resource    string          `json:"resource"`
    Operation   string          `json:"operation"`
    Content     json.RawMessage `json:"content"`
    Timestamp   int64           `json:"timestamp"`
}

// 云端Hub
type CloudHub struct {
    clients    map[string]*websocket.Conn
    clientsMux sync.RWMutex
    messageCh  chan *EdgeMessage
}

func NewCloudHub() *CloudHub {
    return &CloudHub{
        clients:   make(map[string]*websocket.Conn),
        messageCh: make(chan *EdgeMessage, 1000),
    }
}

// 广播消息到所有边缘节点
func (h *CloudHub) Broadcast(msg *EdgeMessage) error {
    h.clientsMux.RLock()
    defer h.clientsMux.RUnlock()
    
    for nodeID, conn := range h.clients {
        if err := conn.WriteJSON(msg); err != nil {
            // 处理发送失败
            continue
        }
    }
    return nil
}

// 边缘Hub
type EdgeHub struct {
    cloudConn      *websocket.Conn
    metaManager    *MetaManager
    reconnectDelay time.Duration
}

func (h *EdgeHub) Start(ctx context.Context) error {
    for {
        select {
        case <-ctx.Done():
            return ctx.Err()
        default:
            if err := h.connect(); err != nil {
                time.Sleep(h.reconnectDelay)
                continue
            }
            h.handleMessages(ctx)
        }
    }
}

// 元数据管理器 - 支持离线自治
type MetaManager struct {
    db *sql.DB  // SQLite
}

func (m *MetaManager) Save(resource string, data []byte) error {
    _, err := m.db.Exec(
        "INSERT OR REPLACE INTO meta (resource, data, updated_at) VALUES (?, ?, ?)",
        resource, data, time.Now().Unix(),
    )
    return err
}

func (m *MetaManager) Load(resource string) ([]byte, error) {
    var data []byte
    err := m.db.QueryRow(
        "SELECT data FROM meta WHERE resource = ?", resource,
    ).Scan(&data)
    return data, err
}
```

---

## 🔧 规则引擎模式 (Rule Engine)

**来源**: EMQX, EdgeX Foundry

```go
package rules

import (
    "context"
    "fmt"
    
    "github.com/antonmedv/expr"  // 表达式引擎
)

// 规则定义
type Rule struct {
    ID        string
    Name      string
    Source    string      // 数据源（如MQTT主题）
    Condition string      // SQL/表达式条件
    Actions   []Action    // 触发的动作
    Enabled   bool
}

// 动作接口
type Action interface {
    Execute(ctx context.Context, data interface{}) error
}

// HTTP动作
type HTTPAction struct {
    URL    string
    Method string
    Headers map[string]string
}

func (a *HTTPAction) Execute(ctx context.Context, data interface{}) error {
    // HTTP请求实现
    return nil
}

// 数据库动作
type DatabaseAction struct {
    DSN    string
    Table  string
    Fields []string
}

func (a *DatabaseAction) Execute(ctx context.Context, data interface{}) error {
    // 数据库写入实现
    return nil
}

// 规则引擎
type RuleEngine struct {
    rules    map[string]*Rule
    exprEnv  *expr.Env
}

func NewRuleEngine() *RuleEngine {
    return &RuleEngine{
        rules: make(map[string]*Rule),
    }
}

func (e *RuleEngine) AddRule(rule *Rule) {
    e.rules[rule.ID] = rule
}

func (e *RuleEngine) Process(ctx context.Context, source string, data map[string]interface{}) error {
    for _, rule := range e.rules {
        if !rule.Enabled || rule.Source != source {
            continue
        }
        
        // 评估条件
        program, err := expr.Compile(rule.Condition, expr.Env(data))
        if err != nil {
            return err
        }
        
        result, err := expr.Run(program, data)
        if err != nil {
            return err
        }
        
        // 条件满足，执行动作
        if matched, ok := result.(bool); ok && matched {
            for _, action := range rule.Actions {
                if err := action.Execute(ctx, data); err != nil {
                    // 记录错误，继续执行其他动作
                    fmt.Printf("Action failed: %v\n", err)
                }
            }
        }
    }
    return nil
}
```

---

## 👥 设备孪生模式 (Device Twin)

**来源**: KubeEdge, Azure IoT Hub

```go
package twin

import (
    "encoding/json"
    "sync"
    "time"
)

// 属性值
type TwinValue struct {
    Value     string `json:"value"`
    Timestamp int64  `json:"timestamp"`
}

// 属性元数据
type TwinProperty struct {
    Reported TwinValue `json:"reported,omitempty"`  // 设备上报
    Desired  TwinValue `json:"desired,omitempty"`   // 云端期望
    Metadata struct {
        LastUpdated time.Time `json:"lastUpdated"`
    } `json:"metadata"`
}

// 设备孪生
type DeviceTwin struct {
    DeviceID string                  `json:"deviceId"`
    Tags     map[string]string       `json:"tags,omitempty"`
    Properties map[string]*TwinProperty `json:"properties"`
    mux      sync.RWMutex
}

// 状态同步管理器
type TwinManager struct {
    twins map[string]*DeviceTwin
    mux   sync.RWMutex
}

func NewTwinManager() *TwinManager {
    return &TwinManager{
        twins: make(map[string]*DeviceTwin),
    }
}

// 设备上报状态
func (m *TwinManager) UpdateReported(deviceID string, properties map[string]string) error {
    m.mux.Lock()
    defer m.mux.Unlock()
    
    twin, exists := m.twins[deviceID]
    if !exists {
        twin = &DeviceTwin{
            DeviceID:   deviceID,
            Properties: make(map[string]*TwinProperty),
        }
        m.twins[deviceID] = twin
    }
    
    for key, value := range properties {
        if prop, ok := twin.Properties[key]; ok {
            prop.Reported = TwinValue{
                Value:     value,
                Timestamp: time.Now().Unix(),
            }
        } else {
            twin.Properties[key] = &TwinProperty{
                Reported: TwinValue{
                    Value:     value,
                    Timestamp: time.Now().Unix(),
                },
            }
        }
    }
    
    return nil
}

// 云端设置期望状态
func (m *TwinManager) UpdateDesired(deviceID string, properties map[string]string) error {
    // 类似UpdateReported，设置Desired字段
    return nil
}

// 获取需要同步的差异
func (t *DeviceTwin) GetDesiredDelta() map[string]string {
    t.mux.RLock()
    defer t.mux.RUnlock()
    
    delta := make(map[string]string)
    for key, prop := range t.Properties {
        if prop.Desired.Value != "" && prop.Desired.Value != prop.Reported.Value {
            delta[key] = prop.Desired.Value
        }
    }
    return delta
}
```

---

## 📡 发布订阅模式 (Pub/Sub)

**来源**: EMQX, Home Assistant, Node-RED

```python
from typing import Callable, Dict, List, Set
from dataclasses import dataclass
from enum import Enum
import asyncio

class QoS(Enum):
    AT_MOST_ONCE = 0    # 最多一次
    AT_LEAST_ONCE = 1   # 至少一次
    EXACTLY_ONCE = 2    # 恰好一次

@dataclass
class Message:
    topic: str
    payload: bytes
    qos: QoS
    retain: bool = False

class PubSubBroker:
    """内存发布订阅代理"""
    
    def __init__(self):
        self._subscriptions: Dict[str, Set[Callable]] = {}
        self._retained: Dict[str, Message] = {}
    
    def subscribe(self, topic: str, callback: Callable) -> Callable:
        """订阅主题，返回取消订阅函数"""
        if topic not in self._subscriptions:
            self._subscriptions[topic] = set()
        
        self._subscriptions[topic].add(callback)
        
        # 如果有保留消息，立即回调
        if topic in self._retained:
            callback(self._retained[topic])
        
        def unsubscribe():
            self._subscriptions[topic].discard(callback)
            if not self._subscriptions[topic]:
                del self._subscriptions[topic]
        
        return unsubscribe
    
    async def publish(self, message: Message) -> None:
        """发布消息"""
        # 处理保留消息
        if message.retain:
            self._retained[message.topic] = message
        
        # 匹配订阅者
        for topic_pattern, callbacks in list(self._subscriptions.items()):
            if self._match(topic_pattern, message.topic):
                for callback in callbacks:
                    try:
                        result = callback(message)
                        if asyncio.iscoroutine(result):
                            await result
                    except Exception as e:
                        print(f"Callback error: {e}")
    
    def _match(self, pattern: str, topic: str) -> bool:
        """主题匹配（支持+和#通配符）"""
        # 实现MQTT主题匹配逻辑
        pattern_parts = pattern.split('/')
        topic_parts = topic.split('/')
        
        for i, p in enumerate(pattern_parts):
            if p == '#':
                return True
            if i >= len(topic_parts):
                return False
            if p != '+' and p != topic_parts[i]:
                return False
        
        return len(pattern_parts) == len(topic_parts)


# 使用示例
broker = PubSubBroker()

async def on_temperature(msg: Message):
    print(f"Temperature: {msg.payload.decode()}")

broker.subscribe("sensors/+/temperature", on_temperature)

await broker.publish(Message(
    topic="sensors/living-room/temperature",
    payload=b"25.5",
    qos=QoS.AT_LEAST_ONCE,
))
```

---

## 🏗️ 微服务通信模式

**来源**: EdgeX Foundry

```go
package messaging

import (
    "context"
    "encoding/json"
    "fmt"
    "time"
    
    "github.com/go-redis/redis/v8"
)

// 消息总线接口
type MessageBus interface {
    Publish(ctx context.Context, topic string, message interface{}) error
    Subscribe(ctx context.Context, topic string) (<-chan []byte, error)
}

// Redis实现
type RedisMessageBus struct {
    client *redis.Client
}

func NewRedisMessageBus(addr string) *RedisMessageBus {
    return &RedisMessageBus{
        client: redis.NewClient(&redis.Options{
            Addr: addr,
        }),
    }
}

func (b *RedisMessageBus) Publish(ctx context.Context, topic string, message interface{}) error {
    data, err := json.Marshal(message)
    if err != nil {
        return err
    }
    return b.client.Publish(ctx, topic, data).Err()
}

func (b *RedisMessageBus) Subscribe(ctx context.Context, topic string) (<-chan []byte, error) {
    pubsub := b.client.Subscribe(ctx, topic)
    ch := make(chan []byte, 100)
    
    go func() {
        defer close(ch)
        for {
            select {
            case <-ctx.Done():
                return
            case msg := <-pubsub.Channel():
                ch <- []byte(msg.Payload)
            }
        }
    }()
    
    return ch, nil
}

// 服务发现
type ServiceRegistry interface {
    Register(serviceName, addr string) error
    Discover(serviceName string) (string, error)
    Deregister(serviceName string) error
}

// Consul实现
type ConsulRegistry struct {
    client *api.Client
}

func (r *ConsulRegistry) Register(serviceName, addr string) error {
    return r.client.Agent().ServiceRegister(&api.AgentServiceRegistration{
        Name: serviceName,
        Address: addr,
        Check: &api.AgentServiceCheck{
            HTTP:     fmt.Sprintf("http://%s/health", addr),
            Interval: "10s",
        },
    })
}

// 服务客户端
type ServiceClient struct {
    registry   ServiceRegistry
    httpClient *http.Client
    cache      map[string]string
}

func (c *ServiceClient) Call(ctx context.Context, service, endpoint string, req interface{}) ([]byte, error) {
    // 获取服务地址
    addr, err := c.registry.Discover(service)
    if err != nil {
        return nil, err
    }
    
    // HTTP调用
    url := fmt.Sprintf("http://%s%s", addr, endpoint)
    body, _ := json.Marshal(req)
    
    httpReq, _ := http.NewRequestWithContext(ctx, "POST", url, bytes.NewReader(body))
    resp, err := c.httpClient.Do(httpReq)
    if err != nil {
        return nil, err
    }
    defer resp.Body.Close()
    
    return io.ReadAll(resp.Body)
}
```

---

## 📊 快速选型决策树

```
需求是什么？
│
├─ 智能家居自动化
│   └─ 选择: Home Assistant
│       理由: 本地优先、隐私好、集成多
│
├─ 边缘计算 + 已有K8s
│   └─ 选择: KubeEdge
│       理由: 云原生、边缘自治、统一管理
│
├─ 边缘计算 + 无K8s
│   └─ 选择: EdgeX Foundry
│       理由: 微服务、协议无关、厂商中立
│
├─ 大规模消息/设备连接
│   └─ 选择: EMQX
│       理由: 百万连接、低延迟、规则引擎
│
├─ 可视化流程编排
│   └─ 选择: Node-RED
│       理由: 低代码、可视化、易上手
│
└─ 企业级智能家居
    └─ 选择: OpenHAB
        理由: Java生态、稳定、规则引擎强
```

---

## 🎯 核心设计原则总结

| 原则 | 说明 | 实践项目 |
|------|------|----------|
| **模块化** | 核心与插件分离，支持扩展 | HA, Node-RED, OpenHAB |
| **事件驱动** | 异步消息，解耦组件 | HA, EMQX, Node-RED |
| **边缘自治** | 断网可运行，本地持久化 | KubeEdge, EdgeX |
| **协议抽象** | 统一接口，屏蔽协议差异 | 所有项目 |
| **安全默认** | TLS、认证、授权内置 | EMQX, KubeEdge |
| **可观测** | 日志、指标、追踪 | EMQX, EdgeX |

---

*最后更新: 2026-02-21*
