
# Synapse API 文档

## 基础信息

- Base URL: `http://localhost:8000/api/v1`
- 认证: Bearer Token
- 格式: JSON

## 认证

### 获取 Token

```http
POST /auth/token
Content-Type: application/json

{
  "username": "admin",
  "password": "password"
}
```

响应：
```json
{
  "access_token": "xxx",
  "token_type": "bearer"
}
```

## 设备 API

### 列出设备

```http
GET /devices
Authorization: Bearer {token}
```

参数：
- `device_type` (可选): 设备类型过滤
- `state` (可选): 状态过滤
- `page` (可选): 页码，默认 1
- `page_size` (可选): 每页数量，默认 20

响应：
```json
{
  "total": 10,
  "page": 1,
  "page_size": 20,
  "devices": [
    {
      "device_id": "light_1",
      "name": "客厅灯",
      "type": "light",
      "state": "online"
    }
  ]
}
```

### 获取设备详情

```http
GET /devices/{device_id}
Authorization: Bearer {token}
```

响应：
```json
{
  "device_id": "light_1",
  "name": "客厅灯",
  "type": "light",
  "state": "online",
  "status": {
    "is_on": true,
    "brightness": 80
  }
}
```

### 执行设备命令

```http
POST /devices/{device_id}/command
Authorization: Bearer {token}
Content-Type: application/json

{
  "command": "turn_on",
  "params": {}
}
```

响应：
```json
{
  "success": true,
  "result": {
    "is_on": true
  }
}
```

## 场景 API

### 列出场景

```http
GET /scenes
Authorization: Bearer {token}
```

### 创建场景

```http
POST /scenes
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "早安场景",
  "description": "早上自动执行",
  "triggers": [
    {
      "type": "time",
      "config": {"time": "07:00"}
    }
  ],
  "actions": [
    {
      "type": "device_control",
      "config": {
        "device_id": "light_1",
        "command": "turn_on"
      }
    }
  ]
}
```

### 执行场景

```http
POST /scenes/{scene_id}/execute
Authorization: Bearer {token}
Content-Type: application/json

{
  "context": {}
}
```

## 系统 API

### 健康检查

```http
GET /system/health
```

响应：
```json
{
  "status": "healthy",
  "checks": {
    "database": {"status": "healthy", "message": "OK"},
    "redis": {"status": "healthy", "message": "OK"},
    "mqtt": {"status": "healthy", "message": "OK"}
  }
}
```

### 获取指标

```http
GET /system/metrics
Authorization: Bearer {token}
```

响应：
```json
{
  "requests": {
    "count": 1000,
    "mean": 45.2,
    "p95": 120.5
  },
  "counters": {
    "requests_total": 1000
  }
}
```

### 获取状态

```http
GET /system/status
```

响应：
```json
{
  "version": "3.0.0",
  "devices": {
    "total": 10,
    "online": 8
  },
  "scenes": {
    "total": 5,
    "enabled": 4
  }
}
```

## 租户 API

### 创建租户

```http
POST /tenants
Content-Type: application/json

{
  "name": "测试公司",
  "plan": "pro"
}
```

### 获取租户

```http
GET /tenants/{tenant_id}
Authorization: Bearer {token}
```

### 列出租户用户

```http
GET /tenants/{tenant_id}/users
Authorization: Bearer {token}
```

## WebSocket API

### 连接

```javascript
const ws = new WebSocket('ws://localhost:8000/ws');
```

### 订阅主题

```json
{
  "type": "subscribe",
  "topic": "device:light_1"
}
```

### 接收消息

```json
{
  "type": "device_event",
  "device_id": "light_1",
  "data": {
    "state": "on"
  }
}
```

## 错误响应

```json
{
  "detail": "设备不存在"
}
```

HTTP 状态码：
- 200: 成功
- 400: 请求错误
- 401: 未授权
- 404: 资源不存在
- 500: 服务器错误
