"""Celery tasks that:
1. Periodically pull vacancies from every active ParsingSource (hh.ru today).
2. Evaluate active user Alerts against newly collected vacancies and push
   Telegram notifications directly via the Bot API (no round-trip through
   the telegram_bot service - it's a fire-and-forget HTTP call, simplest
   thing that works for a scheduled background job).
"""
import logging
from datetime import datetime, timezone

import requests
from celery import shared_task
from django.conf import settings
from django.utils.dateparse import parse_datetime

from .hh_parser import HHClient, HHSearchParams, HHParserError
from .normalizer import normalize_api_salary

logger = logging.getLogger(__name__)

TELEGRAM_API_BASE = "https://api.telegram.org"


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def collect_vacancies_for_source(self, source_id: int):

    from vacancies.models import ParsingSource, Skill, Vacancy

    try:
        source = ParsingSource.objects.get(pk=source_id, is_active=True)
    except ParsingSource.DoesNotExist:
        logger.info("ParsingSource %s not found or inactive, skipping", source_id)
        return {"source_id": source_id, "collected": 0}

    client = HHClient(base_url=settings.HH_API_BASE_URL, user_agent=settings.HH_USER_AGENT)
    params = HHSearchParams(
        text=source.default_params.get("text", ""),
        area=source.default_params.get("area"),
        salary=source.default_params.get("salary"),
    )

    collected = 0
    try:
        for raw in client.search_vacancies(params):
            normalized_salary = normalize_api_salary(raw.get("salary"))
            published_at = parse_datetime(raw.get("published_at", "")) if raw.get("published_at") else None

            vacancy, _created = Vacancy.objects.update_or_create(
    source=source,
    external_id=str(raw["id"]),
    defaults={
        "title": raw.get("name", ""),
        "company_name": (raw.get("employer") or {}).get("name", ""),
        "city": (raw.get("area") or {}).get("name", ""),
        "url": raw.get("alternate_url", ""),
        "description": raw.get("snippet", {}).get("responsibility") or "",
        "salary_from": normalized_salary.salary_from,
        "salary_to": normalized_salary.salary_to,
        "salary_currency": normalized_salary.currency,
        "salary_basis": normalized_salary.basis,
        "published_at": published_at,
        "work_schedule": (raw.get("schedule") or {}).get("id"),
        "employment_type": (raw.get("employment") or {}).get("id"),
    },
)

            skill_names = [s["name"] for s in raw.get("key_skills", [])] if raw.get("key_skills") else []
            if skill_names:
                skill_objs = [Skill.objects.get_or_create(name=name)[0] for name in skill_names]
                vacancy.skills.set(skill_objs)

            collected += 1
    except HHParserError as exc:
        logger.error("hh.ru collection failed for source %s: %s", source.name, exc)
        raise self.retry(exc=exc)

    logger.info("Collected %s vacancies for source %s", collected, source.name)
    return {"source_id": source_id, "collected": collected}


@shared_task
def collect_all_sources():
    """Celery Beat entry point (scheduled hourly): fan out one task per
    active ParsingSource so a slow/failing source doesn't block others."""
    from vacancies.models import ParsingSource

    source_ids = list(ParsingSource.objects.filter(is_active=True).values_list("id", flat=True))
    for source_id in source_ids:
        collect_vacancies_for_source.delay(source_id)
    return {"sources_queued": len(source_ids)}


def _send_telegram_message(chat_id: int, text: str) -> None:
    if not settings.TELEGRAM_BOT_TOKEN:
        logger.warning("TELEGRAM_BOT_TOKEN not configured, skipping notification")
        return
    url = f"{TELEGRAM_API_BASE}/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"}, timeout=10)
    except requests.RequestException:
        logger.exception("Failed to deliver Telegram alert to chat %s", chat_id)


@shared_task
def send_alert_notifications():
    """Celery Beat entry point: check active Alerts against vacancies
    collected since the alert last triggered, and notify via Telegram."""
    from vacancies.models import Alert, Vacancy

    alerts = Alert.objects.filter(is_active=True, user__telegram_chat_id__isnull=False)
    notified = 0

    for alert in alerts:
        qs = Vacancy.objects.all()
        if alert.skill:
            qs = qs.filter(skills__name__iexact=alert.skill)
        if alert.city:
            qs = qs.filter(city__iexact=alert.city)
        if alert.min_salary:
            qs = qs.filter(salary_from__gte=alert.min_salary)
        if alert.last_triggered_at:
            qs = qs.filter(collected_at__gt=alert.last_triggered_at)

        matches = list(qs.order_by("-collected_at")[:5])
        if not matches:
            continue

        lines = [f"🔔 Новые вакансии по вашему алерту ({alert.skill or 'любой навык'}):"]
        for vacancy in matches:
            lines.append(f"• <a href='{vacancy.url}'>{vacancy.title}</a> — {vacancy.company_name}")
        _send_telegram_message(alert.user.telegram_chat_id, "\n".join(lines))

        alert.last_triggered_at = datetime.now(timezone.utc)
        alert.save(update_fields=["last_triggered_at"])
        notified += 1

    return {"alerts_notified": notified}
