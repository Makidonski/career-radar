"""CareerRadar analytics service entrypoint (FastAPI)."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .analytics.router import router as analytics_router
from .forecasting.router import router as forecasting_router
from .scoring.router import router as scoring_router

app = FastAPI(
    title="CareerRadar Analytics Service",
    description="Salary analytics, demand forecasting, and vacancy scoring for CareerRadar.",
    version="1.0.0",
)

# Dashboard is served from the same origin via Nginx in production, but CORS
# stays permissive for local dev where the frontend may run on a different port.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(analytics_router)
app.include_router(forecasting_router)
app.include_router(scoring_router)


@app.get("/health")
def health():
    return {"status": "ok"}
