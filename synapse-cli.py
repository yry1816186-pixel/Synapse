#!/usr/bin/env python3
"""
Synapse CLI - 命令行工具
"""

import asyncio
import argparse
import logging
import sys
from typing import Optional

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def cmd_start(args):
    """启动 Synapse 服务"""
    from synapse.src.main import app

    async def run():
        await app.initialize()
        await app.start()

    asyncio.run(run())


def cmd_devices(args):
    """设备管理"""
    from synapse.src.device_abstraction import device_registry

    if args.action == "list":
        devices = device_registry.list_all()
        print(f"\n设备列表 ({len(devices)} 个):")
        for device in devices:
            print(f"  - [{device.device_id}] {device.name} ({device.device_type.value}) - {device.state.value}")

    elif args.action == "add":
        print(f"添加设备: {args.name} (类型: {args.type})")

    elif args.action == "remove":
        print(f"移除设备: {args.device_id}")


def cmd_scenes(args):
    """场景管理"""
    from synapse.src.scene_engine import scene_engine

    if args.action == "list":
        scenes = scene_engine.list_scenes()
        print(f"\n场景列表 ({len(scenes)} 个):")
        for scene in scenes:
            status = "✓" if scene.enabled else "✗"
            print(f"  {status} [{scene.scene_id}] {scene.name}")

    elif args.action == "execute":
        print(f"执行场景: {args.scene_id}")
        asyncio.run(scene_engine.trigger_scene(args.scene_id))


def cmd_api(args):
    """启动 API 服务"""
    import uvicorn
    from synapse.src.api import app

    uvicorn.run(
        app,
        host=args.host,
        port=args.port,
        log_level="info" if args.debug else "warning"
    )


def cmd_status(args):
    """显示系统状态"""
    from synapse.src.device_abstraction import device_registry
    from synapse.src.scene_engine import scene_engine

    devices = device_registry.list_all()
    scenes = scene_engine.list_scenes()

    print("\n=== Synapse 状态 ===")
    print(f"设备: {len(devices)} 个")
    print(f"场景: {len(scenes)} 个 (启用: {sum(1 for s in scenes if s.enabled)})")

    device_states = {}
    for d in devices:
        state = d.state.value
        device_states[state] = device_states.get(state, 0) + 1

    if device_states:
        print("\n设备状态分布:")
        for state, count in device_states.items():
            print(f"  {state}: {count}")


def main():
    parser = argparse.ArgumentParser(
        description="Synapse - 企业级开源物联网平台",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # start 命令
    parser_start = subparsers.add_parser("start", help="启动 Synapse 服务")
    parser_start.set_defaults(func=cmd_start)

    # devices 命令
    parser_devices = subparsers.add_parser("devices", help="设备管理")
    parser_devices.add_argument("action", choices=["list", "add", "remove"], help="操作")
    parser_devices.add_argument("--name", help="设备名称")
    parser_devices.add_argument("--type", help="设备类型")
    parser_devices.add_argument("--device-id", help="设备ID")
    parser_devices.set_defaults(func=cmd_devices)

    # scenes 命令
    parser_scenes = subparsers.add_parser("scenes", help="场景管理")
    parser_scenes.add_argument("action", choices=["list", "execute", "create", "delete"], help="操作")
    parser_scenes.add_argument("--scene-id", help="场景ID")
    parser_scenes.set_defaults(func=cmd_scenes)

    # api 命令
    parser_api = subparsers.add_parser("api", help="启动 API 服务")
    parser_api.add_argument("--host", default="0.0.0.0", help="绑定地址")
    parser_api.add_argument("--port", type=int, default=8000, help="端口")
    parser_api.add_argument("--debug", action="store_true", help="调试模式")
    parser_api.set_defaults(func=cmd_api)

    # status 命令
    parser_status = subparsers.add_parser("status", help="显示系统状态")
    parser_status.set_defaults(func=cmd_status)

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
