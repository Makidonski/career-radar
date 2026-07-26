"""SQLAlchemy Core/ORM models mirroring tables that Django's migrations own.

This service never runs its own migrations - table names/columns here must
stay in sync with django_app/vacancies/models.py and django_app/users/models.py.
Kept intentionally minimal: only the columns analytics/forecasting/scoring
actually read.
"""
from sqlalchemy import Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship

from .database import Base

vacancy_skills = Table(
    "vacancies_vacancy_skills",
    Base.metadata,
    Column("id", Integer, primary_key=True),
    Column("vacancy_id", Integer, ForeignKey("vacancies_vacancy.id")),
    Column("skill_id", Integer, ForeignKey("vacancies_skill.id")),
)


class Skill(Base):
    __tablename__ = "vacancies_skill"

    id = Column(Integer, primary_key=True)
    name = Column(String)


class Vacancy(Base):
    __tablename__ = "vacancies_vacancy"

    id = Column(Integer, primary_key=True)
    title = Column(String)
    company_name = Column(String)
    city = Column(String)
    salary_from = Column(Integer, nullable=True)
    salary_to = Column(Integer, nullable=True)
    salary_currency = Column(String)
    salary_basis = Column(String)
    published_at = Column("published_at", String)  # read as text; parsed in pandas

    skills = relationship("Skill", secondary=vacancy_skills)


class User(Base):
    __tablename__ = "users_user"

    id = Column(Integer, primary_key=True)
    username = Column(String)
    desired_position = Column(String)
    city = Column(String)
    min_salary = Column(Integer, nullable=True)
    skills = Column("skills", String)  # JSONField stored as text/jsonb
