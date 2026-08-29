from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.transaction import Transaction
from app.ml.predict import predict_transaction

router = APIRouter(
    prefix="/transactions",
    tags=["Transactions"],
)

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
# =========================================================
# Get all transactions
# =========================================================

@router.get("/")
def get_transactions(
    db: Session = Depends(get_db),
):
    transactions = (
        db.query(Transaction)
        .order_by(Transaction.id)
        .all()
    )

    return transactions
# =========================================================
# Get single transaction
# =========================================================

@router.get("/{transaction_id}")
def get_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
):
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

    return transaction


# =========================================================
# Get transaction abuse risk
# =========================================================

@router.get("/{transaction_id}/risk")
def get_transaction_risk(
    transaction_id: int,
    db: Session = Depends(get_db),
):
    """
    Calculate ML-based abuse risk for a transaction.
    """

    # -----------------------------------------------------
    # Find transaction
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
            detail="Transaction not found.",
        )
    

    # -----------------------------------------------------
    # Predict abuse probability
    # -----------------------------------------------------

    risk_score = predict_transaction(
        db,
        transaction,
    )

    '''

    # -----------------------------------------------------
    # Convert probability into classification
    # -----------------------------------------------------

    if risk_score >= 0.50:
        prediction = "ABUSE"
    else:
        prediction = "NORMAL"
    '''

    # -----------------------------------------------------
    # Return API response
    # -----------------------------------------------------

    return {
        "transaction_id": transaction.id,
        "transaction_code": transaction.transaction_code,
        "risk_score": risk_score,
        "risk_percentage": round(
            risk_score * 100,
            2,
        ),
        "prediction": (
           "ABUSE"
            if risk_score >= 0.5
            else "NORMAL" 
        ),
    }