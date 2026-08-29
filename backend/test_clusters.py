from app.db.session import SessionLocal
from app.services.cluster_service import (
    detect_and_store_clusters,
)


def main():

    db = SessionLocal()

    try:

        print("=" * 60)
        print("LOSSGRAPH - ABUSE CLUSTER DETECTION")
        print("=" * 60)

        clusters = detect_and_store_clusters(
            db,
            threshold=0.70,
            minimum_members=3,
        )

        print()
        print(
            f"Suspicious clusters found: {len(clusters)}"
        )

        print()

        for cluster in clusters[:10]:

            print("-" * 60)

            print(
                f"Cluster: {cluster.cluster_code}"
            )

            print(
                f"Merchant ID: {cluster.merchant_id}"
            )

            print(
                f"Members: {cluster.member_count}"
            )

            print(
                f"Risk Score: {float(cluster.risk_score):.4f}"
            )

            print(
                f"Exposure: ₹{float(cluster.exposure_amount):,.2f}"
            )

            if float(cluster.risk_score) >= 0.70:
                risk_level = "HIGH"
            elif float(cluster.risk_score) >= 0.40:
                risk_level = "MEDIUM"
            else:
                risk_level = "LOW"

            print(
                f"Risk Level: {risk_level}"
            )

        print()
        print("=" * 60)

    finally:
        db.close()


if __name__ == "__main__":
    main()