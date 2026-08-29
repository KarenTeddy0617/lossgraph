
from fastapi import APIRouter
from pathlib import Path
import json


router = APIRouter(
    prefix="/evaluation",
    tags=["Evaluation"],
)


# =========================================================
# Get ML evaluation results
# =========================================================

@router.get("/")
def get_evaluation():
    """
    Return the latest ML model evaluation results.
    """

    evaluation_path = (
        Path(__file__).resolve().parents[2]
        / "ml"
        / "saved"
        / "evaluation.json"
    )

    if not evaluation_path.exists():
        return {
            "status": "not_available",
            "message": (
                "No evaluation results found. "
                "Run the ML training pipeline first."
            ),
        }

    with open(
        evaluation_path,
        "r",
        encoding="utf-8",
    ) as file:
        evaluation = json.load(file)

    return {
        "status": "success",
        "evaluation": evaluation,
    }

