"""Custom user model for CareerRadar.

We extend AbstractUser instead of using a separate Profile model so that
DRF TokenAuthentication, admin, and permissions all work against a single
first-class user record. Job-seeker specific fields (desired position,
city, skills, salary floor, telegram link) live directly on the user.
"""
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Job seeker account.

    Assumption: one CareerRadar account maps to one hh.ru job search profile
    and (optionally) one linked Telegram chat.
    """

    desired_position = models.CharField(
        max_length=255, blank=True, help_text="e.g. 'Python developer'"
    )
    city = models.CharField(max_length=120, blank=True)
    min_salary = models.PositiveIntegerField(
        null=True, blank=True, help_text="Minimum acceptable net salary, in RUB"
    )
    skills = models.JSONField(
        default=list, blank=True, help_text="List of skill strings, e.g. ['Django', 'SQL']"
    )

    telegram_chat_id = models.BigIntegerField(
        null=True, blank=True, unique=True, db_index=True,
        help_text="Populated once the user links their Telegram account via /start",
    )
    telegram_username = models.CharField(max_length=64, blank=True)

    def __str__(self):
        return self.username
