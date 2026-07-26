import os

from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
DJANGO_INTERNAL_API_URL = os.environ.get("DJANGO_INTERNAL_API_URL", "http://django:8000/api")
FASTAPI_INTERNAL_URL = os.environ.get("FASTAPI_INTERNAL_URL", "http://fastapi:8001")
INTERNAL_SHARED_SECRET = os.environ.get("INTERNAL_SHARED_SECRET", "dev-secret-change-me")
