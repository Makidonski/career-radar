"""Celery application for CareerRadar. Autodiscovers tasks in installed apps
and in the top-level `parser` package (which lives outside django_app but on
PYTHONPATH inside the container, see Dockerfile)."""
import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("career_radar")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
# parser.tasks isn't a Django app, so register it explicitly
app.autodiscover_tasks(["parser"])
