from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.transaction import Transaction
from app.api.v1.auth import get_current_user

from app.ml.predict import predict_transaction

from app.agent.orchestrator import (
    investigate_transaction,
)

from app.schemas.agent import (
    AgentInvestigation,
)


# =========================================================
# Router
# =========================================================

router = APIRouter(
    prefix="/agent",
    tags=["Risk Analysis Agent"],
)


# =========================================================
# Analyze Transaction
# =========================================================

@router.get(
    "/analyze/{transaction_id}",
    response_model=AgentInvestigation,
)
def analyze_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Analyze one transaction using:

    - Machine learning risk
    - Graph-based risk
    - Refund behaviour
    - Abuse cluster information
    - AI investigation
    """

    # -----------------------------------------------------
    # 1. Find transaction
    # -----------------------------------------------------

    transaction = (
        db.query(Transaction)
        .filter(
            Transaction.id == transaction_id
        )
        .first()
    )

    if transaction is None:

        raise HTTPException(
            status_code=404,
            detail="Transaction not found",
        )

    # -----------------------------------------------------
    # 2. ML risk
    # -----------------------------------------------------

    try:

        ml_risk = predict_transaction(
            db,
            transaction,
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail="ML risk prediction failed.",
        ) from exc

    # -----------------------------------------------------
    # 3. AI investigation
    # -----------------------------------------------------

    try:

        result = investigate_transaction(
            db=db,
            transaction_id=transaction_id,
            ml_risk=ml_risk,
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail="AI investigation failed.",
        ) from exc

    # -----------------------------------------------------
    # 4. Validate final API response
    # -----------------------------------------------------

    try:

        return AgentInvestigation(
            **result
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail="Invalid agent response.",
        ) from exc