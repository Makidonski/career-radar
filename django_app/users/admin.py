from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ["username", "email", "desired_position", "city", "min_salary", "telegram_username"]
    fieldsets = BaseUserAdmin.fieldsets + (
        ("CareerRadar profile", {
            "fields": ("desired_position", "city", "min_salary", "skills",
                       "telegram_chat_id", "telegram_username"),
        }),
    )
