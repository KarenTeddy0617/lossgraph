from app.db.session import SessionLocal
from app.models.transaction import Transaction
from app.risk.scoring import calculate_behavior_score


def main():
    db = SessionLocal()

    try:
        transactions = (
            db.query(Transaction)
            .order_by(Transaction.created_at.desc())
            .limit(10)
            .all()
        )

        print("\n========================================")
        print("LOSSGRAPH BEHAVIORAL RISK TEST")
        print("========================================")

        for transaction in transactions:
            result = calculate_behavior_score(transaction)

            print(
                f"\nTransaction: {transaction.transaction_code}"
            )

            print(
                f"Amount: ₹{transaction.amount}"
            )

            print(
                f"Chargeback: {transaction.chargeback}"
            )

            print(
                f"Refund: {transaction.refund_status}"
            )

            print(
                f"Behavior Score: "
                f"{result['behavior_score']}"
            )

            print(
                f"Risk Level: "
                f"{result['risk_level']}"
            )

    finally:
        db.close()


if __name__ == "__main__":
    main()