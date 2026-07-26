"""Scores a vacancy's relevance to a user profile: skill overlap, salary
expectation match, and city match, combined into one 0-100 score.

The scoring math (`compute_match_score`) is a pure function with no DB or
FastAPI dependency, deliberately extracted from the endpoint so it can be
unit tested directly (see tests/test_scoring.py) without a database.
"""
import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User, Vacancy
from ..schemas import ScoringResult

router = APIRouter(prefix="/scoring", tags=["scoring"])

# Weights: skill overlap matters most, then salary fit, then location
SKILL_WEIGHT = 0.6
SALARY_WEIGHT = 0.25
CITY_WEIGHT = 0.15


def compute_match_score(
    user_skills: list[str],
    vacancy_skills: list[str],
    user_min_salary: int | None,
    vacancy_salary_from: int | None,
    vacancy_salary_to: int | None,
    user_city: str | None,
    vacancy_city: str | None,
) -> dict:
    """Pure scoring function - no I/O, safe to unit test directly.

    Returns a dict with the overall score (0-100), the overlapping skills,
    and boolean flags for salary/city match.
    """
    user_skills_lower = {s.lower() for s in user_skills}
    vacancy_skills_lower = {s.lower() for s in vacancy_skills}
    overlap = sorted(user_skills_lower & vacancy_skills_lower)

    if vacancy_skills_lower:
        skill_ratio = len(overlap) / len(vacancy_skills_lower)
    else:
        skill_ratio = 0.0

    vacancy_salary = vacancy_salary_to or vacancy_salary_from
    if user_min_salary is None or vacancy_salary is None:
        salary_match = True  # not enough info to penalize
        salary_ratio = 1.0
    else:
        salary_match = vacancy_salary >= user_min_salary
        salary_ratio = 1.0 if salary_match else max(vacancy_salary / user_min_salary, 0.0)

    if not user_city or not vacancy_city:
        city_match = True  # no location preference stated
        city_ratio = 1.0
    else:
        city_match = user_city.strip().lower() == vacancy_city.strip().lower()
        city_ratio = 1.0 if city_match else 0.0

    score = 100 * (
        SKILL_WEIGHT * skill_ratio
        + SALARY_WEIGHT * salary_ratio
        + CITY_WEIGHT * city_ratio
    )

    return {
        "score": round(score, 1),
        "skill_overlap": overlap,
        "salary_match": salary_match,
        "city_match": city_match,
    }


@router.get("/match", response_model=ScoringResult)
def score_vacancy(vacancy_id: int, user_id: int, db: Session = Depends(get_db)):
    vacancy = db.get(Vacancy, vacancy_id)
    if vacancy is None:
        raise HTTPException(status_code=404, detail="Vacancy not found")

    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        user_skills = json.loads(user.skills) if user.skills else []
    except (TypeError, ValueError):
        user_skills = []

    result = compute_match_score(
        user_skills=user_skills,
        vacancy_skills=[s.name for s in vacancy.skills],
        user_min_salary=user.min_salary,
        vacancy_salary_from=vacancy.salary_from,
        vacancy_salary_to=vacancy.salary_to,
        user_city=user.city,
        vacancy_city=vacancy.city,
    )

    return ScoringResult(vacancy_id=vacancy_id, user_id=user_id, **result)
