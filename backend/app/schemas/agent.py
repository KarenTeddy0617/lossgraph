from enum import Enum
from typing import Any, Dict, List

from pydantic import BaseModel, Field


class Verdict(str, Enum):
    NORMAL = "NORMAL"
    REVIEW = "REVIEW"
    ABUSE = "ABUSE"


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class RecommendedAction(str, Enum):
    ALLOW = "ALLOW"
    MONITOR = "MONITOR"
    MANUAL_REVIEW = "MANUAL_REVIEW"
    BLOCK = "BLOCK"


class AgentDecision(BaseModel):
    verdict: Verdict

    confidence: float = Field(
        ge=0.0,
        le=1.0,
    )

    risk_level: RiskLevel

    summary: str = Field(
        min_length=1,
        max_length=1000,
    )

    reasons: List[str] = Field(
        min_length=1,
        max_length=10,
    )

    recommended_action: RecommendedAction


class AgentInvestigation(BaseModel):
    transaction_id: int

    verdict: Verdict

    confidence: float = Field(
        ge=0.0,
        le=1.0,
    )

    risk_level: RiskLevel

    summary: str

    reasons: List[str]

    recommended_action: RecommendedAction

    evidence: Dict[str, Any]

    tools_used: List[str]