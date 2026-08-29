from fastapi import FastAPI

from app.api.v1.router import router as api_router


# =========================================================
# FastAPI Application
# =========================================================

app = FastAPI(
    title="LossGraph API",
    description="Graph-based transaction abuse detection API",
    version="1.0.0",
)


# =========================================================
# API Routes
# =========================================================

app.include_router(
    api_router,
    prefix="/api/v1",
)


# =========================================================
# Health Check
# =========================================================

@app.get("/")
def root():
    return {
        "message": "LossGraph API is running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }