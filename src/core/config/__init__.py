"""
配置管理系统 - 修复版（无外部依赖）
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from pathlib import Path
import os
import json
import logging
import asyncio

logger = logging.getLogger(__name__)


class DatabaseConfig:
    """数据库配置"""
    def __init__(self):
        self.host = os.getenv("DB_HOST", "localhost")
        self.port = int(os.getenv("DB_PORT", "5432"))
        self.database = os.getenv("DB_NAME", "synapse")
        self.username = os.getenv("DB_USER", "synapse")
        self.password = os.getenv("DB_PASSWORD", "")
        self.pool_size = int(os.getenv("DB_POOL_SIZE", "10"))


class RedisConfig:
    """Redis 配置"""
    def __init__(self):
        self.host = os.getenv("REDIS_HOST", "localhost")
        self.port = int(os.getenv("REDIS_PORT", "6379"))
        self.db = int(os.getenv("REDIS_DB", "0"))
        self.password = os.getenv("REDIS_PASSWORD")


class MQTTConfig:
    """MQTT 配置"""
    def __init__(self):
        self.host = os.getenv("MQTT_HOST", "localhost")
        self.port = int(os.getenv("MQTT_PORT", "1883"))
        self.username = os.getenv("MQTT_USER")
        self.password = os.getenv("MQTT_PASSWORD")
        self.client_id = os.getenv("MQTT_CLIENT_ID", "synapse")


class APIConfig:
    """API 配置"""
    def __init__(self):
        self.host = os.getenv("API_HOST", "0.0.0.0")
        self.port = int(os.getenv("API_PORT", "8000"))
        self.debug = os.getenv("API_DEBUG", "false").lower() == "true"
        self.cors_origins = os.getenv("API_CORS", "*").split(",")


class Settings:
    """应用配置"""

    def __init__(self):
        # 应用信息
        self.app_name = os.getenv("APP_NAME", "Synapse")
        self.app_version = os.getenv("APP_VERSION", "3.0.0")
        self.debug = os.getenv("DEBUG", "false").lower() == "true"

        # 子配置
        self.database = DatabaseConfig()
        self.redis = RedisConfig()
        self.mqtt = MQTTConfig()
        self.api = APIConfig()


class ConfigManager:
    """配置管理器"""

    def __init__(self, config_dir: str = "./config"):
        self.config_dir = Path(config_dir)
        self._config: Dict[str, Any] = {}
        self._settings: Optional[Settings] = None
        self._observers: List[callable] = []

    def load(self, environment: str = None) -> Settings:
        """加载配置"""
        env = environment or os.getenv("SYNAPSE_ENV", "development")

        # 创建配置对象
        self._settings = Settings()

        # 加载配置文件
        config_file = self.config_dir / f"{env}.yaml"
        if config_file.exists():
            try:
                import yaml
                with open(config_file, "r", encoding="utf-8") as f:
                    file_config = yaml.safe_load(f)
                    if file_config:
                        self._merge_config(file_config)
            except ImportError:
                logger.warning("PyYAML 未安装，跳过 YAML 配置")
            except Exception as e:
                logger.warning(f"加载配置文件失败: {e}")

        # 加载本地覆盖配置
        local_config = self.config_dir / "local.yaml"
        if local_config.exists():
            try:
                import yaml
                with open(local_config, "r", encoding="utf-8") as f:
                    local_data = yaml.safe_load(f)
                    if local_data:
                        self._merge_config(local_data)
            except Exception:
                pass

        logger.info(f"配置加载完成: {env}")
        return self._settings

    def _merge_config(self, override: Dict[str, Any]) -> None:
        """合并配置"""
        def deep_merge(base: dict, update: dict) -> dict:
            for key, value in update.items():
                if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                    base[key] = deep_merge(base[key], value)
                else:
                    base[key] = value
            return base

        self._config = deep_merge(self._config, override)

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        keys = key.split(".")
        value = self._config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key: str, value: Any) -> None:
        """设置配置值"""
        keys = key.split(".")
        config = self._config

        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        config[keys[-1]] = value
        self._notify_observers(key, value)

    def observe(self, callback: callable) -> None:
        """添加配置变更观察者"""
        self._observers.append(callback)

    def _notify_observers(self, key: str, value: Any) -> None:
        """通知观察者"""
        for callback in self._observers:
            try:
                callback(key, value)
            except Exception as e:
                logger.error(f"配置观察者回调错误: {e}")

    @property
    def settings(self) -> Settings:
        """获取配置对象"""
        return self._settings


# 全局配置管理器
config_manager = ConfigManager()
