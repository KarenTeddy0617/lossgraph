from pathlib import Path

import joblib

from sklearn.ensemble import RandomForestClassifier


# =========================================================
# Model location
# =========================================================

MODEL_DIR = Path("app/ml/saved")

MODEL_PATH = MODEL_DIR / "fraud_model.joblib"


# =========================================================
# Create model
# =========================================================

def create_model():
    """
    Create the Random Forest fraud classifier.
    """

    return RandomForestClassifier(
        n_estimators=200,
        max_depth=10,
        min_samples_leaf=2,
        random_state=42,
        class_weight="balanced",
        n_jobs=-1,
    )


# =========================================================
# Save model
# =========================================================

def save_model(model):
    """
    Save trained model to disk.
    """

    MODEL_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    joblib.dump(
        model,
        MODEL_PATH,
    )

    print(
        f"Model saved to: {MODEL_PATH}"
    )


# =========================================================
# Load model
# =========================================================

def load_model():
    """
    Load trained model from disk.
    """

    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"ML model not found: {MODEL_PATH}. "
            "Train the model first."
        )

    return joblib.load(
        MODEL_PATH
    )