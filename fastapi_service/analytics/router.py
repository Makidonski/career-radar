"""Analytics endpoints: median/average salary, top skills, weekly demand trend.

Pulls raw rows via SQLAlchemy and does the aggregation in pandas rather than
in SQL, since it's the same stack used for forecasting and keeps the
aggregation logic testable/readable in one place.
"""
from datetime import datetime

import pandas as pd
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Vacancy
from ..schemas import DemandTrendPoint, SalaryStats, SkillFrequency

router = APIRouter(prefix="/analytics", tags=["analytics"])


def _vacancies_dataframe(db: Session, city: str | None, skill: str | None) -> pd.DataFrame:
    stmt = select(Vacancy)
    rows = db.execute(stmt).scalars().all()

    records = []
    for v in rows:
        skill_names = [s.name for s in v.skills]
        if skill and skill.lower() not in [s.lower() for s in skill_names]:
            continue
        if city and (v.city or "").lower() != city.lower():
            continue
        records.append({
            "id": v.id,
            "city": v.city,
            "salary_from": v.salary_from,
            "salary_to": v.salary_to,
            "published_at": v.published_at,
            "skills": skill_names,
        })

    return pd.DataFrame.from_records(records)


@router.get("/salary", response_model=SalaryStats)
def salary_stats(
    city: str | None = Query(default=None),
    skill: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    """Median/average salary for a given stack (skill) and/or city."""
    df = _vacancies_dataframe(db, city, skill)
    if df.empty:
        return SalaryStats(city=city, skill=skill, median_salary=None,
                            average_salary=None, sample_size=0)

    # Use the midpoint of (salary_from, salary_to) as the representative salary
    df["salary_point"] = df[["salary_from", "salary_to"]].mean(axis=1, skipna=True)
    df = df.dropna(subset=["salary_point"])

    return SalaryStats(
        city=city,
        skill=skill,
        median_salary=float(df["salary_point"].median()) if not df.empty else None,
        average_salary=float(df["salary_point"].mean()) if not df.empty else None,
        sample_size=len(df),
    )


@router.get("/top-skills", response_model=list[SkillFrequency])
def top_skills(
    position: str | None = Query(default=None, description="Filter by desired position/title"),
    limit: int = Query(default=10, le=50),
    db: Session = Depends(get_db),
):
    """Top-N skills co-occurring with a given position, as % of matching vacancies."""
    stmt = select(Vacancy)
    rows = db.execute(stmt).scalars().all()

    if position:
        rows = [v for v in rows if position.lower() in (v.title or "").lower()]

    total = len(rows)
    if total == 0:
        return []

    counts: dict[str, int] = {}
    for v in rows:
        for s in v.skills:
            counts[s.name] = counts.get(s.name, 0) + 1

    ranked = sorted(counts.items(), key=lambda kv: kv[1], reverse=True)[:limit]
    return [
        SkillFrequency(skill=name, vacancy_count=count, percent_of_total=round(100 * count / total, 1))
        for name, count in ranked
    ]


@router.get("/demand-trend", response_model=list[DemandTrendPoint])
def demand_trend(
    city: str | None = Query(default=None),
    skill: str | None = Query(default=None),
    weeks: int = Query(default=12, le=52),
    db: Session = Depends(get_db),
):
    """Weekly count of matching vacancies over the last N weeks."""
    df = _vacancies_dataframe(db, city, skill)
    if df.empty:
        return []

    df["published_at"] = pd.to_datetime(df["published_at"], errors="coerce", utc=True)
    df = df.dropna(subset=["published_at"])
    if df.empty:
        return []

    df["week_start"] = df["published_at"].dt.to_period("W").dt.start_time
    weekly = df.groupby("week_start").size().sort_index()
    weekly = weekly.tail(weeks)

    return [
        DemandTrendPoint(week_start=week.strftime("%Y-%m-%d"), vacancy_count=int(count))
        for week, count in weekly.items()
    ]
