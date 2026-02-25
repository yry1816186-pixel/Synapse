# IoT开源项目 - 快速参考卡

**生成日期**: 2026年2月19日

---

## 🏗️ 架构对比速览

| 特性 | Home Assistant | OpenHAB | Node-RED | KubeEdge | EMQX | EdgeX |
|------|---------------|---------|----------|----------|------|-------|
| **编程语言** | Python | Java | Node.js | Go | Erlang | Go |
| **核心架构** | 事件驱动 | OSGi微内核 | 流式编程 | 云边协同 | 分布式集群 | 微服务 |
| **设备抽象** | Entity | Thing | Node | Device Twin | - | Device Service |
| **扩展机制** | Integration | Binding | Custom Node | Mapper | Plugin | Device Service |
| **规则引擎** | Automation | Rules DSL | Flow | - | SQL Rule | Rules Engine |
| **协议支持** | 多协议 | 多协议 | 可扩展 | MQTT | MQTT/QUIC | 多协议 |
| **边缘支持** | 有限 | 有限 | 单机 | ✅ 云边 | ❌ | ✅ |
| **大规模** | 家庭级 | 企业级 | 小规模 | 大规模 | 超大规模 | 企业级 |

---

## 🎯 设计模式速查

### 模式1: 事件总线
```python
# 发布事件
event_bus.publish("device_connected", {"device_id": "light1"})

# 订阅事件
@event_bus.subscribe("device_connected")
async def handle_device_connect(event_data):
    print(f"Device connected: {event_data['device_id']}")
```

**适用场景**: 所有IoT平台  
**参考项目**: Home Assistant, EMQX, KubeEdge

---

### 模式2: 设备抽象
```python
class LightDevice(BaseDevice):
    @property
    def brightness(self) -> int:
        return self._state.get("brightness", 0)
    
    async def set_brightness(self, value: int):
        await self.write_property("brightness", value)
```

**适用场景**: 设备管理  
**参考项目**: Home Assistant, OpenHAB

---

### 模式3: 规则引擎
```python
# SQL风格规则定义
rule = {
    "name": "high_temp_alert",
    "condition": "payload.temperature > 30",
    "actions": [
        {"type": "alert", "message": "高温告警"},
        {"type": "webhook", "url": "http://api/alert"}
    ]
}
```

**适用场景**: 自动化场景  
**参考项目**: EMQX, Node-RED

---

### 模式4: 设备孪生
```json
{
  "deviceId": "sensor001",
  "properties": {
    "temperature": {
      "desired": 25.0,    // 云端期望值
      "reported": 24.5    // 设备上报值
    }
  },
  "metadata": {
    "lastUpdate": 1708334400,
    "version": "1.0.0"
  }
}
```

**适用场景**: 云边协同  
**参考项目**: KubeEdge, Azure IoT Hub

---

## 🔧 常用代码片段

### 1. 异步设备连接
```python
async def connect_device(device: BaseDevice) -> bool:
    try:
        connected = await device.connect()
        if connected:
            await event_bus.publish("device_connected", {
                "device_id": device.metadata.device_id
            })
        return connected
    except Exception as e:
        logger.error(f"Connection failed: {e}")
        return False
```

---

### 2. 状态同步
```python
async def sync_device_state(device_id: str, state: dict):
    # 1. 更新本地状态
    state_machine.update(device_id, state)
    
    # 2. 触发事件
    await event_bus.publish("state_changed", {
        "device_id": device_id,
        "new_state": state
    })
    
    # 3. 检查规则
    await rule_engine.evaluate(state)
```

---

### 3. MQTT消息处理
```python
async def handle_mqtt_message(topic: str, payload: bytes):
    # 解析消息
    message = json.loads(payload)
    
    # 提取设备ID (假设主题格式: device/{device_id}/data)
    device_id = topic.split("/")[1]
    
    # 更新设备状态
    await sync_device_state(device_id, message)
```

---

### 4. 定时任务
```python
# 每分钟执行一次
@scheduled_task(cron="* * * * *")
async def periodic_device_check():
    devices = device_registry.get_all()
    for device in devices:
        if not device.state.online:
            await device.connect()
```

