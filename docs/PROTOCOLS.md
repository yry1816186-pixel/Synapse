# Synapse 协议支持文档

## 支持的协议

Synapse 采用**插件化协议架构**，理论上可以支持任何协议。

### 已内置支持

| 协议 | 类型 | 用途 | 状态 |
|------|------|------|------|
| **MQTT** | 软件协议 | IoT 标准 | ✅ 内置 |
| **HTTP/REST** | 软件协议 | 通用 API | ✅ 内置 |
| **WebSocket** | 软件协议 | 实时通信 | ✅ 内置 |
| **CoAP** | 软件协议 | 物联网 | ✅ 内置 |
| **Modbus** | 工业协议 | 工业设备 | ✅ 内置 |

### 需要硬件支持

| 协议 | 硬件需求 | 设备类型 | 状态 |
|------|---------|---------|------|
| **Zigbee** | Zigbee 模块 (~¥30) | 智能家居 | 🔌 插件 |
| **Z-Wave** | Z-Wave 模块 (~¥100) | 智能家居 | 🔌 插件 |
| **蓝牙/BLE** | 蓝牙适配器 | 可穿戴、传感器 | 🔌 插件 |
| **Thread/Matter** | Thread 模块 | 新标准 | 🔌 插件 |
| **LoRa** | LoRa 模块 | 远距离 | 🔌 插件 |

### 工业协议

| 协议 | 用途 | 状态 |
|------|------|------|
| **OPC UA** | 工业物联网 | 🔌 插件 |
| **CAN Bus** | 汽车、工业 | 🔌 插件 |
| **RS485/RS232** | 传统设备 | 🔌 插件 |
| **Profibus** | 工业自动化 | 🔌 插件 |

## 如何添加新协议

### 1. 创建适配器插件

```python
# adapters/my_protocol.py

from synapse.src.protocols.universal_adapter import (
    ProtocolAdapter, ProtocolType, universal_adapter
)

class MyProtocolAdapter:
    """自定义协议适配器"""

    async def connect(self, config):
        # 连接设备
        pass

    async def discover(self):
        # 发现设备
        pass

    async def read(self, device_id):
        # 读取数据
        pass

    async def write(self, device_id, value):
        # 写入数据
        pass

# 注册适配器
Adapter = lambda: ProtocolAdapter(
    adapter_id="my_protocol",
    name="我的协议",
    protocol_type=ProtocolType.CUSTOM,
    supported_devices=["my_device"]
)
```

### 2. 配置使用

```yaml
# config/protocols.yaml
protocols:
  - id: my_protocol
    enabled: true
    config:
      port: /dev/ttyUSB0
      baud_rate: 9600
```

## 推荐的硬件方案

### 基础版（¥300-500）
- 树莓派 4B (4GB)
- WiFi + 蓝牙（内置）
- 支持：HTTP/MQTT/蓝牙设备

### 标准版（¥500-800）
- 树莓派 5 (4GB)
- CC2652 Zigbee 模块（¥30）
- 支持：HTTP/MQTT/蓝牙/Zigbee

### 专业版（¥1000-2000）
- 树莓派 5 (8GB)
- Zigbee + Z-Wave + LoRa 模块
- 工业级 RS485/RS232 接口
- 支持：几乎所有协议

## 参考项目

| 项目 | 支持协议数 | 开源 |
|------|-----------|------|
| [Home Assistant](https://github.com/home-assistant/core) | 2000+ | ✅ |
| [zigbee2mqtt](https://github.com/Koenkk/zigbee2mqtt) | Zigbee 专用 | ✅ |
| [OpenHAB](https://github.com/openhab) | 300+ | ✅ |
| [Node-RED](https://github.com/node-red/node-red) | 可视化 | ✅ |

## Matter - 未来的统一标准

**Matter** 是 Apple、Google、Amazon、三星联合推出的统一智能家居协议：

- ✅ 跨品牌兼容
- ✅ 本地控制
- ✅ 安全加密
- ✅ 简单配网

**Synapse 将优先支持 Matter 协议。**

---

## 结论

1. **软件层面**：Synapse 已支持主流协议
2. **硬件层面**：需要购买对应的无线模块
3. **开放性**：任何人可以开发插件
4. **未来**：Matter 协议将统一智能家居

**没有真正的"万能接收器"，但 Synapse 可以做到"万能软件适配"。**
