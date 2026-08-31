from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.transaction import Transaction
from app.api.v1.auth import get_current_user

from app.ml.predict import predict_transaction
from app.graph.features import calculate_graph_features
from app.graph.clustering import (
    calculate_graph_score_from_features,
    get_graph_risk_level,
)
from app.agent.orchestrator import investigate_transaction

router = APIRouter(
    prefix="/agent",
    tags=["Risk Analysis Agent"],
)


@router.get("/analyze/{transaction_id}")
def analyze_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Analyze one transaction using ML + graph signals
    and return an explainable risk assessment.
    """

    # -----------------------------------------------------
    # Find transaction
    # -----------------------------------------------------

    transaction = (
        db.query(Transaction)
        .filter(Transaction.id == transaction_id)
        .first()
    )

    if transaction is None:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found",
        )

    # -----------------------------------------------------
    # ML risk
    # -----------------------------------------------------

    ml_risk = predict_transaction(
        db,
        transaction,
    )

    # -----------------------------------------------------
    # Graph features
    # -----------------------------------------------------

    graph_features = calculate_graph_features(
        db,
        transaction,
    )

    graph_risk = calculate_graph_score_from_features(
        graph_features
    )

    graph_level = get_graph_risk_level(
        graph_risk
    )
    agent_result = investigate_transaction(
    db=db,
    transaction_id=transaction.id,
    ml_risk=ml_risk,
)

    # -----------------------------------------------------
    # Final prediction
    # -----------------------------------------------------

    if ml_risk >= 0.70:
        prediction = "ABUSE"
    else:
        prediction = "NORMAL"

    # -----------------------------------------------------
    # Generate explanations
    # -----------------------------------------------------

    reasons = []

    if graph_features["device_customer_count"] > 1:
        reasons.append(
            "Device is associated with multiple customers."
        )

    if graph_features["ip_customer_count"] > 1:
        reasons.append(
            "IP address is associated with multiple customers."
        )

    if graph_features["address_customer_count"] > 1:
        reasons.append(
            "Address is associated with multiple customers."
        )

    if graph_features["payment_customer_count"] > 1:
        reasons.append(
            "Payment instrument is shared across multiple customers."
        )

    if graph_features["shared_device_count"] > 0:
        reasons.append(
            f"Device is shared with "
            f"{graph_features['shared_device_count']} other transactions."
        )

    if graph_features["shared_ip_count"] > 0:
        reasons.append(
            f"IP address is shared with "
            f"{graph_features['shared_ip_count']} other transactions."
        )

    if graph_features["shared_address_count"] > 0:
        reasons.append(
            f"Address is shared with "
            f"{graph_features['shared_address_count']} other transactions."
        )

    if graph_features["shared_payment_count"] > 0:
        reasons.append(
            f"Payment instrument is shared with "
            f"{graph_features['shared_payment_count']} other transactions."
        )

    if not reasons:
        reasons.append(
            "No significant graph-based abuse signals were detected."
        )

    # -----------------------------------------------------
    # Return analysis
    # -----------------------------------------------------

    return {
        "transaction_id": transaction.id,
        "transaction_code": transaction.transaction_code,

        "ml_risk": ml_risk,
        "ml_risk_percentage": round(
            ml_risk * 100,
            2,
        ),

        "graph_risk": graph_risk,
        "graph_risk_percentage": round(
            graph_risk * 100,
            2,
        ),

        "graph_risk_level": graph_level,

        "prediction": prediction,

        "reasons": reasons,

        "graph_features": graph_features,

        "agent": agent_result,
    }