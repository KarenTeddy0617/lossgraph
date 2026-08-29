from collections import Counter, defaultdict

from sqlalchemy.orm import Session

from app.models.transaction import Transaction


def calculate_all_graph_features(
    db: Session,
    transactions: list[Transaction] | None = None,
):
    """
    Calculate graph features efficiently for transactions.

    IMPORTANT:
    Features are calculated against the complete transaction
    dataset so shared devices, IPs, addresses and payment
    instruments can be detected correctly.

    If `transactions` is provided, those transactions are the
    ones for which features are returned, but relationships are
    still calculated against ALL transactions in the database.
    """

    # ---------------------------------------------------------
    # Load complete transaction dataset
    # ---------------------------------------------------------

    all_transactions = (
        db.query(Transaction)
        .order_by(Transaction.id)
        .all()
    )

    if not all_transactions:
        return {}

    # If no specific transactions were requested,
    # return features for the complete dataset.
    if transactions is None:
        transactions = all_transactions

    # ---------------------------------------------------------
    # Count transactions using each resource
    # ---------------------------------------------------------

    device_count = Counter()
    ip_count = Counter()
    address_count = Counter()
    payment_count = Counter()

    # ---------------------------------------------------------
    # Track customers using each resource
    # ---------------------------------------------------------

    device_customers = defaultdict(set)
    ip_customers = defaultdict(set)
    address_customers = defaultdict(set)
    payment_customers = defaultdict(set)

    # ---------------------------------------------------------
    # Build resource indexes from ALL transactions
    # ---------------------------------------------------------

    for transaction in all_transactions:

        device_count[transaction.device_id] += 1

        ip_count[transaction.ip_address_id] += 1

        address_count[transaction.address_id] += 1

        payment_count[
            transaction.payment_instrument_id
        ] += 1

        device_customers[
            transaction.device_id
        ].add(
            transaction.customer_id
        )

        ip_customers[
            transaction.ip_address_id
        ].add(
            transaction.customer_id
        )

        address_customers[
            transaction.address_id
        ].add(
            transaction.customer_id
        )

        payment_customers[
            transaction.payment_instrument_id
        ].add(
            transaction.customer_id
        )

    # ---------------------------------------------------------
    # Calculate features for requested transactions
    # ---------------------------------------------------------

    features = {}

    for transaction in transactions:

        features[transaction.id] = {
            # Number of OTHER transactions sharing resource
            "shared_device_count": max(
                device_count[transaction.device_id] - 1,
                0,
            ),

            "shared_ip_count": max(
                ip_count[transaction.ip_address_id] - 1,
                0,
            ),

            "shared_address_count": max(
                address_count[transaction.address_id] - 1,
                0,
            ),

            "shared_payment_count": max(
                payment_count[
                    transaction.payment_instrument_id
                ] - 1,
                0,
            ),

            # Number of distinct customers using resource
            "device_customer_count": len(
                device_customers[
                    transaction.device_id
                ]
            ),

            "ip_customer_count": len(
                ip_customers[
                    transaction.ip_address_id
                ]
            ),

            "address_customer_count": len(
                address_customers[
                    transaction.address_id
                ]
            ),

            "payment_customer_count": len(
                payment_customers[
                    transaction.payment_instrument_id
                ]
            ),
        }

    return features


def calculate_graph_features(
    db: Session,
    transaction: Transaction,
):
    """
    Calculate graph features for one transaction.

    Kept for compatibility with existing code.
    """

    all_features = calculate_all_graph_features(
        db,
        [transaction],
    )

    return all_features[transaction.id]