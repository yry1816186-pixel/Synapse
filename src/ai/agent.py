"""
AI Agent - 智能代理
"""

from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import asyncio
import logging

from . import LLMManager, Message

logger = logging.getLogger(__name__)


class AgentRole(Enum):
    """代理角色"""
    ASSISTANT = "assistant"
    DEVICE_MANAGER = "device_manager"
    SCENE_ORCHESTRATOR = "scene_orchestrator"
    ANALYST = "analyst"
    SECURITY = "security"


@dataclass
class AgentConfig:
    """代理配置"""
    name: str
    role: AgentRole
    system_prompt: str = ""
    llm_client: str = None
    tools: List[str] = field(default_factory=list)
    max_history: int = 20


@dataclass
class AgentState:
    """代理状态"""
    agent_id: str
    conversation_history: List[Message] = field(default_factory=list)
    last_activity: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


class AIAgent:
    """AI 代理"""

    def __init__(self, config: AgentConfig):
        self.config = config
        self._state = AgentState(agent_id=config.name)
        self._tools: Dict[str, Callable] = {}

    def register_tool(self, name: str, func: Callable, description: str = "") -> None:
        """注册工具"""
        self._tools[name] = func
        logger.debug(f"代理 {self.config.name} 注册工具: {name}")

    async def chat(self, user_input: str, context: Dict[str, Any] = None) -> str:
        """对话"""
        # 构建消息
        messages = []

        # 系统提示
        if self.config.system_prompt:
            system_content = self.config.system_prompt
            if context:
                system_content += f"\n\n当前上下文: {json.dumps(context, ensure_ascii=False)}"
            messages.append(Message(role="system", content=system_content))

        # 历史记录
        messages.extend(self._state.conversation_history[-self.config.max_history:])

        # 用户输入
        messages.append(Message(role="user", content=user_input))

        # 调用 LLM
        response = await llm_manager.chat(
            messages,
            client_name=self.config.llm_client
        )

        # 更新历史
        self._state.conversation_history.append(Message(role="user", content=user_input))
        self._state.conversation_history.append(Message(role="assistant", content=response.content))
        self._state.last_activity = datetime.now()

        return response.content

    async def execute_tool(self, tool_name: str, **kwargs) -> Any:
        """执行工具"""
        tool = self._tools.get(tool_name)
        if not tool:
            return {"error": f"工具不存在: {tool_name}"}

        try:
            if asyncio.iscoroutinefunction(tool):
                return await tool(**kwargs)
            else:
                return tool(**kwargs)
        except Exception as e:
            return {"error": str(e)}

    def clear_history(self) -> None:
        """清空历史"""
        self._state.conversation_history.clear()


class AgentManager:
    """代理管理器"""

    def __init__(self):
        self._agents: Dict[str, AIAgent] = {}
        self._templates: Dict[AgentRole, str] = {
            AgentRole.ASSISTANT: "你是一个智能助手，帮助用户管理物联网设备。",
            AgentRole.DEVICE_MANAGER: "你是设备管理专家，帮助用户配置和控制设备。",
            AgentRole.SCENE_ORCHESTRATOR: "你是场景编排专家，帮助用户创建智能场景。",
            AgentRole.ANALYST: "你是数据分析师，帮助用户分析设备数据和使用情况。",
            AgentRole.SECURITY: "你是安全专家，监控和保护系统安全。"
        }

    def create_agent(self, config: AgentConfig) -> AIAgent:
        """创建代理"""
        if not config.system_prompt and config.role in self._templates:
            config.system_prompt = self._templates[config.role]

        agent = AIAgent(config)
        self._agents[config.name] = agent
        logger.info(f"AI 代理已创建: {config.name} [{config.role.value}]")
        return agent

    def get_agent(self, name: str) -> Optional[AIAgent]:
        """获取代理"""
        return self._agents.get(name)

    def list_agents(self) -> List[str]:
        """列出代理"""
        return list(self._agents.keys())


# 全局管理器
agent_manager = AgentManager()
