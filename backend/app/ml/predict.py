from app.ml.features import (
    transaction_to_features,
    FEATURE_NAMES,
)

from app.ml.model import (
    load_model,
)

from app.graph.features import (
    calculate_all_graph_features,
)


# =========================================================
# Predict transaction risk
# =========================================================

def predict_transaction(
    db,
    transaction,
):
    """
    Predict ML fraud probability for one transaction.

    Returns:
        float between 0 and 1
    """

    # -------------------------------------------------------
    # Make sure the transaction is visible to the DB queries
    # graph-feature calculation relies on.
    #
    # The app's session is configured with autoflush=False, so
    # a transaction that was just built and added to the
    # session (e.g. during webhook ingestion) but not yet
    # committed is NOT visible to a plain db.query(...).all().
    # Without this flush, that case fails with a raw
    # `KeyError: None` below instead of a usable result.
    # -------------------------------------------------------

    db.flush()

    model = load_model()

    # -----------------------------------------------------
    # Calculate graph features.
    #
    # calculate_all_graph_features() always builds its shared
    # device/IP/address/payment indexes from the FULL
    # transactions table internally - the `transactions`
    # argument only controls which transactions get an entry
    # in the returned dict. So we only need to ask for this
    # one transaction's features, not requery and pass in the
    # entire table.
    # -----------------------------------------------------

    all_graph_features = calculate_all_graph_features(
        db,
        [transaction],
    )

    graph_features = all_graph_features.get(
        transaction.id
    )

    if graph_features is None:
        raise ValueError(
            f"Could not calculate graph features for transaction "
            f"{getattr(transaction, 'transaction_code', transaction.id)!r}."
        )

    # -----------------------------------------------------
    # Build feature vector
    # -----------------------------------------------------

    features = transaction_to_features(
        transaction,
        graph_features,
    )

    X = [
        [
            features[name]
            for name in FEATURE_NAMES
        ]
    ]

    # -----------------------------------------------------
    # Probability of abuse
    # -----------------------------------------------------

    probability = model.predict_proba(
        X
    )[0][1]

    return round(
        float(probability),
        4,
    )