---

## 📊 性能优化技巧

### 1. 减少轮询
❌ **避免**:
```python
while True:
    state = await device.read_state()
    await asyncio.sleep(5)
```

✅ **推荐**:
```python
# 使用事件推送
@device.on_state_change
async def handle_change(new_state):
    await process_state(new_state)
```

---

### 2. 批量处理
```python
# 批量读取设备状态
async def batch_read_devices(device_ids: list) -> dict:
    tasks = [read_device(did) for did in device_ids]
    results = await asyncio.gather(*tasks)
    return dict(zip(device_ids, results))
```

---

### 3. 缓存策略
```python
from functools import lru_cache
from datetime import datetime, timedelta

class DeviceCache:
    def __init__(self, ttl_seconds: int = 60):
        self.cache = {}
        self.ttl = ttl_seconds
    
    async def get(self, device_id: str) -> Optional[dict]:
        if device_id in self.cache:
            data, timestamp = self.cache[device_id]
            if datetime.now() - timestamp < timedelta(seconds=self.ttl):
                return data
        return None
```

---

## 🐛 常见问题与解决方案

### 问题1: 设备频繁掉线
**解决方案**:
```python
class ReconnectableDevice(BaseDevice):
    async def auto_reconnect(self):
        while True:
            if not self.state.online:
                try:
                    await self.connect()
                    logger.info(f"Reconnected: {self.metadata.device_id}")
                except Exception as e:
                    logger.error(f"Reconnect failed: {e}")
            await asyncio.sleep(30)  # 30秒重试一次
```

---

### 问题2: 消息丢失
**解决方案**: 使用QoS保证 (MQTT)
```python
# QoS 1: 至少一次
await mqtt_client.publish(
    topic="device/data",
    payload=json.dumps(data),
    qos=1
)

# QoS 2: 恰好一次
await mqtt_client.publish(
    topic="device/data",
    payload=json.dumps(data),
    qos=2
)
```

---

### 问题3: 状态不一致
**解决方案**: 使用版本号
```python
class StateManager:
    def __init__(self):
        self.states = {}
        self.versions = {}
    
    async def update(self, device_id: str, state: dict, version: int):
        if version > self.versions.get(device_id, 0):
            self.states[device_id] = state
            self.versions[device_id] = version
            return True
        return False  # 旧版本，拒绝更新
```

---

## 🔐 安全最佳实践

### 1. 设备认证
```python
# JWT认证
from jwt import encode, decode

def generate_device_token(device_id: str, secret: str) -> str:
    return encode({
        "device_id": device_id,
        "exp": datetime.now() + timedelta(days=30)
    }, secret)

def verify_device_token(token: str, secret: str) -> Optional[str]:
    try:
        payload = decode(token, secret, algorithms=["HS256"])
        return payload["device_id"]
    except:
        return None
```

---

### 2. 数据加密
```python
from cryptography.fernet import Fernet

class SecureChannel:
    def __init__(self, key: bytes):
        self.cipher = Fernet(key)
    
    def encrypt(self, data: dict) -> bytes:
        return self.cipher.encrypt(json.dumps(data).encode())
    
    def decrypt(self, encrypted: bytes) -> dict:
        return json.loads(self.cipher.decrypt(encrypted))
```

---

### 3. 访问控制
```python
# RBAC示例
class AccessControl:
    def __init__(self):
        self.permissions = {
            "admin": ["read", "write", "delete"],
            "user": ["read", "write"],
            "guest": ["read"]
        }
    
    def check_permission(self, role: str, action: str) -> bool:
        return action in self.permissions.get(role, [])
```

---

## 📝 配置文件模板

### 设备配置
```yaml
# devices.yaml
devices:
  - id: "light001"
    type: "zigbee_light"
    name: "客厅灯"
    config:
      ieee: "0x1234567890abcdef"
      endpoint: 1
    properties:
      - brightness
      - state
      - color_temp
```

---

