from decimal import Decimal


def clamp_score(score: float) -> float:
    """
    Keep a risk score within the valid range [0.0, 1.0].
    """
    return max(0.0, min(1.0, score))


def amount_score(amount: Decimal) -> float:
    """
    Calculate a risk contribution based on transaction amount.

    Higher-value transactions receive a higher score.
    Amount alone should never determine whether a transaction
    is fraudulent.
    """

    amount = float(amount)

    if amount < 5000:
        return 0.0

    if amount < 10000:
        return 0.15

    if amount < 25000:
        return 0.30

    if amount < 50000:
        return 0.50

    return 0.70


def chargeback_score(chargeback: bool) -> float:
    """
    Chargebacks are a strong risk signal.
    """

    if chargeback:
        return 0.80

    return 0.0


def refund_score(refund_status: str | None) -> float:
    """
    Calculate a small risk contribution based on refund status.

    A refund is not automatically fraudulent, so this signal
    receives a relatively low weight.
    """

    if refund_status is None:
        return 0.0

    status = refund_status.upper()

    if status == "REFUNDED":
        return 0.20

    if status == "REQUESTED":
        return 0.10

    return 0.0


def status_score(status: str) -> float:
    """
    Calculate a small risk contribution based on transaction status.
    """

    status = status.upper()

    if status == "FAILED":
        return 0.10

    if status == "PENDING":
        return 0.05

    return 0.0


def calculate_behavior_score(transaction) -> dict:
    """
    Calculate the behavioral risk score for a transaction.

    The final behavioral score is a weighted combination of:
        - transaction amount
        - chargeback status
        - refund status
        - transaction status
    """

    amount = amount_score(transaction.amount)
    chargeback = chargeback_score(transaction.chargeback)
    refund = refund_score(transaction.refund_status)
    status = status_score(transaction.status)

    # -----------------------------------------------------
    # Weighted behavioral score
    # -----------------------------------------------------

    score = (
        amount * 0.25
        + chargeback * 0.50
        + refund * 0.15
        + status * 0.10
    )

    score = clamp_score(score)

    # -----------------------------------------------------
    # Risk classification
    # -----------------------------------------------------

    if score >= 0.70:
        risk_level = "HIGH"
    elif score >= 0.40:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    return {
        "transaction_id": transaction.id,
        "behavior_score": round(score, 4),
        "risk_level": risk_level,
        "signals": {
            "amount_score": round(amount, 4),
            "chargeback_score": round(chargeback, 4),
            "refund_score": round(refund, 4),
            "status_score": round(status, 4),
        },
    }