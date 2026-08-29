from collections import defaultdict
from decimal import Decimal

import networkx as nx
from sqlalchemy.orm import Session

from app.models.transaction import Transaction
from app.graph.features import calculate_all_graph_features


# =========================================================
# Transaction-level graph scoring
# =========================================================

def calculate_graph_score_from_features(
    features: dict,
) -> float:
    """
    Calculate graph risk score from precomputed features.

    Returns a score between 0 and 1.
    """

    shared_device = features["shared_device_count"]
    shared_ip = features["shared_ip_count"]
    shared_address = features["shared_address_count"]
    shared_payment = features["shared_payment_count"]

    device_customers = features["device_customer_count"]
    ip_customers = features["ip_customer_count"]
    address_customers = features["address_customer_count"]
    payment_customers = features["payment_customer_count"]

    # -----------------------------------------------------
    # Normalize shared-resource signals
    # -----------------------------------------------------

    device_score = min(shared_device / 10, 1.0)
    ip_score = min(shared_ip / 10, 1.0)
    address_score = min(shared_address / 10, 1.0)
    payment_score = min(shared_payment / 10, 1.0)

    # -----------------------------------------------------
    # Normalize customer-sharing signals
    # -----------------------------------------------------

    device_customer_score = min(
        device_customers / 10,
        1.0,
    )

    ip_customer_score = min(
        ip_customers / 10,
        1.0,
    )

    address_customer_score = min(
        address_customers / 10,
        1.0,
    )

    payment_customer_score = min(
        payment_customers / 10,
        1.0,
    )

    # -----------------------------------------------------
    # Weighted graph risk score
    # -----------------------------------------------------

        # -----------------------------------------------------
    # Weighted graph risk score
    #
    # Distinct-customer sharing is the real fraud signal:
    # one customer reusing their own device/IP/payment many
    # times is normal repeat behaviour and should NOT drive
    # the score up. Multiple DIFFERENT customers sharing the
    # same device/IP/address/payment is what indicates
    # coordinated abuse, so those features dominate here.
    # -----------------------------------------------------

    score = (
        device_customer_score * 0.30
        + payment_customer_score * 0.25
        + ip_customer_score * 0.20
        + address_customer_score * 0.15
        + device_score * 0.03
        + payment_score * 0.03
        + ip_score * 0.02
        + address_score * 0.02
    )

    return round(
        min(max(score, 0.0), 1.0),
        4,
    )


def calculate_graph_score(
    db: Session,
    transaction: Transaction,
) -> float:
    """
    Calculate graph score for one transaction while
    considering the complete transaction graph.
    """
    transactions = (
        db.query(Transaction)
        .order_by(Transaction.id)
        .all()
    )

    all_features = calculate_all_graph_features(
        db,
        transactions,
    )
    features = all_features[transaction.id]

    return calculate_graph_score_from_features(features)


def get_graph_risk_level(score: float) -> str:
    """
    Convert graph risk score into a human-readable risk level.
    """

    if score >= 0.70:
        return "HIGH"

    if score >= 0.40:
        return "MEDIUM"

    return "LOW"


# =========================================================
# Suspicious transaction detection
# =========================================================

def find_suspicious_transactions(
    db: Session,
    threshold: float = 0.70,
):
    """
    Find suspicious transactions efficiently.

    Graph features are calculated once for the complete
    transaction dataset.

    Returns:
        list of (transaction, graph_score)
    """

    transactions = (
        db.query(Transaction)
        .order_by(Transaction.id)
        .all()
    )

    if not transactions:
        return []

    # -----------------------------------------------------
    # Calculate graph features once
    # -----------------------------------------------------

    all_features = calculate_all_graph_features(
        db,
        transactions,
    )

    suspicious = []

    # -----------------------------------------------------
    # Score transactions in memory
    # -----------------------------------------------------

    for transaction in transactions:

        features = all_features[transaction.id]

        score = calculate_graph_score_from_features(
            features
        )

        if score >= threshold:
            suspicious.append(
                (transaction, score)
            )

    return suspicious


# =========================================================
# Build suspicious transaction graph
# =========================================================

