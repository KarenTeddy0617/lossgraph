from collections import defaultdict

from sqlalchemy.orm import Session

from app.models.transaction import Transaction


def build_transaction_graph(
    db: Session,
    merchant_id: int | None = None,
):
    """
    Build a relationship graph from transactions.

    Nodes represent entities such as customers, devices,
    IP addresses, addresses and payment instruments.

    Edges represent relationships created by transactions.
    """

    query = db.query(Transaction)

    if merchant_id is not None:
        query = query.filter(
            Transaction.merchant_id == merchant_id
        )

    transactions = query.all()

    graph = defaultdict(set)

    for transaction in transactions:

        customer = f"customer:{transaction.customer_id}"
        device = f"device:{transaction.device_id}"
        ip = f"ip:{transaction.ip_address_id}"
        address = f"address:{transaction.address_id}"
        payment = f"payment:{transaction.payment_instrument_id}"

        entities = [
            customer,
            device,
            ip,
            address,
            payment,
        ]

        # Connect every entity involved in the transaction
        for i in range(len(entities)):

            for j in range(i + 1, len(entities)):

                node_a = entities[i]
                node_b = entities[j]

                graph[node_a].add(node_b)
                graph[node_b].add(node_a)

    return graph