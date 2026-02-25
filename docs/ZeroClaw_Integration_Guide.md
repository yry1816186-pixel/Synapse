# Synapse + ZeroClaw 集成指南

## 快速开始

### 1. 安装 ZeroClaw（树莓派）

```bash
# 下载 ZeroClaw ARM 版本
wget https://github.com/zeroclaw-labs/zeroclaw/releases/download/v0.1.1/zeroclaw-armv7-unknown-linux-gnueabihf.tar.gz

# 解压
tar -xzf zeroclaw-armv7-unknown-linux-gnueabihf.tar.gz

# 移动到系统目录
sudo mv zeroclaw /usr/local/bin/

# 验证
zeroclaw --version
```

### 2. 配置 ZeroClaw

```bash
# 初始化配置
zeroclaw config init

# 设置云端 API 端点
zeroclaw config set api.endpoint "https://your-synapse-server.com/api/v1"

# 设置 API 密钥
zeroclaw config set api.key "your-api-key"

# 设置节点名称
zeroclaw config set node.name "rpi-zero-01"

# 启用传感器支持
zeroclaw config set sensors.enabled true
```

### 3. 启动 ZeroClaw

```bash
# 前台运行
zeroclaw run

# 后台守护进程
zeroclaw daemon start

# 查看状态
zeroclaw status
```

---

## 传感器配置

### DHT22 温湿度传感器

```yaml
# ~/.zeroclaw/sensors.yaml
sensors:
  - id: dht22_living_room
    type: dht22
    gpio_pin: 4
    interval: 60  # 秒
    enabled: true
```

### 光敏传感器

```yaml
  - id: light_sensor_01
    type: analog
    gpio_pin: 17
    interval: 30
    enabled: true
```

### 继电器控制

```yaml
actuators:
  - id: relay_light_01
    type: relay
    gpio_pin: 18
    initial_state: off
```

---

## 与 Synapse 通信

### API 端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/v1/edge/register` | POST | 注册边缘节点 |
| `/api/v1/edge/heartbeat` | POST | 发送心跳 |
| `/api/v1/edge/sensor/data` | POST | 上报传感器数据 |
| `/api/v1/edge/task/result` | POST | 任务结果回调 |
| `/api/v1/edge/task` | GET | 获取待执行任务 |

### 传感器数据格式

```json
{
  "node_id": "zeroclaw_rpi_01",
  "sensor_id": "dht22_temperature",
  "value": 25.6,
  "unit": "celsius",
  "timestamp": "2026-02-21T21:00:00Z",
  "quality": 0.98
}
```

---

## 规则配置

### 示例规则

```yaml
# ~/.zeroclaw/rules.yaml
rules:
  - id: temp_control
    name: 温度控制
    trigger:
      type: threshold
      sensor: dht22_temperature
      condition: "> 28"
    actions:
      - type: actuator
        target: relay_fan_01
        command: on
      - type: notify
        message: "温度过高，已开启风扇"
```

---

## 硬件连接

### 树莓派 Zero 2W GPIO

```
GPIO 4  -> DHT22 数据脚
GPIO 17 -> 光敏电阻
GPIO 18 -> 继电器 IN
3.3V    -> 传感器 VCC
GND     -> 传感器 GND
```

### ESP32 连接

```
GPIO 21 -> DHT22 数据脚
GPIO 22 -> 继电器 IN
3.3V    -> 传感器 VCC
GND     -> 传感器 GND
```

---

## 成本清单

| 组件 | 型号 | 价格 | 数量 | 小计 |
|------|------|------|------|------|
| 主板 | 树莓派 Zero 2W | $15 | 1 | $15 |
| 存储 | 32GB SD卡 | $8 | 1 | $8 |
| 传感器 | DHT22 | $5 | 2 | $10 |
| 执行器 | 继电器模块 | $3 | 2 | $6 |
| 电源 | 5V 2.5A | $5 | 1 | $5 |
| 线材 | 杜邦线 | $3 | 1 | $3 |
| 外壳 | 3D打印 | $2 | 1 | $2 |
| **总计** | | | | **$49** |

---

## 故障排除

### ZeroClaw 无法启动

```bash
# 检查依赖
zeroclaw doctor

# 查看日志
zeroclaw logs --tail 100
```

### 传感器读取失败

```bash
# 测试 GPIO
zeroclaw test gpio 4

# 检查传感器
zeroclaw test sensor dht22_living_room
```

### 无法连接云端

```bash
# 检查网络
zeroclaw test connection

# 检查 API 密钥
zeroclaw config get api.key
```

---

## 下一步

1. 在树莓派上安装 ZeroClaw
2. 连接传感器和执行器
3. 配置与 Synapse 的通信
4. 测试规则执行
5. 部署到实际环境
