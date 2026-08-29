
from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.transaction import Transaction
from app.graph.clustering import find_suspicious_clusters


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
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
# Dashboard Overview
# =========================================================

@router.get("/overview")
def get_dashboard_overview(
    db: Session = Depends(get_db),
):
    """
    Return the main LossGraph dashboard statistics.
    """

    # -----------------------------------------------------
    # Transaction counts
    # -----------------------------------------------------

    total_transactions = (
        db.query(func.count(Transaction.id))
        .scalar()
        or 0
    )

    abuse_transactions = (
        db.query(func.count(Transaction.id))
        .filter(Transaction.is_abuse == True)
        .scalar()
        or 0
    )

    normal_transactions = (
        total_transactions
        - abuse_transactions
    )

    # -----------------------------------------------------
    # Total financial exposure of known abuse
    # -----------------------------------------------------

    abuse_exposure = (
        db.query(
            func.coalesce(
                func.sum(Transaction.amount),
                0,
            )
        )
        .filter(Transaction.is_abuse == True)
        .scalar()
    )

    # -----------------------------------------------------
    # Detect suspicious clusters
    # -----------------------------------------------------

    clusters = find_suspicious_clusters(
        db,
        threshold=0.70,
        minimum_members=3,
    )

    # -----------------------------------------------------
    # High-risk transaction count
    #
    # A transaction belongs to a high-risk cluster when
    # it is part of a cluster with risk >= 0.70.
    # -----------------------------------------------------

    high_risk_transactions = set()

    for cluster in clusters:
        if cluster["risk_score"] >= 0.70:
            for transaction in cluster["transactions"]:
                high_risk_transactions.add(
                    transaction.id
                )

    # -----------------------------------------------------
    # Cluster statistics
    # -----------------------------------------------------

    cluster_count = len(clusters)

    average_cluster_risk = 0.0

    if clusters:
        average_cluster_risk = round(
            sum(
                cluster["risk_score"]
                for cluster in clusters
            )
            / len(clusters),
            4,
        )

    # -----------------------------------------------------
    # Return dashboard data
    # -----------------------------------------------------

    return {
        "total_transactions": total_transactions,

        "normal_transactions": normal_transactions,

        "abuse_transactions": abuse_transactions,

        "abuse_percentage": (
            round(
                (
                    abuse_transactions
                    / total_transactions
                )
                * 100,
                2,
            )
            if total_transactions
            else 0.0
        ),

        "abuse_exposure": float(
            abuse_exposure
        ),

        "high_risk_transactions": len(
            high_risk_transactions
        ),

        "cluster_count": cluster_count,

        "average_cluster_risk": average_cluster_risk,

        "average_cluster_risk_percentage": round(
            average_cluster_risk * 100,
            2,
        ),
    }
