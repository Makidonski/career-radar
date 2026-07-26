FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

COPY telegram_bot/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY telegram_bot /app

CMD ["python", "bot.py"]
