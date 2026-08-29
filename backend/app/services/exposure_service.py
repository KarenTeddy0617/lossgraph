from decimal import Decimal


def calculate_cluster_exposure(
    transactions,
) -> Decimal:
    """
    Calculate total transaction exposure for a cluster.
    """

    return sum(
        (
            transaction.amount
            for transaction in transactions
        ),
        Decimal("0.00"),
    )