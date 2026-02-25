"""
场景模板 - 预定义的智能场景
"""

from typing import Dict, Any, List
from . import Scene, Trigger, TriggerType, Action, ActionType, Condition


class SceneTemplates:
    """场景模板"""

    @staticmethod
    def morning_routine() -> Scene:
        """早安场景"""
        return Scene(
            scene_id="template_morning",
            name="早安场景",
            description="早上自动执行的场景",
            triggers=[
                Trigger(
                    trigger_type=TriggerType.TIME,
                    config={"time": "07:00", "days": ["mon", "tue", "wed", "thu", "fri"]}
                )
            ],
            actions=[
                Action(
                    action_type=ActionType.NOTIFY,
                    config={"message": "早上好！新的一天开始了"}
                ),
                Action(
                    action_type=ActionType.DEVICE_CONTROL,
                    config={"device_type": "light", "command": "turn_on"}
                ),
                Action(
                    action_type=ActionType.DEVICE_CONTROL,
                    config={"device_type": "thermostat", "command": "set_temperature", "params": {"temperature": 22}}
                )
            ]
        )

    @staticmethod
    def leave_home() -> Scene:
        """离家场景"""
        return Scene(
            scene_id="template_leave",
            name="离家场景",
            description="离开家时自动关闭设备",
            triggers=[
                Trigger(
                    trigger_type=TriggerType.MANUAL,
                    config={}
                )
            ],
            actions=[
                Action(
                    action_type=ActionType.DEVICE_CONTROL,
                    config={"device_type": "light", "command": "turn_off"}
                ),
                Action(
                    action_type=ActionType.DEVICE_CONTROL,
                    config={"device_type": "switch", "command": "turn_off"}
                ),
                Action(
                    action_type=ActionType.DEVICE_CONTROL,
                    config={"device_type": "thermostat", "command": "set_mode", "params": {"mode": "away"}}
                )
            ]
        )

    @staticmethod
    def good_night() -> Scene:
        """晚安场景"""
        return Scene(
            scene_id="template_night",
            name="晚安场景",
            description="睡前自动关闭设备",
            triggers=[
                Trigger(
                    trigger_type=TriggerType.TIME,
                    config={"time": "22:30"}
                )
            ],
            actions=[
                Action(
                    action_type=ActionType.NOTIFY,
                    config={"message": "晚安！祝您好梦"}
                ),
                Action(
                    action_type=ActionType.DEVICE_CONTROL,
                    config={"device_type": "light", "command": "turn_off"}
                ),
                Action(
                    action_type=ActionType.DEVICE_CONTROL,
                    config={"device_type": "camera", "command": "start_recording"}
                )
            ]
        )

    @staticmethod
    def temperature_control() -> Scene:
        """智能温控场景"""
        return Scene(
            scene_id="template_temp_control",
            name="智能温控",
            description="根据温度自动调节",
            triggers=[
                Trigger(
                    trigger_type=TriggerType.CONDITION,
                    config={"field": "temperature", "operator": "gt", "value": 28}
                )
            ],
            actions=[
                Action(
                    action_type=ActionType.DEVICE_CONTROL,
                    config={"device_type": "thermostat", "command": "set_mode", "params": {"mode": "cool"}}
                )
            ]
        )

    @staticmethod
    def security_mode() -> Scene:
        """安防模式"""
        return Scene(
            scene_id="template_security",
            name="安防模式",
            description="启动安防监控",
            triggers=[
                Trigger(
                    trigger_type=TriggerType.MANUAL,
                    config={}
                )
            ],
            actions=[
                Action(
                    action_type=ActionType.DEVICE_CONTROL,
                    config={"device_type": "camera", "command": "start_recording"}
                ),
                Action(
                    action_type=ActionType.NOTIFY,
                    config={"message": "安防模式已启动"}
                )
            ]
        )

    @staticmethod
    def get_all_templates() -> List[Scene]:
        """获取所有模板"""
        return [
            SceneTemplates.morning_routine(),
            SceneTemplates.leave_home(),
            SceneTemplates.good_night(),
            SceneTemplates.temperature_control(),
            SceneTemplates.security_mode(),
        ]
