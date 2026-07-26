from pydantic import BaseModel


class SalaryStats(BaseModel):
    city: str | None = None
    skill: str | None = None
    median_salary: float | None = None
    average_salary: float | None = None
    sample_size: int


class SkillFrequency(BaseModel):
    skill: str
    vacancy_count: int
    percent_of_total: float


class DemandTrendPoint(BaseModel):
    week_start: str
    vacancy_count: int


class DemandForecast(BaseModel):
    filters: dict
    next_week_estimate: float
    method: str
    history_weeks_used: int


class ScoringRequest(BaseModel):
    vacancy_id: int
    user_id: int


class ScoringResult(BaseModel):
    vacancy_id: int
    user_id: int
    score: float
    skill_overlap: list[str]
    salary_match: bool
    city_match: bool
