"""Forecasts the number of matching vacancies expected next week.

Uses a simple Holt linear trend model (statsmodels) over the weekly
demand-trend series. Falls back to a naive average when there isn't
enough history for a trend model to be meaningful (< 4 weeks of data).
"""
import pandas as pd
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from statsmodels.tsa.holtwinters import SimpleExpSmoothing

from ..analytics.router import _vacancies_dataframe
from ..database import get_db
from ..schemas import DemandForecast

router = APIRouter(prefix="/forecasting", tags=["forecasting"])

MIN_WEEKS_FOR_MODEL = 4


@router.get("/next-week", response_model=DemandForecast)
def forecast_next_week(
    city: str | None = Query(default=None),
    skill: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    df = _vacancies_dataframe(db, city, skill)
    filters = {"city": city, "skill": skill}

    if df.empty:
        return DemandForecast(filters=filters, next_week_estimate=0.0,
                               method="no_data", history_weeks_used=0)

    df["published_at"] = pd.to_datetime(df["published_at"], errors="coerce", utc=True)
    df = df.dropna(subset=["published_at"])
    if df.empty:
        return DemandForecast(filters=filters, next_week_estimate=0.0,
                               method="no_data", history_weeks_used=0)

    df["week_start"] = df["published_at"].dt.to_period("W").dt.start_time
    weekly = df.groupby("week_start").size().sort_index()

    if len(weekly) < MIN_WEEKS_FOR_MODEL:
        estimate = float(weekly.mean())
        return DemandForecast(filters=filters, next_week_estimate=round(estimate, 1),
                               method="naive_average", history_weeks_used=len(weekly))

    model = SimpleExpSmoothing(weekly.values, initialization_method="estimated").fit()
    forecast = model.forecast(1)[0]
    return DemandForecast(
        filters=filters,
        next_week_estimate=round(max(float(forecast), 0.0), 1),
        method="simple_exponential_smoothing",
        history_weeks_used=len(weekly),
    )
