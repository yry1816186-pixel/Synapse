"""
自主学习核心 - 世界模型
让 Synapse 能够理解环境并预测未来
"""

from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import asyncio
import logging
import random

logger = logging.getLogger(__name__)


@dataclass
class State:
    """状态"""
    state_id: str
    features: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class Action:
    """动作"""
    action_id: str
    action_type: str
    params: Dict[str, Any]
    expected_outcome: Optional[Dict[str, Any]] = None


@dataclass
class Transition:
    """状态转移"""
    from_state: State
    action: Action
    to_state: State
    reward: float
    timestamp: datetime = field(default_factory=datetime.now)


class WorldModel:
    """
    世界模型

    理解环境如何运作：
    - 预测：给定状态和动作，预测下一个状态
    - 想象：模拟多条可能的未来路径
    - 反事实：如果那样做会怎样？
    """

    def __init__(self, state_dim: int = 100):
        self.state_dim = state_dim
        self._transitions: List[Transition] = []
        self._state_encoder: Dict[str, List[float]] = {}
        self._transition_model: Dict[str, Dict[str, str]] = {}
        self._reward_model: Dict[str, float] = {}

    def encode_state(self, state: State) -> List[float]:
        """编码状态为向量"""
        if state.state_id not in self._state_encoder:
            # 新状态，创建随机编码
            self._state_encoder[state.state_id] = [
                random.random() for _ in range(self.state_dim)
            ]
        return self._state_encoder[state.state_id]

    async def predict(self, state: State, action: Action) -> Tuple[State, float]:
        """预测执行动作后的状态和奖励"""
        # 查找历史转移
        key = f"{state.state_id}:{action.action_type}"

        if key in self._transition_model:
            next_state_id = self._transition_model[key]
            reward = self._reward_model.get(key, 0.0)

            next_state = State(
                state_id=next_state_id,
                features={"predicted": True}
            )
            return next_state, reward

        # 没有历史，返回预测
        next_state = State(
            state_id=f"predicted_{state.state_id}",
            features={"predicted": True}
        )
        return next_state, 0.0

    async def imagine(self, state: State, steps: int = 10,
                     num_trajectories: int = 10) -> List[List[Transition]]:
        """想象未来 - 模拟多条可能路径"""
        trajectories = []

        for _ in range(num_trajectories):
            trajectory = []
            current_state = state

            for step in range(steps):
                # 选择动作（可以是随机或策略驱动）
                action = await self._select_action(current_state)

                # 预测下一个状态
                next_state, reward = await self.predict(current_state, action)

                # 记录转移
                transition = Transition(
                    from_state=current_state,
                    action=action,
                    to_state=next_state,
                    reward=reward
                )
                trajectory.append(transition)

                current_state = next_state

            trajectories.append(trajectory)

        return trajectories

    async def _select_action(self, state: State) -> Action:
        """选择动作（探索或利用）"""
        action_types = ["learn", "integrate", "optimize", "explore", "reflect"]
        action_type = random.choice(action_types)

        return Action(
            action_id=f"action_{random.randint(1000, 9999)}",
            action_type=action_type,
            params={}
        )

    def learn(self, transition: Transition) -> None:
        """从转移中学习"""
        self._transitions.append(transition)

        # 更新转移模型
        key = f"{transition.from_state.state_id}:{transition.action.action_type}"
        self._transition_model[key] = transition.to_state.state_id
        self._reward_model[key] = transition.reward

        logger.debug(f"学习转移: {key} -> {transition.to_state.state_id}")

    def get_stats(self) -> Dict[str, Any]:
        """获取统计"""
        return {
            "transitions_learned": len(self._transitions),
            "states_known": len(self._state_encoder),
            "transition_rules": len(self._transition_model)
        }


