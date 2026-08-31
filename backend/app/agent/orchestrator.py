import json

from sqlalchemy.orm import Session

from app.agent.client import generate_agent_response
from app.agent.tools import (
    get_transaction,
    get_graph_analysis,
    get_transaction_refunds,
    get_cluster_information,
)
from app.schemas.agent import (
    AgentDecision,
    AgentInvestigation,
    Verdict,
    RiskLevel,
    RecommendedAction,
)


SYSTEM_INSTRUCTION = """
You are LossGraph, an AI payment-abuse investigation agent.

Your job is to analyze evidence about a payment transaction
and produce a conservative risk assessment.

You may use ONLY the evidence supplied to you.

You must NOT:
- invent evidence
- invent transaction relationships
- assume fraud from transaction amount alone
- treat a chargeback as automatic proof of fraud
- change numerical values supplied in the evidence
- claim that evidence exists when it does not

Important interpretation rules:

1. ML risk is a predictive signal, not proof of abuse.

2. Graph risk represents relational evidence.
   Shared devices, IP addresses, physical addresses and
   payment instruments can indicate coordinated behaviour.

3. Cluster membership is additional evidence of coordinated abuse.

4. Refund behaviour can provide supporting evidence.

5. A chargeback indicates a disputed transaction but does
   NOT by itself prove intentional fraud.

6. Strong conclusions require multiple supporting signals.

7. When evidence is ambiguous or conflicting, prefer REVIEW.

8. Confidence must reflect the strength and consistency
   of the available evidence.

Decision meanings:

NORMAL:
Evidence does not indicate meaningful abuse risk.

REVIEW:
Evidence is suspicious, incomplete, or conflicting and
requires human investigation.

ABUSE:
Evidence strongly indicates payment abuse.

Risk levels:

LOW
MEDIUM
HIGH
CRITICAL

Recommended actions:

ALLOW
MONITOR
MANUAL_REVIEW
BLOCK

Return ONLY the structured JSON response matching the
provided schema.
"""


TOOLS_USED = [
    "get_transaction",
    "get_graph_analysis",
    "get_transaction_refunds",
    "get_cluster_information",
]


def _build_evidence(
    db: Session,
    transaction_id: int,
    ml_risk: float,
):
    """
    Collect all evidence required by the agent.
    """

    transaction = get_transaction(
        db,
        transaction_id,
    )

    if transaction is None:
        raise ValueError(
            "Transaction not found."
        )

    graph = get_graph_analysis(
        db,
        transaction_id,
    )

    refunds = get_transaction_refunds(
        db,
        transaction_id,
    )

    cluster = get_cluster_information(
        db,
        transaction_id,
    )

    return {
        "transaction": transaction,
        "ml_risk": float(ml_risk),
        "graph_analysis": graph,
        "refunds": refunds,
        "cluster": cluster,
    }


