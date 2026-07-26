FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
        libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

COPY fastapi_service/requirements.txt /app/fastapi_service/requirements.txt
RUN pip install --no-cache-dir -r fastapi_service/requirements.txt

COPY fastapi_service /app/fastapi_service

EXPOSE 8001

CMD ["uvicorn", "fastapi_service.main:app", "--host", "0.0.0.0", "--port", "8001"]
