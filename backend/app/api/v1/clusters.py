from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.graph.clustering import find_suspicious_clusters


router = APIRouter(
    prefix="/clusters",
    tags=["Abuse Clusters"],
)


# =========================================================
# Database Dependency
# =========================================================

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# =========================================================
# Get Abuse Clusters
# =========================================================

@router.get("/")
def get_abuse_clusters(
    db: Session = Depends(get_db),
):
    """
    Detect and return suspicious transaction clusters.
    """

    clusters = find_suspicious_clusters(
        db,
        threshold=0.70,
        minimum_members=3,
    )

    return [
        {
            "merchant_id": cluster["merchant_id"],
            "member_count": cluster["member_count"],
            "risk_score": cluster["risk_score"],
            "risk_percentage": round(
                cluster["risk_score"] * 100,
                2,
            ),
            "exposure_amount": float(
                cluster["exposure_amount"]
            ),
            "transaction_ids": [
                transaction.id
                for transaction in cluster["transactions"]
            ],
            "transaction_codes": [
                transaction.transaction_code
                for transaction in cluster["transactions"]
            ],
        }
        for cluster in clusters
    ]