FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app/django_app

RUN apt-get update && apt-get install -y --no-install-recommends \
        libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

COPY django_app/requirements.txt /app/django_app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# django_app itself
COPY django_app /app/django_app
# sibling packages imported by Celery tasks / settings (parser, shared frontend)
COPY parser /app/parser
COPY frontend /app/frontend

EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
