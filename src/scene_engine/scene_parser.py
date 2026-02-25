"""
YAML 场景解析器 - 声明式场景定义
"""

from typing import Dict, Any, List, Optional
import yaml
import logging

from . import Scene, Trigger, TriggerType, Action, ActionType, Condition

logger = logging.getLogger(__name__)


class SceneParser:
    """场景解析器"""

    @staticmethod
    def parse_yaml(yaml_content: str) -> Scene:
        """解析 YAML 格式的场景定义"""
        data = yaml.safe_load(yaml_content)
        return SceneParser.parse_dict(data)

    @staticmethod
    def parse_file(file_path: str) -> Scene:
        """解析 YAML 文件"""
        with open(file_path, "r", encoding="utf-8") as f:
            return SceneParser.parse_yaml(f.read())

    @staticmethod
    def parse_dict(data: Dict[str, Any]) -> Scene:
        """解析字典格式的场景定义"""
        # 解析触发器
        triggers = []
        for t in data.get("triggers", []):
            trigger = Trigger(
                trigger_type=TriggerType(t.get("type", "manual")),
                config=t.get("config", {}),
                enabled=t.get("enabled", True)
            )
            triggers.append(trigger)

        # 解析动作
        actions = []
        for a in data.get("actions", []):
            # 解析条件
            conditions = []
            for c in a.get("conditions", []):
                condition = Condition(
                    field=c["field"],
                    operator=c["operator"],
                    value=c["value"]
                )
                conditions.append(condition)

            action = Action(
                action_type=ActionType(a.get("type", "device_control")),
                config=a.get("config", {}),
                conditions=conditions,
                timeout=a.get("timeout", 30)
            )
            actions.append(action)

        return Scene(
            scene_id=data.get("id", ""),
            name=data.get("name", ""),
            description=data.get("description", ""),
            triggers=triggers,
            actions=actions,
            enabled=data.get("enabled", True),
            priority=data.get("priority", 5),
            metadata=data.get("metadata", {})
        )

    @staticmethod
    def to_yaml(scene: Scene) -> str:
        """将场景转换为 YAML"""
        data = {
            "id": scene.scene_id,
            "name": scene.name,
            "description": scene.description,
            "enabled": scene.enabled,
            "priority": scene.priority,
            "triggers": [
                {
                    "type": t.trigger_type.value,
                    "config": t.config,
                    "enabled": t.enabled
                }
                for t in scene.triggers
            ],
            "actions": [
                {
                    "type": a.action_type.value,
                    "config": a.config,
                    "conditions": [
                        {"field": c.field, "operator": c.operator, "value": c.value}
                        for c in a.conditions
                    ],
                    "timeout": a.timeout
                }
                for a in scene.actions
            ],
            "metadata": scene.metadata
        }
        return yaml.dump(data, allow_unicode=True, default_flow_style=False)


# 示例 YAML 场景
EXAMPLE_SCENE_YAML = """
id: morning_routine
name: 早安场景
description: 早上自动执行的智能场景
enabled: true
priority: 5

triggers:
  - type: time
    config:
      time: "07:00"
      days: ["mon", "tue", "wed", "thu", "fri"]
    enabled: true

actions:
  - type: notify
    config:
      message: "早上好！新的一天开始了"
  
  - type: device_control
    config:
      device_id: "living_room_light"
      command: "turn_on"
    conditions:
      - field: "occupancy"
        operator: "eq"
        value: true

  - type: device_control
    config:
      device_id: "thermostat_1"
      command: "set_temperature"
      params:
        temperature: 22

metadata:
  category: daily
  author: system
"""
