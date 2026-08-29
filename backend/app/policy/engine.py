from app.policy.thresholds import (
    LOW_RISK_THRESHOLD,
    HIGH_RISK_THRESHOLD,
)


def classify_risk(score: float) -> str:
    """
    Convert a numerical risk score into a risk level.
    """

    if score >= HIGH_RISK_THRESHOLD:
        return "HIGH"

    if score >= LOW_RISK_THRESHOLD:
        return "MEDIUM"

    return "LOW"