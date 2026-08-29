import json
from pathlib import Path
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    roc_auc_score,
)

from sklearn.model_selection import train_test_split

from app.db.session import SessionLocal

from app.ml.features import (
    build_ml_dataset,
    FEATURE_NAMES,
)

from app.ml.model import (
    create_model,
    save_model,
)


# =========================================================
# Train ML model
# =========================================================

def train_model():
    """
    Train Random Forest fraud detection model.
    """

    db = SessionLocal()

    try:

        # -------------------------------------------------
        # Build dataset
        # -------------------------------------------------

        X, y = build_ml_dataset(
            db
        )

        print("=" * 60)
        print("LOSSGRAPH - ML TRAINING")
        print("=" * 60)

        print(
            f"Total samples: {len(X)}"
        )

        print(
            f"Normal transactions: {y.count(0)}"
        )

        print(
            f"Abuse transactions: {y.count(1)}"
        )

        print()
        print("Features:")
        
        for feature in FEATURE_NAMES:
            print(
                f"  - {feature}"
            )

        # -------------------------------------------------
        # Train/test split
        # -------------------------------------------------

        X_train, X_test, y_train, y_test = (
            train_test_split(
                X,
                y,
                test_size=0.20,
                random_state=42,
                stratify=y,
            )
        )

        print()
        print(
            f"Training samples: {len(X_train)}"
        )

        print(
            f"Testing samples: {len(X_test)}"
        )

        # -------------------------------------------------
        # Create model
        # -------------------------------------------------

        model = create_model()

        print()
        print(
            "Training Random Forest..."
        )

        model.fit(
            X_train,
            y_train,
        )

        # -------------------------------------------------
        # Predictions
        # -------------------------------------------------

        predictions = model.predict(
            X_test
        )

        probabilities = model.predict_proba(
            X_test
        )[:, 1]

        # -------------------------------------------------
        # Evaluation
        # -------------------------------------------------

        print()
        print("=" * 60)
        print("MODEL EVALUATION")
        print("=" * 60)

        print()
        print("Confusion Matrix:")

        print(
            confusion_matrix(
                y_test,
                predictions,
            )
        )

        print()
        print("Classification Report:")

        print(
            classification_report(
                y_test,
                predictions,
                target_names=[
                    "NORMAL",
                    "ABUSE",
                ],
                zero_division=0,
            )
        )

        # -------------------------------------------------
        # ROC AUC
        # -------------------------------------------------

        auc = roc_auc_score(
            y_test,
            probabilities,
        )

        print(
            f"ROC-AUC: {auc:.4f}"
        )
    
        # -------------------------------------------------
        # Save evaluation results
        # -------------------------------------------------

        report = classification_report(
            y_test,
            predictions,
            target_names=[
                "NORMAL",
                "ABUSE",
            ],
            output_dict=True,
            zero_division=0,
        )

        accuracy = report["accuracy"]

        evaluation_results = {
            "accuracy": round(
                accuracy,
                4,
            ),

            "roc_auc": round(
                float(auc),
                4,
            ),

            "precision": round(
                report["ABUSE"]["precision"],
                4,
            ),

            "recall": round(
                report["ABUSE"]["recall"],
                4,
            ),

            "f1_score": round(
                report["ABUSE"]["f1-score"],
                4,
            ),

            "normal": {
                "precision": round(
                    report["NORMAL"]["precision"],
                    4,
                ),
                "recall": round(
                    report["NORMAL"]["recall"],
                    4,
                ),
                "f1_score": round(
                    report["NORMAL"]["f1-score"],
                    4,
                ),
                "support": int(
                    report["NORMAL"]["support"]
                ),
            },

            "abuse": {
                "precision": round(
                    report["ABUSE"]["precision"],
                    4,
                ),
                "recall": round(
                    report["ABUSE"]["recall"],
                    4,
                ),
                "f1_score": round(
                    report["ABUSE"]["f1-score"],
                    4,
                ),
                "support": int(
                    report["ABUSE"]["support"]
                ),
            },
        }

        evaluation_path = (
            Path(__file__).resolve().parent
            / "saved"
            / "evaluation.json"
        )

        evaluation_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with open(
            evaluation_path,
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                evaluation_results,
                file,
                indent=4,
            )

        print()
        print(
            f"Evaluation saved to: {evaluation_path}"
        )


        # -------------------------------------------------
        # Feature importance
        # -------------------------------------------------

        print()
        print("=" * 60)
        print("FEATURE IMPORTANCE")
        print("=" * 60)

        importance = sorted(
            zip(
                FEATURE_NAMES,
                model.feature_importances_,
            ),
            key=lambda x: x[1],
            reverse=True,
        )

        for name, value in importance:
            print(
                f"{name:<30} {value:.4f}"
            )

        # -------------------------------------------------
        # Save model
        # -------------------------------------------------

        save_model(
            model
        )

        print()
        print("=" * 60)
        print("TRAINING COMPLETE")
        print("=" * 60)

    finally:

        db.close()


if __name__ == "__main__":
    train_model()