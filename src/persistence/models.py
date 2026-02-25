"""
数据持久化层 - SQLAlchemy 模型
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, JSON, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine

Base = declarative_base()


class TenantModel(Base):
    """租户模型"""
    __tablename__ = "tenants"

    tenant_id = Column(String(32), primary_key=True)
    name = Column(String(128), nullable=False)
    plan = Column(String(32), default="free")
    status = Column(String(32), default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    settings = Column(JSON, default={})
    metadata = Column(JSON, default={})

    users = relationship("UserModel", back_populates="tenant")
    devices = relationship("DeviceModel", back_populates="tenant")
    scenes = relationship("SceneModel", back_populates="tenant")


class UserModel(Base):
    """用户模型"""
    __tablename__ = "users"

    user_id = Column(String(32), primary_key=True)
    tenant_id = Column(String(32), ForeignKey("tenants.tenant_id"))
    username = Column(String(64), nullable=False)
    email = Column(String(128))
    role = Column(String(32), default="user")
    password_hash = Column(String(256))
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    metadata = Column(JSON, default={})

    tenant = relationship("TenantModel", back_populates="users")


class DeviceModel(Base):
    """设备模型"""
    __tablename__ = "devices"

    device_id = Column(String(64), primary_key=True)
    tenant_id = Column(String(32), ForeignKey("tenants.tenant_id"))
    name = Column(String(128), nullable=False)
    device_type = Column(String(32), nullable=False)
    state = Column(String(32), default="offline")
    manufacturer = Column(String(128))
    model = Column(String(128))
    firmware_version = Column(String(32))
    config = Column(JSON, default={})
    capabilities = Column(JSON, default=[])
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_seen = Column(DateTime, nullable=True)
    metadata = Column(JSON, default={})

    tenant = relationship("TenantModel", back_populates="devices")


class SceneModel(Base):
    """场景模型"""
    __tablename__ = "scenes"

    scene_id = Column(String(64), primary_key=True)
    tenant_id = Column(String(32), ForeignKey("tenants.tenant_id"))
    name = Column(String(128), nullable=False)
    description = Column(Text)
    enabled = Column(Boolean, default=True)
    priority = Column(Integer, default=5)
    triggers = Column(JSON, default=[])
    actions = Column(JSON, default=[])
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_executed = Column(DateTime, nullable=True)
    execution_count = Column(Integer, default=0)
    metadata = Column(JSON, default={})

    tenant = relationship("TenantModel", back_populates="scenes")


class SceneExecutionModel(Base):
    """场景执行记录"""
    __tablename__ = "scene_executions"

    execution_id = Column(String(64), primary_key=True)
    scene_id = Column(String(64), ForeignKey("scenes.scene_id"))
    tenant_id = Column(String(32))
    status = Column(String(32))
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    duration_ms = Column(Integer)
    trigger_type = Column(String(32))
    context = Column(JSON, default={})
    result = Column(JSON, default={})
    error = Column(Text, nullable=True)


class DeviceDataModel(Base):
    """设备数据模型"""
    __tablename__ = "device_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    device_id = Column(String(64), nullable=False)
    tenant_id = Column(String(32))
    data_type = Column(String(32))
    value = Column(JSON)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    metadata = Column(JSON, default={})


class AuditLogModel(Base):
    """审计日志模型"""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id = Column(String(32))
    user_id = Column(String(32))
    event_type = Column(String(64))
    resource_type = Column(String(64))
    resource_id = Column(String(128))
    action = Column(String(64))
    result = Column(String(32))
    details = Column(JSON, default={})
    ip_address = Column(String(64))
    user_agent = Column(String(256))
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)


class HopeMemoryModel(Base):
    """Hope 记忆模型"""
    __tablename__ = "hope_memories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id = Column(String(32))
    memory_type = Column(String(32))
    key = Column(String(256), index=True)
    value = Column(JSON)
    importance = Column(Float, default=0.5)
    access_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    metadata = Column(JSON, default={})


class HopePatternModel(Base):
    """Hope 模式模型"""
    __tablename__ = "hope_patterns"

    pattern_id = Column(String(64), primary_key=True)
    tenant_id = Column(String(32))
    pattern_type = Column(String(64))
    conditions = Column(JSON)
    action = Column(JSON)
    confidence = Column(Float, default=0.0)
    occurrence_count = Column(Integer, default=0)
    last_occurrence = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)


def init_db(database_url: str = "sqlite:///synapse.db"):
    """初始化数据库"""
    engine = create_engine(database_url)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)


# 数据库会话工厂
SessionLocal = None


def get_session():
    """获取数据库会话"""
    global SessionLocal
    if SessionLocal is None:
        SessionLocal = init_db()
    return SessionLocal()
