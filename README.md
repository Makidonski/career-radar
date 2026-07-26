# CareerRadar 📡

Платформа мониторинга и аналитики рынка труда на основе данных hh.ru.
Собирает вакансии, нормализует зарплаты, считает аналитику/прогноз спроса,
скорит вакансии под профиль пользователя и присылает персональные дайджесты
и алерты в Telegram — плюс веб-дашборд и мини-приложение в Telegram.

## Архитектура

```
career-radar/
├── docker-compose.yml        # оркестрация всех сервисов
├── django_app/                # ядро: users, vacancies, dashboard, DRF API
├── fastapi_service/            # аналитика, прогноз, скоринг (FastAPI + Pydantic)
├── parser/                     # hh.ru клиент, нормализация зарплат, Celery-задачи
├── telegram_bot/                # aiogram-бот: /start /digest /stats /alerts
├── frontend/                    # веб-дашборд (HTML/CSS/JS + Chart.js)
├── telegram_miniapp/             # компактный дашборд как Telegram Mini App
├── nginx/                        # reverse proxy: django / fastapi / miniapp
├── postgres/                      # init.sql
└── tests/                          # pytest: нормализация + скоринг
```

Django-ядро и FastAPI-сервис делят одну и ту же PostgreSQL-схему: миграциями
владеет Django, FastAPI читает те же таблицы через SQLAlchemy. Celery worker
и Celery Beat используют Redis как брокер. Telegram-бот и FastAPI обращаются
к внутренним Django-эндпоинтам по общему секрету (`X-Internal-Secret`),
минуя пользовательскую токен-аутентификацию.

## Быстрый старт

```bash
cp .env.example .env
# отредактируйте .env: задайте пароли, TELEGRAM_BOT_TOKEN, INTERNAL_SHARED_SECRET

docker-compose up --build
```

После старта:
- Дашборд: http://localhost/
- Django admin: http://localhost/admin/
- FastAPI docs: http://localhost:8001/docs
- Telegram Mini App (для локальной проверки вёрстки): http://localhost/miniapp/

Первый суперпользователь:
```bash
docker-compose exec django python manage.py createsuperuser
```

Добавить источник парсинга (в Django admin, `ParsingSource`):
- `name`: hh.ru
- `base_url`: https://api.hh.ru
- `default_params`: `{"text": "python developer", "area": 1}`

Celery Beat нужно один раз настроить в admin (`django_celery_beat` уже
подключен): периодические задачи `collect_all_sources` (каждый час) и
`send_alert_notifications` (например, каждые 30 минут).

## Тесты и линтер

```bash
pip install -r django_app/requirements.txt -r fastapi_service/requirements.txt -r telegram_bot/requirements.txt
pip install ruff pytest
ruff check .
pytest
```

CI (`.github/workflows/ci.yml`) прогоняет линтер и тесты на каждый push/PR.

## Что реализовано

-  Парсер hh.ru API с ретраями и обработкой rate limit (429)
-  Нормализация зарплат (API-объекты и свободный текст)
-  Django-ядро: пользователи, вакансии, алерты, история просмотров, admin
-  Celery + Celery Beat: сбор по расписанию, рассылка алертов
-  FastAPI: медианная/средняя ЗП, топ навыков, тренд спроса, прогноз
  (Simple Exponential Smoothing), скоринг вакансий под профиль
-  Telegram-бот: /start (привязка аккаунта), /digest, /stats, /alerts, /newalert
-  Telegram Mini App: компактный мобильный дашборд
-  Веб-дашборд с Chart.js (тренд, зарплаты, навыки, города)
-  Docker Compose, Nginx reverse proxy, GitHub Actions CI, ruff, pytest.