def build_suspicious_transaction_graph(
    db: Session,
    suspicious_transactions,
):
    """
    Build a NetworkX graph where each node represents a
    suspicious transaction.

    Two transactions are connected only when they share
    at least two important entities.
    """

    graph = nx.Graph()

    transactions = [
        transaction
        for transaction, _score in suspicious_transactions
    ]

    # -----------------------------------------------------
    # Add transaction nodes
    # -----------------------------------------------------

    for transaction in transactions:

        graph.add_node(
            transaction.id,
            transaction_id=transaction.id,
            merchant_id=transaction.merchant_id,
        )

    # -----------------------------------------------------
    # Entity -> transactions mapping
    # -----------------------------------------------------

            # -----------------------------------------------------
    # Quick lookup for same-customer filtering
    # -----------------------------------------------------

    transaction_lookup_by_id = {
        transaction.id: transaction
        for transaction in transactions
    }

    # -----------------------------------------------------
    # Entity -> transactions mapping
    # -----------------------------------------------------

    entity_transactions = defaultdict(list)

    for transaction in transactions:

        # NOTE: "customer" is deliberately NOT added here.
        # Two transactions from the SAME customer are not
        # evidence of coordinated abuse between DIFFERENT
        # people — that's just one person's normal repeat
        # activity. Only shared devices/IPs/addresses/payment
        # instruments across transactions are meaningful
        # signals of coordination.

        entity_transactions[
            ("device", transaction.device_id)
        ].append(transaction.id)

        entity_transactions[
            ("ip", transaction.ip_address_id)
        ].append(transaction.id)

        entity_transactions[
            ("address", transaction.address_id)
        ].append(transaction.id)

        entity_transactions[
            ("payment", transaction.payment_instrument_id)
        ].append(transaction.id)

    # -----------------------------------------------------
    # Count shared entities between transaction pairs
    # -----------------------------------------------------

    pair_shared_entities = defaultdict(int)

    for (
        _entity_type,
        _entity_id,
    ), transaction_ids in entity_transactions.items():

        if len(transaction_ids) < 2:
            continue

        for i in range(len(transaction_ids)):

            for j in range(i + 1, len(transaction_ids)):

                tx_a_id = transaction_ids[i]
                tx_b_id = transaction_ids[j]

                # Skip pairs belonging to the same customer —
                # repeat purchases by one person are not
                # coordination between different actors.
                if (
                    transaction_lookup_by_id[tx_a_id].customer_id
                    == transaction_lookup_by_id[tx_b_id].customer_id
                ):
                    continue

                pair = tuple(
                    sorted((tx_a_id, tx_b_id))
                )

                pair_shared_entities[pair] += 1

    # -----------------------------------------------------
    # Connect only strongly related transactions
    # -----------------------------------------------------

    MIN_SHARED_ENTITIES = 2

    for (
        tx_a,
        tx_b,
    ), shared_count in pair_shared_entities.items():

        if shared_count < MIN_SHARED_ENTITIES:
            continue

        graph.add_edge(
            tx_a,
            tx_b,
            shared_entities=shared_count,
        )

    return graph


# =========================================================
# Extract suspicious clusters
# =========================================================

def find_suspicious_clusters(
    db: Session,
    threshold: float = 0.70,
    minimum_members: int = 3,
):
    """
    Find groups of suspicious transactions connected through
    strong shared-entity relationships.

    Each connected component becomes a candidate abuse cluster.
    """

    # -----------------------------------------------------
    # Find suspicious transactions
    # -----------------------------------------------------

    suspicious_transactions = find_suspicious_transactions(
        db,
        threshold=threshold,
    )

    if not suspicious_transactions:
        return []

    # -----------------------------------------------------
    # Build suspicious transaction graph
    # -----------------------------------------------------

    graph = build_suspicious_transaction_graph(
        db,
        suspicious_transactions,
    )

    # -----------------------------------------------------
    # Lookup dictionaries
    # -----------------------------------------------------

    score_lookup = {
        transaction.id: score
        for transaction, score in suspicious_transactions
    }

    transaction_lookup = {
        transaction.id: transaction
        for transaction, _score in suspicious_transactions
    }

    clusters = []

    # -----------------------------------------------------
    # Find connected components
    # -----------------------------------------------------

    for component in nx.connected_components(graph):

        if len(component) < minimum_members:
            continue

        transactions = [
            transaction_lookup[transaction_id]
            for transaction_id in component
        ]

        # -------------------------------------------------
        # Split clusters by merchant
        # -------------------------------------------------

        merchant_groups = defaultdict(list)

        for transaction in transactions:

            merchant_groups[
                transaction.merchant_id
            ].append(transaction)

        # -------------------------------------------------
        # Build merchant-specific clusters
        # -------------------------------------------------

        for (
            merchant_id,
            merchant_transactions,
        ) in merchant_groups.items():

            if len(merchant_transactions) < minimum_members:
                continue

            merchant_scores = [
                score_lookup[transaction.id]
                for transaction in merchant_transactions
            ]

            # ---------------------------------------------
            # Average risk score
            # ---------------------------------------------

            cluster_score = round(
                sum(merchant_scores)
                / len(merchant_scores),
                4,
            )

            # ---------------------------------------------
            # Total financial exposure
            # ---------------------------------------------

            exposure = sum(
                (
                    transaction.amount
                    for transaction in merchant_transactions
                ),
                Decimal("0.00"),
            )

            clusters.append(
                {
                    "merchant_id": merchant_id,
                    "transactions": merchant_transactions,
                    "member_count": len(
                        merchant_transactions
                    ),
                    "risk_score": cluster_score,
                    "exposure_amount": exposure,
                }
            )

    # -----------------------------------------------------
    # Highest-risk clusters first
    # -----------------------------------------------------

    clusters.sort(
        key=lambda cluster: (
            cluster["risk_score"],
            cluster["exposure_amount"],
        ),
        reverse=True,
    )

    return clusters