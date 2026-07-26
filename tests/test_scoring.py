import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi_service.scoring.router import compute_match_score  # noqa: E402


class TestComputeMatchScore:
    def test_perfect_match(self):
        result = compute_match_score(
            user_skills=["Python", "Django", "SQL"],
            vacancy_skills=["Python", "Django"],
            user_min_salary=100000,
            vacancy_salary_from=120000,
            vacancy_salary_to=150000,
            user_city="Москва",
            vacancy_city="Москва",
        )
        assert result["score"] == 100.0
        assert set(result["skill_overlap"]) == {"python", "django"}
        assert result["salary_match"] is True
        assert result["city_match"] is True

    def test_no_skill_overlap(self):
        result = compute_match_score(
            user_skills=["Java"],
            vacancy_skills=["Python", "Django"],
            user_min_salary=None,
            vacancy_salary_from=None,
            vacancy_salary_to=None,
            user_city=None,
            vacancy_city=None,
        )
        assert result["skill_overlap"] == []
        # skill component is 0, but salary/city default to "match" when unknown
        assert result["score"] == 40.0  # SALARY_WEIGHT(0.25) + CITY_WEIGHT(0.15) = 0.4 -> 40%

    def test_salary_below_expectation(self):
        result = compute_match_score(
            user_skills=["Python"],
            vacancy_skills=["Python"],
            user_min_salary=200000,
            vacancy_salary_from=100000,
            vacancy_salary_to=120000,
            user_city=None,
            vacancy_city=None,
        )
        assert result["salary_match"] is False
        assert result["score"] < 100.0

    def test_city_mismatch_reduces_score(self):
        matching_city = compute_match_score(
            user_skills=["Python"], vacancy_skills=["Python"],
            user_min_salary=None, vacancy_salary_from=None, vacancy_salary_to=None,
            user_city="Москва", vacancy_city="Москва",
        )
        mismatched_city = compute_match_score(
            user_skills=["Python"], vacancy_skills=["Python"],
            user_min_salary=None, vacancy_salary_from=None, vacancy_salary_to=None,
            user_city="Москва", vacancy_city="Казань",
        )
        assert mismatched_city["city_match"] is False
        assert mismatched_city["score"] < matching_city["score"]

    def test_case_insensitive_skill_matching(self):
        result = compute_match_score(
            user_skills=["python", "DJANGO"],
            vacancy_skills=["Python", "Django"],
            user_min_salary=None,
            vacancy_salary_from=None,
            vacancy_salary_to=None,
            user_city=None,
            vacancy_city=None,
        )
        assert len(result["skill_overlap"]) == 2
