import json

from sqlalchemy.orm import Session

from app.agent.client import generate_agent_response

from app.agent.tools import (
    get_transaction,
    get_graph_analysis,
    get_transaction_refunds,
    get_cluster_information,
)

from app.schemas.agent import AgentDecision


# =========================================================
# System Instruction
# =========================================================

SYSTEM_INSTRUCTION = """
You are LossGraph, an AI payment abuse investigation agent.

Your job is to investigate suspicious payment transactions.

You analyze evidence from:

1. Transaction information
2. Machine-learning risk score
3. Graph relationships
4. Refund behaviour
5. Coordinated abuse clusters

Important rules:

- Do not invent evidence.
- Only use information supplied in the investigation data.
- Shared devices, IP addresses, addresses and payment instruments
  are important indicators of coordinated abuse.
- A high ML score alone does not prove abuse.
- A high graph score indicates stronger relational evidence.
- Cluster membership increases the likelihood of coordinated abuse.
- Refund behaviour can provide additional evidence.
- Clearly distinguish evidence from conclusions.
- Be conservative when evidence is weak.
- Never claim evidence that is not present in the supplied data.

Return ONLY a JSON object with exactly these fields:

{
    "verdict": "ABUSE" | "NORMAL" | "REVIEW",
    "confidence": number between 0 and 1,
    "risk_level": "LOW" | "MEDIUM" | "HIGH" | "CRITICAL",
    "summary": "short explanation",
    "reasons": ["reason 1", "reason 2"],
    "recommended_action": "ALLOW" | "MONITOR" | "MANUAL_REVIEW" | "BLOCK"
}
"""


# =========================================================
# Investigation
# =========================================================

def investigate_transaction(
    db: Session,
    transaction_id: int,
    ml_risk: float,
):

    # -----------------------------------------------------
    # 1. Transaction
    # -----------------------------------------------------

    transaction = get_transaction(
        db,
        transaction_id,
    )

    if transaction is None:
        raise ValueError(
            "Transaction not found."
        )

    # -----------------------------------------------------
    # 2. Graph investigation
    # -----------------------------------------------------

    graph = get_graph_analysis(
        db,
        transaction_id,
    )

    # -----------------------------------------------------
    # 3. Refund investigation
    # -----------------------------------------------------

    refunds = get_transaction_refunds(
        db,
        transaction_id,
    )

    # -----------------------------------------------------
    # 4. Cluster investigation
    # -----------------------------------------------------

    cluster = get_cluster_information(
        db,
        transaction_id,
    )

    # -----------------------------------------------------
    # Evidence package
    # -----------------------------------------------------

    evidence = {
        "transaction": transaction,
        "ml_risk": ml_risk,
        "graph_analysis": graph,
        "refunds": refunds,
        "cluster": cluster,
    }

    # -----------------------------------------------------
    # Gemini prompt
    # -----------------------------------------------------

    prompt = f"""
Investigate this payment transaction.

Evidence:

{json.dumps(
    evidence,
    indent=2,
    default=str,
)}

Analyze the evidence and determine whether this
transaction appears to be:

- NORMAL
- ABUSE
- REVIEW

Consider:

- ML risk
- Graph risk
- Shared identifiers
- Refund behaviour
- Chargebacks
- Cluster membership

Do not invent any evidence.

Return ONLY valid JSON.
"""

    # -----------------------------------------------------
    # Gemini
    # -----------------------------------------------------

    response = generate_agent_response(
        system_instruction=SYSTEM_INSTRUCTION,
        prompt=prompt,
    )

    # -----------------------------------------------------
    # Clean response
    # -----------------------------------------------------

    cleaned = response.strip()

    if cleaned.startswith("```json"):
        cleaned = cleaned[
            len("```json"):
        ].strip()

    elif cleaned.startswith("```"):
        cleaned = cleaned[
            len("```"):
        ].strip()

    if cleaned.endswith("```"):
        cleaned = cleaned[
            :-len("```")
        ].strip()

    # -----------------------------------------------------
    # Validate Gemini response
    # -----------------------------------------------------

    try:
        decision = AgentDecision.model_validate_json(
            cleaned
        )

    except Exception as exc:

        raise ValueError(
            "AI returned an invalid investigation response."
        ) from exc

    # -----------------------------------------------------
    # Final agent result
    # -----------------------------------------------------

    graph_score = 0.0
    graph_level = "LOW"
    graph_features = {}

    if graph:

        graph_score = float(
            graph.get(
                "graph_score",
                0.0,
            )
        )

        graph_level = graph.get(
            "graph_risk_level",
            "LOW",
        )

        graph_features = graph.get(
            "features",
            {},
        )

    return {
        "transaction_id": transaction_id,

        "transaction_code": transaction[
            "transaction_code"
        ],

        # -------------------------------------------------
        # ML
        # -------------------------------------------------

        "ml_risk": float(
            ml_risk
        ),

        "ml_risk_percentage": round(
            float(ml_risk) * 100,
            2,
        ),

        # -------------------------------------------------
        # Graph
        # -------------------------------------------------

        "graph_risk": graph_score,

        "graph_risk_percentage": round(
            graph_score * 100,
            2,
        ),

        "graph_risk_level": graph_level,

        "graph_features": graph_features,

        # -------------------------------------------------
        # AI decision
        # -------------------------------------------------

        "verdict": decision.verdict.value,

        "confidence": float(
            decision.confidence
        ),

        "risk_level": decision.risk_level.value,

        "summary": decision.summary,

        "reasons": decision.reasons,

        "recommended_action": (
            decision.recommended_action.value
        ),

        # -------------------------------------------------
        # Evidence
        # -------------------------------------------------

        "evidence": evidence,

        "tools_used": [
            "get_transaction",
            "get_graph_analysis",
            "get_transaction_refunds",
            "get_cluster_information",
        ],
    }