### 规则配置
```yaml
# rules.yaml
rules:
  - name: "日落开灯"
    trigger:
      type: "event"
      event: "sunset"
    condition:
      - "device.light001.state == 'home'"
    action:
      - type: "device_command"
        device: "light001"
        command: "turn_on"
        params:
          brightness: 100
```

---

### 集成配置
```yaml
# integrations.yaml
integrations:
  zigbee:
    type: "zigbee"
    config:
      port: "/dev/ttyUSB0"
      baudrate: 115200
  
  mqtt:
    type: "mqtt"
    config:
      broker: "mqtt://localhost:1883"
      username: "admin"
      password: "${MQTT_PASSWORD}"
```

---

## 🧪 测试策略

### 单元测试
```python
import pytest
from unittest.mock import AsyncMock, MagicMock

@pytest.mark.asyncio
async def test_device_connect():
    device = MockDevice()
    connected = await device.connect()
    assert connected == True
    assert device.state.online == True

@pytest.mark.asyncio
async def test_event_bus():
    bus = EventBus()
    handler = AsyncMock()
    bus.subscribe("test_event", handler)
    
    await bus.publish("test_event", {"data": "test"})
    handler.assert_called_once_with({"data": "test"})
```

---

### 集成测试
```python
@pytest.mark.integration
async def test_mqtt_integration():
    # 启动测试MQTT Broker
    broker = await start_test_broker()
    
    # 连接设备
    device = MQTTDevice(broker.url)
    await device.connect()
    
    # 发布消息
    await device.publish("test/topic", {"value": 123})
    
    # 验证接收
    messages = await broker.get_messages("test/topic")
    assert len(messages) == 1
    assert messages[0]["value"] == 123
```

---

## 📦 部署检查清单

### Docker部署
```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制代码
COPY . .

# 启动服务
CMD ["python", "-m", "synapse.main"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  synapse-core:
    build: .
    ports:
      - "8080:8080"
    environment:
      - MQTT_BROKER=mqtt://emqx:1883
      - DB_URL=postgresql://db:5432/synapse
    depends_on:
      - emqx
      - db
  
  emqx:
    image: emqx/emqx:latest
    ports:
      - "1883:1883"
      - "8081:8081"
  
  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=synapse
      - POSTGRES_PASSWORD=secret
    volumes:
      - pgdata:/var/lib/postgresql/data

volumes:
  pgdata:
```

---

### Kubernetes部署
```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: synapse-core
spec:
  replicas: 3
  selector:
    matchLabels:
      app: synapse-core
  template:
    metadata:
      labels:
        app: synapse-core
    spec:
      containers:
      - name: synapse
        image: synapse-iot:latest
        ports:
        - containerPort: 8080
        env:
        - name: MQTT_BROKER
          valueFrom:
            configMapKeyRef:
              name: synapse-config
              key: mqtt-broker
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
```

---

## 📚 推荐阅读

### 官方文档
- [Home Assistant架构](https://developers.home-assistant.io/docs/architecture_index)
- [EMQX规则引擎](https://docs.emqx.com/en/emqx/latest/data-integration/rules.html)
- [KubeEdge云边协同](https://kubeedge.io/docs/architecture/introduction/)

### 技术博客
- [MQTT 5.0新特性详解](https://www.emqx.com/en/blog/introduction-to-mqtt-5)
- [边缘计算架构设计](https://www.edgexfoundry.org/why-edgex-foundry/why-edgex/)
- [设备数字孪生最佳实践](https://azure.microsoft.com/en-us/services/digital-twins/)

---

## 🎓 学习路径

### 初级 (1-2周)
1. 学习MQTT协议基础
2. 阅读Home Assistant源码 (核心部分)
3. 实现简单的设备集成

### 中级 (3-4周)
1. 深入理解事件驱动架构
2. 学习规则引擎设计
3. 实现完整的自动化场景

### 高级 (5-8周)
1. 研究分布式系统设计
2. 学习边缘计算模式
3. 优化性能和可扩展性

---

*快速参考卡 - 随时查阅！*
