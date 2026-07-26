"""Shared-secret permission for internal service-to-service calls.

The Telegram bot and the FastAPI analytics service both need to reach a
handful of trusted internal endpoints (e.g. resolving a user by
telegram_chat_id, or creating an alert on the user's behalf) without going
through per-user TokenAuthentication. They authenticate with a static
shared secret sent in the X-Internal-Secret header instead.

This is intentionally simple (a single shared secret, not per-service
credentials) since all callers run inside the same docker-compose network
and the secret never reaches the public frontend.
"""
from django.conf import settings
from rest_framework.permissions import BasePermission


class InternalServicePermission(BasePermission):
    """Grants access only to requests carrying the correct internal secret."""

    message = "Invalid or missing internal service secret."

    def has_permission(self, request, view):
        provided = request.headers.get("X-Internal-Secret", "")
        return bool(settings.INTERNAL_SHARED_SECRET) and provided == settings.INTERNAL_SHARED_SECRET
