"""
Synapse ZeroClaw 边缘协议

定义 Synapse 与 ZeroClaw 之间的通信协议
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
import hashlib


class MessageType(Enum):
    """消息类型"""
    # 心跳
    HEARTBEAT = "heartbeat"
    HEARTBEAT_ACK = "heartbeat_ack"

    # 任务
    TASK_SUBMIT = "task_submit"
    TASK_STATUS = "task_status"
    TASK_RESULT = "task_result"
    TASK_CANCEL = "task_cancel"

    # 传感器
    SENSOR_READ = "sensor_read"
    SENSOR_DATA = "sensor_data"
    SENSOR_COMMAND = "sensor_command"

    # 规则
    RULE_EXECUTE = "rule_execute"
    RULE_RESULT = "rule_result"

    # API 调用
    API_CALL = "api_call"
    API_RESPONSE = "api_response"

    # 配置
    CONFIG_SYNC = "config_sync"
    CONFIG_UPDATE = "config_update"


@dataclass
class EdgeMessage:
    """边缘消息"""
    msg_type: MessageType
    msg_id: str
    timestamp: datetime
    source: str
    target: str
    payload: Dict[str, Any]
    signature: Optional[str] = None

    def to_json(self) -> str:
        return json.dumps({
            "msg_type": self.msg_type.value,
            "msg_id": self.msg_id,
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
            "target": self.target,
            "payload": self.payload,
            "signature": self.signature
        })

    @classmethod
    def from_json(cls, data: str) -> 'EdgeMessage':
        obj = json.loads(data)
        return cls(
            msg_type=MessageType(obj["msg_type"]),
            msg_id=obj["msg_id"],
            timestamp=datetime.fromisoformat(obj["timestamp"]),
            source=obj["source"],
            target=obj["target"],
            payload=obj["payload"],
            signature=obj.get("signature")
        )


@dataclass
class HeartbeatPayload:
    """心跳负载"""
    node_id: str
    status: str
    memory_used_mb: float
    memory_total_mb: float
    cpu_percent: float
    tasks_running: int
    uptime_seconds: int
    capabilities: List[str]


@dataclass
class SensorReading:
    """传感器读数"""
    sensor_id: str
    sensor_type: str
    value: float
    unit: str
    timestamp: datetime
    quality: float = 1.0  # 0-1

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sensor_id": self.sensor_id,
            "sensor_type": self.sensor_type,
            "value": self.value,
            "unit": self.unit,
            "timestamp": self.timestamp.isoformat(),
            "quality": self.quality
        }


@dataclass
class RuleTrigger:
    """规则触发"""
    rule_id: str
    trigger_type: str  # "threshold", "schedule", "event"
    conditions: Dict[str, Any]
    actions: List[Dict[str, Any]]


# 协议常量
PROTOCOL_VERSION = "1.0"
DEFAULT_PORT = 9527
HEARTBEAT_INTERVAL = 30  # 秒
TASK_TIMEOUT = 300  # 秒


def generate_message_id(source: str, msg_type: MessageType) -> str:
    """生成消息 ID"""
    timestamp = datetime.now().isoformat()
    data = f"{source}:{msg_type.value}:{timestamp}"
    return hashlib.md5(data.encode()).hexdigest()[:16]


def sign_message(msg: EdgeMessage, secret: str) -> str:
    """签名消息"""
    data = f"{msg.msg_id}:{msg.timestamp.isoformat()}:{secret}"
    return hashlib.sha256(data.encode()).hexdigest()[:32]


def verify_signature(msg: EdgeMessage, secret: str) -> bool:
    """验证签名"""
    if not msg.signature:
        return False
    expected = sign_message(msg, secret)
    return msg.signature == expected
