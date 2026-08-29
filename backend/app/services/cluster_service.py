from sqlalchemy.orm import Session

from app.graph.clustering import find_suspicious_clusters
from app.models.abuse_cluster import AbuseCluster
from app.models.abuse_cluster_member import AbuseClusterMember


def generate_cluster_code(number: int) -> str:
    """
    Generate a readable abuse-cluster identifier.
    """

    return f"CLU_{number:04d}"


def detect_and_store_clusters(
    db: Session,
    threshold: float = 0.70,
    minimum_members: int = 3,
):
    """
    Detect suspicious transaction clusters and store them
    in the abuse_clusters table.

    Also stores the relationship between each abuse cluster
    and its member transactions in abuse_cluster_members.

    Existing abuse clusters and their memberships are removed
    before regeneration.
    """

    # -----------------------------------------------------
    # Remove previously generated cluster memberships
    # -----------------------------------------------------

    db.query(AbuseClusterMember).delete()

    # -----------------------------------------------------
    # Remove previously generated clusters
    # -----------------------------------------------------

    db.query(AbuseCluster).delete()

    db.flush()

    # -----------------------------------------------------
    # Detect suspicious clusters
    # -----------------------------------------------------

    clusters = find_suspicious_clusters(
        db,
        threshold=threshold,
        minimum_members=minimum_members,
    )

    created_clusters = []

    # -----------------------------------------------------
    # Store clusters and their transaction memberships
    # -----------------------------------------------------

    for index, cluster in enumerate(
        clusters,
        start=1,
    ):

        abuse_cluster = AbuseCluster(
            merchant_id=cluster["merchant_id"],
            cluster_code=generate_cluster_code(index),
            risk_score=cluster["risk_score"],
            member_count=cluster["member_count"],
            exposure_amount=cluster["exposure_amount"],
        )

        db.add(abuse_cluster)

        # Flush so abuse_cluster.id is available
        db.flush()

        # -------------------------------------------------
        # Store each transaction belonging to this cluster
        # -------------------------------------------------

        for transaction in cluster["transactions"]:

            membership = AbuseClusterMember(
                cluster_id=abuse_cluster.id,
                transaction_id=transaction.id,
            )

            db.add(membership)

        created_clusters.append(abuse_cluster)

    # -----------------------------------------------------
    # Commit everything
    # -----------------------------------------------------

    db.commit()

    return created_clusters