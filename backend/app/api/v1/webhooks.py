
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.transaction import Transaction
from app.schemas.transaction import TransactionCreate
from app.ml.predict import predict_transaction


router = APIRouter(
    prefix="/webhooks",
    tags=["Webhooks"],
)


# =========================================================
# Database dependency
# =========================================================

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# =========================================================
# Incoming transaction webhook
# =========================================================

@router.post("/transaction")
def receive_transaction(
    data: TransactionCreate,
    db: Session = Depends(get_db),
):
    """
    Receive a new transaction and immediately calculate
    its ML abuse risk.

    Flow:

        Incoming transaction
                ↓
        Save transaction
                ↓
        Calculate graph features
                ↓
        ML prediction
                ↓
        Return risk score
    """

    # -----------------------------------------------------
    # Check duplicate transaction code
    # -----------------------------------------------------

    existing = (
        db.query(Transaction)
        .filter(
            Transaction.transaction_code
            == data.transaction_code
        )
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=409,
            detail="Transaction code already exists.",
        )

    # -----------------------------------------------------
    # Create transaction
    # -----------------------------------------------------

    transaction = Transaction(
        transaction_code=data.transaction_code,

        merchant_id=data.merchant_id,
        customer_id=data.customer_id,

        device_id=data.device_id,
        ip_address_id=data.ip_address_id,
        address_id=data.address_id,
        payment_instrument_id=data.payment_instrument_id,

        amount=data.amount,
        status=data.status,

        refund_status=data.refund_status,
        chargeback=data.chargeback,

        # Incoming transactions are not given a
        # ground-truth abuse label.
        #
        # The ML model determines the risk.
        is_abuse=False,

        created_at=datetime.utcnow(),
    )

    db.add(transaction)

    # -----------------------------------------------------
    # Flush so the transaction receives an ID
    # -----------------------------------------------------

    db.flush()

    # -----------------------------------------------------
    # ML risk prediction
    # -----------------------------------------------------

    risk_score = predict_transaction(
        db,
        transaction,
    )

    # -----------------------------------------------------
    # Convert score into decision
    # -----------------------------------------------------

    if risk_score >= 0.70:
        prediction = "ABUSE"
    else:
        prediction = "NORMAL"

    # -----------------------------------------------------
    # Commit transaction
    # -----------------------------------------------------

    db.commit()

    return {
        "transaction_id": transaction.id,
        "transaction_code": transaction.transaction_code,

        "risk_score": risk_score,
        "risk_percentage": round(
            risk_score * 100,
            2,
        ),

        "prediction": prediction,

        "status": "processed",
    }

