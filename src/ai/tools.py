"""
AI 工具 - 设备和场景控制工具
"""

from typing import Dict, Any, Optional, List
import asyncio
import logging
import json

from ..device_abstraction import device_registry
from ..scene_engine import scene_engine, TriggerType

logger = logging.getLogger(__name__)


# ============ 设备工具 ============

async def tool_list_devices(filter_type: str = None) -> Dict[str, Any]:
    """列出所有设备"""
    devices = device_registry.list_all()

    if filter_type:
        from ..device_abstraction import DeviceType
        try:
            device_type = DeviceType(filter_type)
            devices = [d for d in devices if d.device_type == device_type]
        except ValueError:
            pass

    return {
        "success": True,
        "count": len(devices),
        "devices": [
            {
                "id": d.device_id,
                "name": d.name,
                "type": d.device_type.value,
                "state": d.state.value
            }
            for d in devices
        ]
    }


async def tool_get_device(device_id: str) -> Dict[str, Any]:
    """获取设备详情"""
    device = device_registry.get(device_id)
    if not device:
        return {"success": False, "error": "设备不存在"}

    return {
        "success": True,
        "device": {
            "id": device.device_id,
            "name": device.name,
            "type": device.device_type.value,
            "state": device.state.value,
            "status": device.status.__dict__ if device.status else None
        }
    }


async def tool_control_device(device_id: str, command: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
    """控制设备"""
    device = device_registry.get(device_id)
    if not device:
        return {"success": False, "error": "设备不存在"}

    result = await device.execute(command, params or {})
    return {"success": result.get("success", False), "result": result}


# ============ 场景工具 ============

async def tool_list_scenes() -> Dict[str, Any]:
    """列出所有场景"""
    scenes = scene_engine.list_scenes()

    return {
        "success": True,
        "count": len(scenes),
        "scenes": [s.to_dict() for s in scenes]
    }


async def tool_execute_scene(scene_id: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """执行场景"""
    try:
        execution_id = await scene_engine.trigger_scene(
            scene_id,
            TriggerType.MANUAL,
            context or {}
        )
        return {"success": True, "execution_id": execution_id}
    except ValueError as e:
        return {"success": False, "error": str(e)}


async def tool_get_scene(scene_id: str) -> Dict[str, Any]:
    """获取场景详情"""
    scene = scene_engine.get_scene(scene_id)
    if not scene:
        return {"success": False, "error": "场景不存在"}

    return {"success": True, "scene": scene.to_dict()}


# ============ 系统工具 ============

async def tool_get_system_status() -> Dict[str, Any]:
    """获取系统状态"""
    devices = device_registry.list_all()
    scenes = scene_engine.list_scenes()

    device_states = {}
    for device in devices:
        state = device.state.value
        device_states[state] = device_states.get(state, 0) + 1

    return {
        "success": True,
        "status": {
            "devices": {
                "total": len(devices),
                "by_state": device_states
            },
            "scenes": {
                "total": len(scenes),
                "enabled": sum(1 for s in scenes if s.enabled)
            }
        }
    }


# ============ 工具注册 ============

AI_TOOLS = {
    "list_devices": {
        "func": tool_list_devices,
        "description": "列出所有设备",
        "parameters": {
            "type": "object",
            "properties": {
                "filter_type": {
                    "type": "string",
                    "description": "设备类型过滤（可选）"
                }
            }
        }
    },
    "get_device": {
        "func": tool_get_device,
        "description": "获取设备详情",
        "parameters": {
            "type": "object",
            "properties": {
                "device_id": {"type": "string", "description": "设备ID"}
            },
            "required": ["device_id"]
        }
    },
    "control_device": {
        "func": tool_control_device,
        "description": "控制设备",
        "parameters": {
            "type": "object",
            "properties": {
                "device_id": {"type": "string", "description": "设备ID"},
                "command": {"type": "string", "description": "命令"},
                "params": {"type": "object", "description": "参数"}
            },
            "required": ["device_id", "command"]
        }
    },
    "list_scenes": {
        "func": tool_list_scenes,
        "description": "列出所有场景",
        "parameters": {"type": "object", "properties": {}}
    },
    "execute_scene": {
        "func": tool_execute_scene,
        "description": "执行场景",
        "parameters": {
            "type": "object",
            "properties": {
                "scene_id": {"type": "string", "description": "场景ID"},
                "context": {"type": "object", "description": "执行上下文"}
            },
            "required": ["scene_id"]
        }
    },
    "get_scene": {
        "func": tool_get_scene,
        "description": "获取场景详情",
        "parameters": {
            "type": "object",
            "properties": {
                "scene_id": {"type": "string", "description": "场景ID"}
            },
            "required": ["scene_id"]
        }
    },
    "get_system_status": {
        "func": tool_get_system_status,
        "description": "获取系统状态",
        "parameters": {"type": "object", "properties": {}}
    }
}


def get_tool_definitions() -> List[Dict[str, Any]]:
    """获取工具定义（用于 LLM function calling）"""
    return [
        {
            "type": "function",
            "function": {
                "name": name,
                "description": info["description"],
                "parameters": info["parameters"]
            }
        }
        for name, info in AI_TOOLS.items()
    ]


async def execute_tool(name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """执行工具"""
    if name not in AI_TOOLS:
        return {"error": f"未知工具: {name}"}

    func = AI_TOOLS[name]["func"]
    return await func(**arguments)