def _fallback_decision(
    evidence: dict,
) -> AgentDecision:
    """
    Conservative fallback when Gemini is unavailable
    or returns invalid output.
    """

    ml_risk = float(
        evidence.get("ml_risk", 0.0)
    )

    graph = evidence.get(
        "graph_analysis"
    ) or {}

    graph_score = float(
        graph.get("graph_score", 0.0)
    )

    chargeback = bool(
        evidence["transaction"].get(
            "chargeback",
            False,
        )
    )

    cluster = evidence.get(
        "cluster"
    ) or {}

    in_cluster = bool(
        cluster.get(
            "in_cluster",
            False,
        )
    )

    # Strong deterministic evidence
    if (
        ml_risk >= 0.90
        and graph_score >= 0.80
        and (
            chargeback
            or in_cluster
        )
    ):
        return AgentDecision(
            verdict=Verdict.ABUSE,
            confidence=0.90,
            risk_level=RiskLevel.CRITICAL,
            summary=(
                "Strong ML and graph-based risk signals "
                "require immediate intervention."
            ),
            reasons=[
                f"ML risk score is {ml_risk:.4f}.",
                f"Graph risk score is {graph_score:.4f}.",
                (
                    "Transaction has chargeback evidence."
                    if chargeback
                    else "Transaction belongs to an abuse cluster."
                ),
            ],
            recommended_action=(
                RecommendedAction.BLOCK
            ),
        )

    # Suspicious evidence
    if (
        ml_risk >= 0.70
        or graph_score >= 0.70
        or chargeback
        or in_cluster
    ):
        return AgentDecision(
            verdict=Verdict.REVIEW,
            confidence=0.70,
            risk_level=RiskLevel.MEDIUM,
            summary=(
                "Suspicious risk signals were detected, "
                "but the evidence is insufficient for a "
                "confident automated abuse decision."
            ),
            reasons=[
                f"ML risk score: {ml_risk:.4f}.",
                f"Graph risk score: {graph_score:.4f}.",
            ],
            recommended_action=(
                RecommendedAction.MANUAL_REVIEW
            ),
        )

    return AgentDecision(
        verdict=Verdict.NORMAL,
        confidence=0.75,
        risk_level=RiskLevel.LOW,
        summary=(
            "No strong abuse indicators were detected "
            "in the available evidence."
        ),
        reasons=[
            f"ML risk score: {ml_risk:.4f}.",
            f"Graph risk score: {graph_score:.4f}.",
        ],
        recommended_action=(
            RecommendedAction.ALLOW
        ),
    )


def investigate_transaction(
    db: Session,
    transaction_id: int,
    ml_risk: float,
):
    """
    Run the complete LossGraph AI investigation pipeline.
    """

    # --------------------------------------------------
    # 1. Collect evidence
    # --------------------------------------------------

    evidence = _build_evidence(
        db=db,
        transaction_id=transaction_id,
        ml_risk=ml_risk,
    )

    # --------------------------------------------------
    # 2. Build investigation prompt
    # --------------------------------------------------

    prompt = f"""
Investigate this payment transaction.

The following evidence was collected from LossGraph's
database, ML system and graph analysis system.

IMPORTANT:
Treat these values as authoritative.
Do not modify or invent them.

EVIDENCE:

{json.dumps(
    evidence,
    indent=2,
    default=str,
)}

Based only on this evidence:

1. Determine the verdict.
2. Assign a confidence between 0 and 1.
3. Assign an appropriate risk level.
4. Give a short evidence-based summary.
5. List the strongest supporting reasons.
6. Recommend an action.

If evidence conflicts or is insufficient,
choose REVIEW rather than making an aggressive conclusion.

Return ONLY the structured JSON response.
"""

    # --------------------------------------------------
    # 3. Ask Gemini
    # --------------------------------------------------

    try:

        response = generate_agent_response(
            system_instruction=SYSTEM_INSTRUCTION,
            prompt=prompt,
            response_schema=AgentDecision,
        )

        # --------------------------------------------------
        # 4. Validate Gemini output
        # --------------------------------------------------

        decision = AgentDecision.model_validate_json(
            response
        )

        ai_error = None

    except Exception as exc:

        # --------------------------------------------------
        # 5. Safe fallback
        # --------------------------------------------------

        decision = _fallback_decision(
            evidence
        )

        ai_error = str(exc)

    # --------------------------------------------------
    # 6. Build final investigation response
    # --------------------------------------------------

    result = AgentInvestigation(
        transaction_id=transaction_id,

        verdict=decision.verdict,

        confidence=decision.confidence,

        risk_level=decision.risk_level,

        summary=decision.summary,

        reasons=decision.reasons,

        recommended_action=(
            decision.recommended_action
        ),

        evidence=evidence,

        tools_used=TOOLS_USED,
    )

    output = result.model_dump(
        mode="json"
    )

    output["ai_status"] = (
        "success"
        if ai_error is None
        else "fallback"
    )

    if ai_error is not None:
        output["ai_error"] = (
            "AI investigation unavailable; "
            "deterministic fallback used."
        )

    return output