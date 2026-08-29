from app.db.session import SessionLocal
from app.models.transaction import Transaction

from app.graph.features import calculate_graph_features
from app.graph.clustering import (
    calculate_graph_score,
    get_graph_risk_level,
)


def main():

    db = SessionLocal()

    try:

        transactions = (
            db.query(Transaction)
            .limit(10)
            .all()
        )

        print("=" * 50)
        print("LOSSGRAPH - GRAPH RISK TEST")
        print("=" * 50)

        for transaction in transactions:

            features = calculate_graph_features(
                db,
                transaction,
            )

            score = calculate_graph_score(
                db,
                transaction,
            )

            level = get_graph_risk_level(
                score
            )

            print()
            print(
                f"Transaction: "
                f"{transaction.transaction_code}"
            )

            print(
                f"Shared device: "
                f"{features['shared_device_count']}"
            )

            print(
                f"Shared IP: "
                f"{features['shared_ip_count']}"
            )

            print(
                f"Shared address: "
                f"{features['shared_address_count']}"
            )

            print(
                f"Shared payment: "
                f"{features['shared_payment_count']}"
            )

            print(
                f"Graph Score: {score}"
            )

            print(
                f"Graph Risk: {level}"
            )

    finally:

        db.close()


if __name__ == "__main__":
    main()