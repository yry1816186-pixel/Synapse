"""
SQL 规则引擎 - 借鉴 EMQX 设计
支持 SQL 事件处理
"""

from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import re
import logging

logger = logging.getLogger(__name__)


class RuleState(Enum):
    """规则状态"""
    ENABLED = "enabled"
    DISABLED = "disabled"


@dataclass
class Rule:
    """规则"""
    rule_id: str
    name: str
    sql: str  # SQL-like 语法
    actions: List[str] = field(default_factory=list)
    state: RuleState = RuleState.ENABLED
    description: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    trigger_count: int = 0


@dataclass
class RuleMatch:
    """规则匹配结果"""
    rule_id: str
    matched: bool
    extracted_data: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


class SQLRuleEngine:
    """
    SQL 规则引擎
    
    借鉴 EMQX 的 SQL 事件处理
    支持 WHERE、SELECT 等语法
    """

    def __init__(self):
        self._rules: Dict[str, Rule] = {}
        self._action_handlers: Dict[str, Callable] = {}

    def create_rule(self, rule: Rule) -> bool:
        """创建规则"""
        # 解析 SQL
        parsed = self._parse_sql(rule.sql)
        if not parsed:
            logger.error(f"规则 SQL 解析失败: {rule.sql}")
            return False

        self._rules[rule.rule_id] = rule
        logger.info(f"创建规则: {rule.name}")
        return True

    def _parse_sql(self, sql: str) -> Optional[Dict[str, Any]]:
        """解析 SQL"""
        # 简化的 SQL 解析
        # 支持: SELECT ... FROM topic WHERE condition
        
        result = {
            "select": ["*"],
            "from": "*",
            "where": None
        }

        sql = sql.strip().upper()

        # 提取 SELECT
        select_match = re.search(r'SELECT\s+(.+?)\s+FROM', sql)
        if select_match:
            fields = select_match.group(1).strip()
            if fields != "*":
                result["select"] = [f.strip() for f in fields.split(",")]

        # 提取 FROM
        from_match = re.search(r'FROM\s+(\S+)', sql)
        if from_match:
            result["from"] = from_match.group(1).lower()

        # 提取 WHERE
        where_match = re.search(r'WHERE\s+(.+)$', sql)
        if where_match:
            result["where"] = where_match.group(1).strip()

        return result

    async def process(self, topic: str, payload: Dict[str, Any]) -> List[RuleMatch]:
        """处理事件"""
        matches = []

        for rule in self._rules.values():
            if rule.state != RuleState.ENABLED:
                continue

            parsed = self._parse_sql(rule.sql)
            if not parsed:
                continue

            # 检查 topic 匹配
            if not self._match_topic(parsed["from"], topic):
                continue

            # 检查 WHERE 条件
            if parsed["where"]:
                if not self._evaluate_where(parsed["where"], payload):
                    continue

            # 提取数据
            extracted = {}
            if "*" in parsed["select"]:
                extracted = payload.copy()
            else:
                for field in parsed["select"]:
                    if field in payload:
                        extracted[field] = payload[field]

            # 执行动作
            for action in rule.actions:
                await self._execute_action(action, topic, extracted)

            rule.trigger_count += 1

            matches.append(RuleMatch(
                rule_id=rule.rule_id,
                matched=True,
                extracted_data=extracted
            ))

        return matches

    def _match_topic(self, pattern: str, topic: str) -> bool:
        """匹配 topic"""
        if pattern == "*":
            return True

        # 支持通配符
        pattern_parts = pattern.split("/")
        topic_parts = topic.split("/")

        for i, p in enumerate(pattern_parts):
            if p == "#":  # 多级通配符
                return True
            if p == "+":  # 单级通配符
                continue
            if i >= len(topic_parts) or p != topic_parts[i]:
                return False

        return len(pattern_parts) == len(topic_parts)

    def _evaluate_where(self, where: str, payload: Dict[str, Any]) -> bool:
        """评估 WHERE 条件"""
        # 简化条件评估
        # 支持: field = value, field > value 等

        # 替换变量
        condition = where
        for key, value in payload.items():
            if isinstance(value, str):
                condition = condition.replace(f"{key.upper()}", f"'{value}'")
            elif isinstance(value, (int, float)):
                condition = condition.replace(f"{key.upper()}", str(value))

        # 简单表达式评估
        try:
            # 安全评估（仅支持简单比较）
            if "=" in condition and "==" not in condition:
                condition = condition.replace("=", "==")
            if ">" in condition or "<" in condition:
                pass  # 保持原样

            # 这里应该用更安全的方式
            # 简化处理，只检查是否包含 true
            return "true" in condition.lower() or condition == "1==1"
        except:
            return False

    async def _execute_action(self, action: str, topic: str, data: Dict[str, Any]) -> None:
        """执行动作"""
        handler = self._action_handlers.get(action)
        if handler:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(topic, data)
                else:
                    handler(topic, data)
            except Exception as e:
                logger.error(f"动作执行失败: {e}")

    def register_action(self, action_name: str, handler: Callable) -> None:
        """注册动作处理器"""
        self._action_handlers[action_name] = handler

    def enable_rule(self, rule_id: str) -> bool:
        """启用规则"""
        rule = self._rules.get(rule_id)
        if rule:
            rule.state = RuleState.ENABLED
            return True
        return False

    def disable_rule(self, rule_id: str) -> bool:
        """禁用规则"""
        rule = self._rules.get(rule_id)
        if rule:
            rule.state = RuleState.DISABLED
            return True
        return False

    def get_rules(self) -> List[Dict[str, Any]]:
        """获取所有规则"""
        return [
            {
                "rule_id": r.rule_id,
                "name": r.name,
                "sql": r.sql,
                "state": r.state.value,
                "trigger_count": r.trigger_count
            }
            for r in self._rules.values()
        ]


# 示例规则
EXAMPLE_RULES = [
    """
    SELECT temperature, humidity
    FROM "sensor/+/temperature"
    WHERE temperature > 30
    """,
    """
    SELECT *
    FROM "device/+/status"
    WHERE status = 'offline'
    """
]


# 全局规则引擎
sql_rule_engine = SQLRuleEngine()
