from fastapi import APIRouter

from app.api.v1.transactions import router as transactions_router
from app.api.v1.clusters import router as clusters_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.evaluation import router as evaluation_router
from app.api.v1.webhooks import router as webhooks_router


router = APIRouter()


router.include_router(
    transactions_router
)

router.include_router(
    clusters_router
)

router.include_router(
    dashboard_router
)

router.include_router(
    evaluation_router
)
router.include_router(
    webhooks_router
)
