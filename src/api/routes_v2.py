"""
完整 API 路由
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Path, Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from datetime import datetime

# ============ 请求模型 ============

class PaginationParams:
    def __init__(
        self,
        page: int = Query(1, ge=1),
        page_size: int = Query(20, ge=1, le=100)
    ):
        self.page = page
        self.page_size = page_size


# ============ 设备路由 ============

device_router = APIRouter(prefix="/devices", tags=["devices"])


@device_router.get("/")
async def list_devices(
    device_type: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    pagination: PaginationParams = Depends()
):
    """列出设备"""
    from ..device_abstraction import device_registry

    devices = device_registry.list_all()

    # 过滤
    if device_type:
        from ..device_abstraction import DeviceType
        try:
            dt = DeviceType(device_type)
            devices = [d for d in devices if d.device_type == dt]
        except ValueError:
            pass

    if state:
        from ..device_abstraction import DeviceState
        try:
            ds = DeviceState(state)
            devices = [d for d in devices if d.state == ds]
        except ValueError:
            pass

    # 分页
    start = (pagination.page - 1) * pagination.page_size
    end = start + pagination.page_size
    paginated = devices[start:end]

    return {
        "total": len(devices),
        "page": pagination.page,
        "page_size": pagination.page_size,
        "devices": [
            {
                "device_id": d.device_id,
                "name": d.name,
                "type": d.device_type.value,
                "state": d.state.value
            }
            for d in paginated
        ]
    }


@device_router.get("/{device_id}")
async def get_device(device_id: str = Path(...)):
    """获取设备详情"""
    from ..device_abstraction import device_registry

    device = device_registry.get(device_id)
    if not device:
        raise HTTPException(status_code=404, detail="设备不存在")

    return {
        "device_id": device.device_id,
        "name": device.name,
        "type": device.device_type.value,
        "state": device.state.value,
        "status": device.status.__dict__ if device.status else None
    }


@device_router.post("/{device_id}/command")
async def execute_device_command(
    device_id: str = Path(...),
    command: str = Body(...),
    params: Dict[str, Any] = Body(default={})
):
    """执行设备命令"""
    from ..device_abstraction import device_registry
    from ..core.metrics import performance_monitor

    device = device_registry.get(device_id)
    if not device:
        raise HTTPException(status_code=404, detail="设备不存在")

    start_time = datetime.now()
    result = await device.execute(command, params)
    duration_ms = (datetime.now() - start_time).total_seconds() * 1000

    performance_monitor.record_device_operation(
        device_id, command, result.get("success", False), duration_ms
    )

    return {"success": True, "result": result}


# ============ 场景路由 ============

scene_router = APIRouter(prefix="/scenes", tags=["scenes"])


@scene_router.get("/")
async def list_scenes(pagination: PaginationParams = Depends()):
    """列出场景"""
    from ..scene_engine import scene_engine

    scenes = scene_engine.list_scenes()
    start = (pagination.page - 1) * pagination.page_size
    end = start + pagination.page_size
    paginated = scenes[start:end]

    return {
        "total": len(scenes),
        "page": pagination.page,
        "page_size": pagination.page_size,
        "scenes": [s.to_dict() for s in paginated]
    }


@scene_router.post("/")
async def create_scene(
    name: str = Body(...),
    description: str = Body(""),
    triggers: List[Dict[str, Any]] = Body(default=[]),
    actions: List[Dict[str, Any]] = Body(default=[])
):
    """创建场景"""
    from ..scene_engine import Scene, scene_engine, Trigger, TriggerType, Action, ActionType

    scene = Scene(
        name=name,
        description=description
    )

    for t in triggers:
        trigger = Trigger(
            trigger_type=TriggerType(t.get("type", "manual")),
            config=t.get("config", {})
        )
        scene.triggers.append(trigger)

    for a in actions:
        action = Action(
            action_type=ActionType(a.get("type", "device_control")),
            config=a.get("config", {})
        )
        scene.actions.append(action)

    await scene_engine.register_scene(scene)

    return {"success": True, "scene_id": scene.scene_id}


@scene_router.post("/{scene_id}/execute")
async def execute_scene(
    scene_id: str = Path(...),
    context: Dict[str, Any] = Body(default={})
):
    """执行场景"""
    from ..scene_engine import scene_engine, TriggerType
    from ..core.metrics import performance_monitor

    try:
        start_time = datetime.now()
        execution_id = await scene_engine.trigger_scene(
            scene_id,
            TriggerType.MANUAL,
            context
        )
        duration_ms = (datetime.now() - start_time).total_seconds() * 1000

        performance_monitor.record_scene_execution(scene_id, True, duration_ms)

        return {"success": True, "execution_id": execution_id}

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============ 系统路由 ============

system_router = APIRouter(prefix="/system", tags=["system"])


@system_router.get("/health")
async def health_check():
    """健康检查"""
    from ..core.health import health_checker

    results = await health_checker.run_all()

    return {
        "status": health_checker.get_overall_status().value,
        "checks": {
            name: {
                "status": result.status.value,
                "message": result.message
            }
            for name, result in results.items()
        }
    }


@system_router.get("/metrics")
async def get_metrics():
    """获取指标"""
    from ..core.metrics import performance_monitor

    return performance_monitor.get_summary()


@system_router.get("/status")
async def get_status():
    """获取系统状态"""
    from ..device_abstraction import device_registry
    from ..scene_engine import scene_engine

    devices = device_registry.list_all()
    scenes = scene_engine.list_scenes()

    return {
        "version": "3.0.0",
        "devices": {
            "total": len(devices),
            "online": sum(1 for d in devices if d.state.value == "online")
        },
        "scenes": {
            "total": len(scenes),
            "enabled": sum(1 for s in scenes if s.enabled)
        },
        "timestamp": datetime.now().isoformat()
    }


# ============ 租户路由 ============

tenant_router = APIRouter(prefix="/tenants", tags=["tenants"])


@tenant_router.post("/")
async def create_tenant(
    name: str = Body(...),
    plan: str = Body("free")
):
    """创建租户"""
    from ..tenancy import TenantManager, PlanType

    manager = TenantManager()
    plan_type = PlanType(plan)
    tenant = await manager.create_tenant(name, plan_type)

    return {"success": True, "tenant_id": tenant.tenant_id}


@tenant_router.get("/{tenant_id}")
async def get_tenant(tenant_id: str = Path(...)):
    """获取租户"""
    from ..tenancy import tenant_manager

    tenant = await tenant_manager.get_tenant(tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="租户不存在")

    return {
        "tenant_id": tenant.tenant_id,
        "name": tenant.name,
        "plan": tenant.plan.value,
        "status": tenant.status.value,
        "quota": tenant.quota.__dict__
    }


@tenant_router.get("/{tenant_id}/users")
async def list_tenant_users(tenant_id: str = Path(...)):
    """列出租户用户"""
    from ..tenancy import tenant_manager

    users = tenant_manager.get_users_by_tenant(tenant_id)
    return {
        "total": len(users),
        "users": [
            {
                "user_id": u.user_id,
                "username": u.username,
                "email": u.email,
                "role": u.role
            }
            for u in users
        ]
    }
