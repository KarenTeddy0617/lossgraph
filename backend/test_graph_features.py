from app.db.session import SessionLocal
from app.models.transaction import Transaction
from app.graph.features import calculate_graph_features


def main():

    db = SessionLocal()

    try:

        transaction = (
            db.query(Transaction)
            .first()
        )

        if transaction is None:
            print("No transactions found.")
            return

        print("Transaction:", transaction.transaction_code)

        features = calculate_graph_features(
            db,
            transaction,
        )

        print("\nGraph Features")
        print("-------------------------")

        for name, value in features.items():
            print(f"{name}: {value}")

    finally:

        db.close()


if __name__ == "__main__":
    main()