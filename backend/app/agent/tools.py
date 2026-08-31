from sqlalchemy.orm import Session

from app.models.transaction import Transaction
from app.models.refund import Refund
from app.models.abuse_cluster_member import AbuseClusterMember
from app.models.abuse_cluster import AbuseCluster
from app.graph.features import calculate_graph_features
from app.graph.clustering import (
    calculate_graph_score_from_features,
    get_graph_risk_level,
)


def get_transaction(
    db: Session,
    transaction_id: int,
):

    transaction = (
        db.query(Transaction)
        .filter(Transaction.id == transaction_id)
        .first()
    )

    if not transaction:
        return None

    return {
        "id": transaction.id,
        "transaction_code": transaction.transaction_code,
        "merchant_id": transaction.merchant_id,
        "customer_id": transaction.customer_id,
        "amount": float(transaction.amount),
        "status": transaction.status,
        "refund_status": transaction.refund_status,
        "chargeback": transaction.chargeback,
        "is_abuse": transaction.is_abuse,
        "created_at": transaction.created_at.isoformat(),
    }


def get_graph_analysis(
    db: Session,
    transaction_id: int,
):

    transaction = (
        db.query(Transaction)
        .filter(Transaction.id == transaction_id)
        .first()
    )

    if not transaction:
        return None

    features = calculate_graph_features(
        db,
        transaction,
    )

    graph_score = calculate_graph_score_from_features(
        features
    )

    risk_level = get_graph_risk_level(
        graph_score
    )

    return {
        "graph_score": graph_score,
        "graph_risk_level": risk_level,
        "features": features,
    }


def get_transaction_refunds(
    db: Session,
    transaction_id: int,
):

    refunds = (
        db.query(Refund)
        .filter(
            Refund.transaction_id == transaction_id
        )
        .all()
    )

    return [
        {
            "id": refund.id,
            "amount": float(refund.amount),
            "reason": refund.reason,
            "status": refund.status,
            "created_at": refund.created_at.isoformat(),
        }
        for refund in refunds
    ]


def get_cluster_information(
    db: Session,
    transaction_id: int,
):

    membership = (
        db.query(AbuseClusterMember)
        .filter(
            AbuseClusterMember.transaction_id
            == transaction_id
        )
        .first()
    )

    if not membership:
        return {
            "in_cluster": False
        }

    cluster = (
        db.query(AbuseCluster)
        .filter(
            AbuseCluster.id
            == membership.cluster_id
        )
        .first()
    )

    if not cluster:
        return {
            "in_cluster": False
        }

    return {
        "in_cluster": True,
        "cluster_id": cluster.id,
        "cluster_code": cluster.cluster_code,
        "risk_score": float(cluster.risk_score),
        "member_count": cluster.member_count,
        "exposure_amount": float(
            cluster.exposure_amount
        ),
    }