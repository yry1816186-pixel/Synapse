"""
API 层 - RESTful API
"""

from typing import Dict, Any, Optional, List
from fastapi import FastAPI, HTTPException, Depends, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from datetime import datetime
import logging
import uvicorn

logger = logging.getLogger(__name__)

# FastAPI 应用
app = FastAPI(
    title="Synapse API",
    description="企业级开源物联网平台 API",
    version="3.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()


# ============ 请求模型 ============

class DeviceCreateRequest(BaseModel):
    """创建设备请求"""
    name: str
    device_type: str
    config: Dict[str, Any] = Field(default_factory=dict)


class DeviceControlRequest(BaseModel):
    """设备控制请求"""
    command: str
    params: Dict[str, Any] = Field(default_factory=dict)


class SceneCreateRequest(BaseModel):
    """创建场景请求"""
    name: str
    description: str = ""
    triggers: List[Dict[str, Any]] = Field(default_factory=list)
    actions: List[Dict[str, Any]] = Field(default_factory=list)


class SceneExecuteRequest(BaseModel):
    """执行场景请求"""
    context: Dict[str, Any] = Field(default_factory=dict)


class TenantCreateRequest(BaseModel):
    """创建租户请求"""
    name: str
    plan: str = "free"


class UserCreateRequest(BaseModel):
    """创建用户请求"""
    username: str
    email: str
    role: str = "user"


# ============ 响应模型 ============

class BaseResponse(BaseModel):
    """基础响应"""
    success: bool = True
    message: str = ""
    timestamp: datetime = Field(default_factory=datetime.now)


class DeviceResponse(BaseResponse):
    """设备响应"""
    data: Optional[Dict[str, Any]] = None


class SceneResponse(BaseResponse):
    """场景响应"""
    data: Optional[Dict[str, Any]] = None


class TenantResponse(BaseResponse):
    """租户响应"""
    data: Optional[Dict[str, Any]] = None


# ============ 健康检查 ============

@app.get("/health", response_model=BaseResponse)
async def health_check():
    """健康检查"""
    return BaseResponse(message="OK")


@app.get("/")
async def root():
    """根路径"""
    return {
        "name": "Synapse API",
        "version": "3.0.0",
        "status": "running"
    }


# ============ 设备 API ============

@app.get("/api/v1/devices", response_model=DeviceResponse)
async def list_devices():
    """列出所有设备"""
    from ..device_abstraction import device_registry
    devices = device_registry.list_all()
    return DeviceResponse(
        data={"devices": [d.info.__dict__ for d in devices]}
    )


@app.get("/api/v1/devices/{device_id}", response_model=DeviceResponse)
async def get_device(device_id: str):
    """获取设备"""
    from ..device_abstraction import device_registry
    device = device_registry.get(device_id)
    if not device:
        raise HTTPException(status_code=404, detail="设备不存在")
    return DeviceResponse(data=device.info.__dict__)


@app.post("/api/v1/devices/{device_id}/control", response_model=DeviceResponse)
async def control_device(device_id: str, request: DeviceControlRequest):
    """控制设备"""
    from ..device_abstraction import device_registry
    device = device_registry.get(device_id)
    if not device:
        raise HTTPException(status_code=404, detail="设备不存在")

    result = await device.execute(request.command, request.params)
    return DeviceResponse(data=result)


# ============ 场景 API ============

@app.get("/api/v1/scenes", response_model=SceneResponse)
async def list_scenes():
    """列出所有场景"""
    from ..scene_engine import scene_engine
    scenes = scene_engine.list_scenes()
    return SceneResponse(
        data={"scenes": [s.to_dict() for s in scenes]}
    )


@app.post("/api/v1/scenes", response_model=SceneResponse)
async def create_scene(request: SceneCreateRequest):
    """创建场景"""
    from ..scene_engine import Scene, scene_engine, Trigger, TriggerType, Action, ActionType

    scene = Scene(
        name=request.name,
        description=request.description
    )

    # 解析触发器
    for t in request.triggers:
        trigger = Trigger(
            trigger_type=TriggerType(t.get("type", "manual")),
            config=t.get("config", {})
        )
        scene.triggers.append(trigger)

    # 解析动作
    for a in request.actions:
        action = Action(
            action_type=ActionType(a.get("type", "device_control")),
            config=a.get("config", {})
        )
        scene.actions.append(action)

    await scene_engine.register_scene(scene)
    return SceneResponse(data=scene.to_dict())


@app.post("/api/v1/scenes/{scene_id}/execute", response_model=SceneResponse)
async def execute_scene(scene_id: str, request: SceneExecuteRequest):
    """执行场景"""
    from ..scene_engine import scene_engine, TriggerType

    try:
        execution_id = await scene_engine.trigger_scene(
            scene_id,
            TriggerType.MANUAL,
            request.context
        )
        return SceneResponse(
            data={"execution_id": execution_id, "scene_id": scene_id}
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============ 租户 API ============

@app.post("/api/v1/tenants", response_model=TenantResponse)
async def create_tenant(request: TenantCreateRequest):
    """创建租户"""
    from ..tenancy import TenantManager, PlanType

    manager = TenantManager()
    plan = PlanType(request.plan)
    tenant = await manager.create_tenant(request.name, plan)
    return TenantResponse(data={"tenant_id": tenant.tenant_id})


@app.get("/api/v1/tenants/{tenant_id}", response_model=TenantResponse)
async def get_tenant(tenant_id: str):
    """获取租户"""
    from ..tenancy import tenant_manager
    tenant = await tenant_manager.get_tenant(tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="租户不存在")
    return TenantResponse(data=tenant.__dict__)


# ============ 启动函数 ============

def create_app() -> FastAPI:
    """创建应用"""
    return app


async def start_server(host: str = "0.0.0.0", port: int = 8000):
    """启动服务器"""
    config = uvicorn.Config(app, host=host, port=port, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
