"""
区域治理系统 - 非独裁式资源管理
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import asyncio
import logging

logger = logging.getLogger(__name__)


class GovernanceLevel(Enum):
    """治理级别"""
    ADMIN = "admin"        # 管理员
    OPERATOR = "operator"  # 操作员
    USER = "user"          # 用户
    GUEST = "guest"        # 访客


@dataclass
class ResourceQuota:
    """资源配额"""
    cpu_limit: float = 0.0
    memory_limit: float = 0.0
    storage_limit: float = 0.0
    device_limit: int = 0
    scene_limit: int = 0


@dataclass
class GovernancePolicy:
    """治理策略"""
    policy_id: str
    name: str
    description: str = ""
    rules: Dict[str, Any] = field(default_factory=dict)
    priority: int = 5
    enabled: bool = True


@dataclass
class AuditLog:
    """审计日志"""
    log_id: str
    user_id: str
    action: str
    resource: str
    result: str
    timestamp: datetime = field(default_factory=datetime.now)
    details: Dict[str, Any] = field(default_factory=dict)


class RegionalGovernance:
    """
    区域治理系统
    
    非独裁式资源管理，公平、透明、可审计
    """

    def __init__(self):
        self._policies: Dict[str, GovernancePolicy] = {}
        self._quotas: Dict[str, ResourceQuota] = {}
        self._audit_logs: List[AuditLog] = []
        self._log_counter = 0

    def set_quota(self, tenant_id: str, quota: ResourceQuota) -> None:
        """设置配额"""
        self._quotas[tenant_id] = quota
        logger.info(f"配额设置: {tenant_id}")

    def get_quota(self, tenant_id: str) -> Optional[ResourceQuota]:
        """获取配额"""
        return self._quotas.get(tenant_id)

    def check_quota(self, tenant_id: str, resource_type: str, amount: float) -> bool:
        """检查配额"""
        quota = self._quotas.get(tenant_id)
        if not quota:
            return True  # 无配额限制

        if resource_type == "cpu" and quota.cpu_limit > 0:
            return amount <= quota.cpu_limit
        elif resource_type == "memory" and quota.memory_limit > 0:
            return amount <= quota.memory_limit
        elif resource_type == "storage" and quota.storage_limit > 0:
            return amount <= quota.storage_limit
        elif resource_type == "device" and quota.device_limit > 0:
            return int(amount) <= quota.device_limit

        return True

    def add_policy(self, policy: GovernancePolicy) -> None:
        """添加治理策略"""
        self._policies[policy.policy_id] = policy
        logger.info(f"策略添加: {policy.name}")

    async def evaluate_policy(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """评估策略"""
        results = {}

        for policy_id, policy in self._policies.items():
            if not policy.enabled:
                continue

            # 评估规则
            passed = True
            for rule_name, rule_config in policy.rules.items():
                if not self._evaluate_rule(rule_name, rule_config, context):
                    passed = False
                    break

            results[policy_id] = {
                "policy_name": policy.name,
                "passed": passed,
                "priority": policy.priority
            }

        return results

    def _evaluate_rule(self, rule_name: str, rule_config: Dict[str, Any],
                      context: Dict[str, Any]) -> bool:
        """评估单个规则"""
        # 简化规则评估
        if rule_name == "time_restriction":
            # 时间限制
            allowed_hours = rule_config.get("hours", [])
            current_hour = datetime.now().hour
            return current_hour in allowed_hours

        elif rule_name == "resource_limit":
            # 资源限制
            max_value = rule_config.get("max", float('inf'))
            current = context.get("current_usage", 0)
            return current < max_value

        elif rule_name == "user_role":
            # 角色限制
            allowed_roles = rule_config.get("roles", [])
            user_role = context.get("user_role", "guest")
            return user_role in allowed_roles

        return True

    async def audit(self, user_id: str, action: str, resource: str,
                   result: str, details: Dict[str, Any] = None) -> None:
        """记录审计日志"""
        self._log_counter += 1
        log = AuditLog(
            log_id=f"log_{self._log_counter}",
            user_id=user_id,
            action=action,
            resource=resource,
            result=result,
            details=details or {}
        )
        self._audit_logs.append(log)

        # 保留最近 10000 条
        if len(self._audit_logs) > 10000:
            self._audit_logs = self._audit_logs[-10000:]

    def get_audit_logs(self, user_id: str = None, action: str = None,
                      limit: int = 100) -> List[Dict[str, Any]]:
        """获取审计日志"""
        logs = self._audit_logs

        if user_id:
            logs = [l for l in logs if l.user_id == user_id]
        if action:
            logs = [l for l in logs if l.action == action]

        return [
            {
                "log_id": l.log_id,
                "user_id": l.user_id,
                "action": l.action,
                "resource": l.resource,
                "result": l.result,
                "timestamp": l.timestamp.isoformat()
            }
            for l in logs[-limit:]
        ]

    def get_governance_status(self) -> Dict[str, Any]:
        """获取治理状态"""
        return {
            "policies": len(self._policies),
            "active_policies": sum(1 for p in self._policies.values() if p.enabled),
            "quotas": len(self._quotas),
            "audit_logs": len(self._audit_logs),
            "status": "healthy"
        }


class DemocraticDecision:
    """民主决策"""

    def __init__(self):
        self._votes: Dict[str, Dict[str, Any]] = {}
        self._vote_counter = 0

    async def create_vote(self, topic: str, options: List[str],
                         voters: List[str], threshold: float = 0.5) -> str:
        """创建投票"""
        self._vote_counter += 1
        vote_id = f"vote_{self._vote_counter}"

        self._votes[vote_id] = {
            "topic": topic,
            "options": {opt: 0 for opt in options},
            "voters": voters,
            "voted": [],
            "threshold": threshold,
            "status": "open"
        }

        logger.info(f"投票创建: {topic}")
        return vote_id

    async def cast_vote(self, vote_id: str, voter_id: str, option: str) -> bool:
        """投票"""
        vote = self._votes.get(vote_id)
        if not vote or vote["status"] != "open":
            return False

        if voter_id not in vote["voters"]:
            return False

        if voter_id in vote["voted"]:
            return False

        if option not in vote["options"]:
            return False

        vote["options"][option] += 1
        vote["voted"].append(voter_id)

        # 检查是否达到阈值
        total_votes = sum(vote["options"].values())
        total_voters = len(vote["voters"])

        if total_votes >= total_voters * vote["threshold"]:
            # 找出获胜选项
            winner = max(vote["options"].items(), key=lambda x: x[1])
            vote["winner"] = winner[0]
            vote["status"] = "closed"

        return True

    def get_vote_result(self, vote_id: str) -> Optional[Dict[str, Any]]:
        """获取投票结果"""
        vote = self._votes.get(vote_id)
        if not vote:
            return None

        return {
            "topic": vote["topic"],
            "status": vote["status"],
            "options": vote["options"],
            "winner": vote.get("winner"),
            "participation": len(vote["voted"]) / len(vote["voters"]) if vote["voters"] else 0
        }


# 全局治理系统
regional_governance = RegionalGovernance()
democratic_decision = DemocraticDecision()
