from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.transaction import Transaction
from app.models.audit_event import AuditEvent
from app.schemas.transaction import TransactionCreate
from app.ml.predict import predict_transaction


router = APIRouter(
    prefix="/webhooks",
    tags=["Webhooks"],
)


@router.post("/transaction")
def receive_transaction(
    data: TransactionCreate,
    db: Session = Depends(get_db),
):
    """
    Receive a transaction, calculate ML risk,
    and create an audit trail entry.
    """

    # Check duplicate transaction
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

    # Create transaction
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
        is_abuse=False,
        created_at=datetime.utcnow(),
    )

    db.add(transaction)

    # Get transaction ID
    db.flush()

    # ML prediction
    risk_score = predict_transaction(
        db,
        transaction,
    )

    prediction = (
        "ABUSE"
        if risk_score >= 0.70
        else "NORMAL"
    )

    # -----------------------------------------------------
    # Create audit event
    # -----------------------------------------------------

    audit_event = AuditEvent(
        merchant_id=transaction.merchant_id,
        event_type="TRANSACTION_RISK_ASSESSMENT",
        transaction_id=transaction.id,
        action=prediction,
        reason=(
            f"ML risk assessment completed. "
            f"Risk score: {risk_score * 100:.2f}%"
        ),
        created_at=datetime.utcnow(),
    )

    db.add(audit_event)

    # Commit both transaction + audit event
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