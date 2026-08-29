from fastapi import APIRouter

from app.api.v1.transactions import router as transactions_router


router = APIRouter()


# =========================================================
# API Routes
# =========================================================

router.include_router(
    transactions_router
)