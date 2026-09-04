from enum import Enum
from typing import Any, Dict, List

from pydantic import BaseModel, Field


# =========================================================
# Agent Enums
# =========================================================

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


# =========================================================
# Gemini Decision
# =========================================================

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


# =========================================================
# Final API Response
# =========================================================

class AgentInvestigation(BaseModel):

    transaction_id: int

    transaction_code: str

    # -----------------------------------------------------
    # ML
    # -----------------------------------------------------

    ml_risk: float = Field(
        ge=0.0,
        le=1.0,
    )

    ml_risk_percentage: float = Field(
        ge=0.0,
        le=100.0,
    )

    # -----------------------------------------------------
    # Graph
    # -----------------------------------------------------

    graph_risk: float = Field(
        ge=0.0,
        le=1.0,
    )

    graph_risk_percentage: float = Field(
        ge=0.0,
        le=100.0,
    )

    graph_risk_level: RiskLevel

    graph_features: Dict[str, Any]

    # -----------------------------------------------------
    # AI decision
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # Evidence
    # -----------------------------------------------------

    evidence: Dict[str, Any]

    tools_used: List[str]