from pydantic import BaseModel
from typing import List, Dict, Any


class AgentInvestigation(BaseModel):

    transaction_id: int

    verdict: str

    confidence: float

    risk_level: str

    summary: str

    reasons: List[str]

    recommended_action: str

    evidence: Dict[str, Any]

    tools_used: List[str]