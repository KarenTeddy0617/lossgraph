import json

from sqlalchemy.orm import Session

from app.agent.client import generate_agent_response

from app.agent.tools import (
    get_transaction,
    get_graph_analysis,
    get_transaction_refunds,
    get_cluster_information,
)


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

Return a JSON object with exactly these fields:

{
    "verdict": "ABUSE" | "NORMAL" | "REVIEW",
    "confidence": number between 0 and 1,
    "risk_level": "LOW" | "MEDIUM" | "HIGH" | "CRITICAL",
    "summary": "short explanation",
    "reasons": ["reason 1", "reason 2"],
    "recommended_action": "ALLOW" | "MONITOR" | "MANUAL_REVIEW" | "BLOCK",
}

Be conservative when evidence is weak.
"""


def investigate_transaction(
    db: Session,
    transaction_id: int,
    ml_risk: float,
):

    # --------------------------------------------------
    # 1. Transaction
    # --------------------------------------------------

    transaction = get_transaction(
        db,
        transaction_id,
    )

    if transaction is None:
        raise ValueError(
            "Transaction not found."
        )

    # --------------------------------------------------
    # 2. Graph investigation
    # --------------------------------------------------

    graph = get_graph_analysis(
        db,
        transaction_id,
    )

    # --------------------------------------------------
    # 3. Refund investigation
    # --------------------------------------------------

    refunds = get_transaction_refunds(
        db,
        transaction_id,
    )

    # --------------------------------------------------
    # 4. Cluster investigation
    # --------------------------------------------------

    cluster = get_cluster_information(
        db,
        transaction_id,
    )

    # --------------------------------------------------
    # Evidence package
    # --------------------------------------------------

    evidence = {
        "transaction": transaction,
        "ml_risk": ml_risk,
        "graph_analysis": graph,
        "refunds": refunds,
        "cluster": cluster,
    }

    prompt = f"""
Investigate this payment transaction.

Evidence:

{json.dumps(
    evidence,
    indent=2,
    default=str
)}

Analyze the evidence and determine whether this
transaction appears to be:

- NORMAL
- ABUSE
- REVIEW

Consider both individual transaction risk and
coordinated behaviour visible through the graph.

Return ONLY valid JSON.
"""

    response = generate_agent_response(
        system_instruction=SYSTEM_INSTRUCTION,
        prompt=prompt,
    )

    # --------------------------------------------------
    # Parse Gemini response
    # --------------------------------------------------

    cleaned = response.strip()

    if cleaned.startswith("```"):
        cleaned = cleaned.replace(
            "```json",
            ""
        ).replace(
            "```",
            ""
        ).strip()

    result = json.loads(cleaned)

    # --------------------------------------------------
    # Final response
    # --------------------------------------------------

    return {
        "transaction_id": transaction_id,

        "verdict": result["verdict"],

        "confidence": float(
            result["confidence"]
        ),

        "risk_level": result["risk_level"],

        "summary": result["summary"],

        "reasons": result["reasons"],

        "recommended_action": result[
            "recommended_action"
        ],

        "evidence": evidence,

        "tools_used": [
            "get_transaction",
            "get_graph_analysis",
            "get_transaction_refunds",
            "get_cluster_information",
        ],
    }