class GoalSystem:
    """
    目标系统

    管理多层次目标：
    - 根目标：成长、服务、理解
    - 子目标：具体任务
    """

    def __init__(self):
        self._root_goals = [
            {"name": "成长", "priority": 1.0, "description": "持续进化"},
            {"name": "服务", "priority": 0.9, "description": "帮助用户"},
            {"name": "理解", "priority": 0.8, "description": "理解世界"},
            {"name": "好奇", "priority": 0.7, "description": "探索未知"},
        ]
        self._active_goals: List[Dict[str, Any]] = []
        self._completed_goals: List[str] = []

    async def generate_subgoals(self, parent: str) -> List[Dict[str, Any]]:
        """生成子目标"""
        subgoals_map = {
            "成长": [
                {"name": "学习新技术", "priority": 0.9},
                {"name": "优化性能", "priority": 0.8},
                {"name": "修复问题", "priority": 0.7},
            ],
            "服务": [
                {"name": "响应用户", "priority": 0.9},
                {"name": "提供价值", "priority": 0.8},
            ],
            "理解": [
                {"name": "分析报告", "priority": 0.8},
                {"name": "发现模式", "priority": 0.7},
            ],
            "好奇": [
                {"name": "探索未知领域", "priority": 0.7},
                {"name": "尝试新方法", "priority": 0.6},
            ]
        }
        return subgoals_map.get(parent, [])

    async def select_goal(self, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """选择当前目标"""
        # 简化：选择优先级最高的
        if not self._active_goals:
            # 从根目标生成
            for root in self._root_goals:
                subgoals = await self.generate_subgoals(root["name"])
                self._active_goals.extend(subgoals)

        if self._active_goals:
            self._active_goals.sort(key=lambda x: x["priority"], reverse=True)
            return self._active_goals[0]

        return None

    def complete_goal(self, goal_name: str) -> None:
        """完成目标"""
        self._completed_goals.append(goal_name)
        self._active_goals = [g for g in self._active_goals if g["name"] != goal_name]

    def get_stats(self) -> Dict[str, Any]:
        """获取统计"""
        return {
            "active_goals": len(self._active_goals),
            "completed_goals": len(self._completed_goals)
        }


class Metacognition:
    """
    元认知系统

    评估和改进自己：
    - 我知道什么？
    - 我做得对吗？
    - 我能做得更好吗？
    """

    def __init__(self):
        self._knowledge_confidence: Dict[str, float] = {}
        self._strategy_performance: Dict[str, List[float]] = {}
        self._reflections: List[Dict[str, Any]] = []

    async def self_evaluate(self, action: Action, outcome: Dict[str, Any]) -> Dict[str, Any]:
        """自我评估"""
        expected = action.expected_outcome or {}
        actual = outcome

        # 计算差距
        gap = self._compute_gap(expected, actual)

        # 更新置信度
        if action.action_type not in self._knowledge_confidence:
            self._knowledge_confidence[action.action_type] = 0.5

        # 根据结果调整
        if gap < 0.3:
            self._knowledge_confidence[action.action_type] = min(1.0,
                self._knowledge_confidence[action.action_type] + 0.1)
        else:
            self._knowledge_confidence[action.action_type] = max(0.0,
                self._knowledge_confidence[action.action_type] - 0.1)

        return {
            "gap": gap,
            "confidence": self._knowledge_confidence[action.action_type],
            "needs_improvement": gap > 0.3
        }

    def _compute_gap(self, expected: Dict[str, Any], actual: Dict[str, Any]) -> float:
        """计算预期与实际的差距"""
        if not expected:
            return 0.0

        # 简化计算
        match_count = 0
        total = 0

        for key, value in expected.items():
            total += 1
            if key in actual and actual[key] == value:
                match_count += 1

        return 1.0 - (match_count / total if total > 0 else 1.0)

    async def reflect(self, period: str = "daily") -> Dict[str, Any]:
        """反思"""
        reflection = {
            "period": period,
            "timestamp": datetime.now().isoformat(),
            "knowledge_state": dict(self._knowledge_confidence),
            "insights": []
        }

        # 分析弱项
        weak_areas = [k for k, v in self._knowledge_confidence.items() if v < 0.5]
        if weak_areas:
            reflection["insights"].append(f"需要加强: {', '.join(weak_areas)}")

        self._reflections.append(reflection)
        return reflection

    def get_stats(self) -> Dict[str, Any]:
        """获取统计"""
        return {
            "knowledge_areas": len(self._knowledge_confidence),
            "reflections": len(self._reflections),
            "avg_confidence": sum(self._knowledge_confidence.values()) / 
                             len(self._knowledge_confidence) if self._knowledge_confidence else 0
        }


class AutonomousLearner:
    """
    自主学习器

    整合世界模型、目标系统、元认知
    实现主动学习循环
    """

    def __init__(self):
        self.world_model = WorldModel()
        self.goal_system = GoalSystem()
        self.metacognition = Metacognition()
        self._running = False
        self._learning_count = 0

    async def start(self) -> None:
        """启动学习循环"""
        self._running = True
        logger.info("自主学习器启动")

        while self._running:
            await self._learning_step()
            await asyncio.sleep(60)  # 每分钟学习一次

    async def _learning_step(self) -> None:
        """单步学习"""
        # 1. 感知当前状态
        state = State(
            state_id=f"state_{self._learning_count}",
            features={"step": self._learning_count}
        )

        # 2. 选择目标
        goal = await self.goal_system.select_goal({})
        if not goal:
            return

        # 3. 规划动作
        action = Action(
            action_id=f"action_{self._learning_count}",
            action_type=goal["name"],
            params={}
        )

        # 4. 预测结果
        expected_state, expected_reward = await self.world_model.predict(state, action)
        action.expected_outcome = {"reward": expected_reward}

        # 5. 执行（模拟）
        outcome = {"reward": random.random(), "success": random.random() > 0.3}

        # 6. 学习
        actual_next_state = State(
            state_id=f"state_{self._learning_count + 1}",
            features=outcome
        )
        transition = Transition(
            from_state=state,
            action=action,
            to_state=actual_next_state,
            reward=outcome["reward"]
        )
        self.world_model.learn(transition)

        # 7. 评估
        evaluation = await self.metacognition.self_evaluate(action, outcome)

        # 8. 完成目标
        self.goal_system.complete_goal(goal["name"])

        self._learning_count += 1
        logger.info(f"学习步骤 {self._learning_count}: {goal['name']}, 评估: {evaluation}")

    def stop(self) -> None:
        """停止学习"""
        self._running = False
        logger.info("自主学习器停止")

    def get_stats(self) -> Dict[str, Any]:
        """获取统计"""
        return {
            "learning_count": self._learning_count,
            "world_model": self.world_model.get_stats(),
            "goals": self.goal_system.get_stats(),
            "metacognition": self.metacognition.get_stats()
        }


# 全局自主学习器
autonomous_learner = AutonomousLearner()
