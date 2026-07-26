"""SQLAlchemy engine/session setup for the FastAPI analytics service.

Reads the same PostgreSQL database Django writes to (schema owned by
Django migrations); this service is read-mostly and only reflects existing
tables rather than managing its own migrations.
"""
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

DATABASE_URL = (
    f"postgresql+psycopg2://{os.environ.get('POSTGRES_USER', 'career_radar')}:"
    f"{os.environ.get('POSTGRES_PASSWORD', 'career_radar')}@"
    f"{os.environ.get('POSTGRES_HOST', 'localhost')}:"
    f"{os.environ.get('POSTGRES_PORT', '5432')}/"
    f"{os.environ.get('POSTGRES_DB', 'career_radar')}"
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
