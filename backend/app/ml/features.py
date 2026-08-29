from app.models.transaction import Transaction
from app.graph.features import calculate_all_graph_features


# =========================================================
# ML FEATURE NAMES
# =========================================================

FEATURE_NAMES = [
    "amount",
    "is_success",
    "is_failed",
    "is_pending",
    "has_refund_request",
    "has_refund",
    "chargeback",

    # Graph features
    "shared_device_count",
    "shared_ip_count",
    "shared_address_count",
    "shared_payment_count",

    "device_customer_count",
    "ip_customer_count",
    "address_customer_count",
    "payment_customer_count",
]


# =========================================================
# Transaction -> ML features
# =========================================================

def transaction_to_features(
    transaction: Transaction,
    graph_features: dict,
) -> dict:

    status = (
        transaction.status.upper()
        if transaction.status
        else ""
    )

    refund_status = (
        transaction.refund_status.upper()
        if transaction.refund_status
        else "NONE"
    )

    return {
        # -------------------------------------------------
        # Transaction features
        # -------------------------------------------------

        "amount": float(transaction.amount),

        "is_success": int(
            status == "SUCCESS"
        ),

        "is_failed": int(
            status == "FAILED"
        ),

        "is_pending": int(
            status == "PENDING"
        ),

        "has_refund_request": int(
            refund_status == "REQUESTED"
        ),

        "has_refund": int(
            refund_status == "REFUNDED"
        ),

        "chargeback": int(
            transaction.chargeback
        ),

        # -------------------------------------------------
        # Graph features
        # -------------------------------------------------

        "shared_device_count": graph_features[
            "shared_device_count"
        ],

        "shared_ip_count": graph_features[
            "shared_ip_count"
        ],

        "shared_address_count": graph_features[
            "shared_address_count"
        ],

        "shared_payment_count": graph_features[
            "shared_payment_count"
        ],

        "device_customer_count": graph_features[
            "device_customer_count"
        ],

        "ip_customer_count": graph_features[
            "ip_customer_count"
        ],

        "address_customer_count": graph_features[
            "address_customer_count"
        ],

        "payment_customer_count": graph_features[
            "payment_customer_count"
        ],
    }


# =========================================================
# Build ML dataset
# =========================================================

def build_ml_dataset(
    db,
    transactions=None,
):
    """
    Build supervised ML dataset.

    Ground-truth labels come directly from the
    transactions.is_abuse column.

    is_abuse = 0 -> normal transaction
    is_abuse = 1 -> known abuse transaction

    NOTE:
    This is appropriate for our synthetic/demo dataset.
    In a real system, labels should come from verified
    fraud/abuse investigations.
    """

    if transactions is None:
        transactions = (
            db.query(Transaction)
            .order_by(Transaction.id)
            .all()
        )

    if not transactions:
        raise ValueError(
            "No transactions available for ML training."
        )

    # -----------------------------------------------------
    # Calculate graph features for the COMPLETE dataset
    # -----------------------------------------------------

    graph_features = calculate_all_graph_features(
        db,
        transactions,
    )

    X = []
    y = []

    for transaction in transactions:

        features = transaction_to_features(
            transaction,
            graph_features[transaction.id],
        )

        X.append(
            [
                features[name]
                for name in FEATURE_NAMES
            ]
        )

        # -------------------------------------------------
        # Ground-truth label
        # -------------------------------------------------

        y.append(
            int(transaction.is_abuse)
        )

    return X, y