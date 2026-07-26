"""hh.ru API client: fetches vacancy search results with retry + rate-limit
handling. Kept dependency-free from Django models so it's independently
testable and reusable from FastAPI if needed.
"""
import logging
import time
from dataclasses import dataclass
from typing import Any, Iterator

import requests

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 10
MAX_RETRIES = 3
RETRY_BACKOFF_SECONDS = 2


@dataclass
class HHSearchParams:
    text: str = ""
    area: int | None = None  # hh.ru numeric region id, e.g. 1 = Moscow
    salary: int | None = None
    per_page: int = 50
    page: int = 0


class HHParserError(Exception):
    """Raised when the hh.ru API cannot be reached after retries."""


class HHClient:
    def __init__(self, base_url: str, user_agent: str):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": user_agent})

    def _get(self, path: str, params: dict[str, Any]) -> dict:
        url = f"{self.base_url}{path}"
        last_error: Exception | None = None

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                response = self.session.get(url, params=params, timeout=DEFAULT_TIMEOUT)
                if response.status_code == 429:
                    # hh.ru rate limit hit - back off and retry
                    wait = RETRY_BACKOFF_SECONDS * attempt
                    logger.warning("hh.ru rate limit (429), retrying in %ss", wait)
                    time.sleep(wait)
                    continue
                response.raise_for_status()
                return response.json()
            except requests.RequestException as exc:
                last_error = exc
                logger.warning("hh.ru request failed (attempt %s/%s): %s",
                               attempt, MAX_RETRIES, exc)
                time.sleep(RETRY_BACKOFF_SECONDS * attempt)

        raise HHParserError(f"Failed to fetch {url} after {MAX_RETRIES} attempts") from last_error

    def search_vacancies(self, params: HHSearchParams) -> Iterator[dict]:
        """Yields raw vacancy dicts from hh.ru's /vacancies endpoint,
        transparently paging until results are exhausted."""
        page = params.page
        while True:
            query = {
                "text": params.text,
                "area": params.area,
                "salary": params.salary,
                "per_page": params.per_page,
                "page": page,
            }
            query = {k: v for k, v in query.items() if v not in (None, "")}
            data = self._get("/vacancies", query)

            items = data.get("items", [])
            if not items:
                return

            yield from items

            if page + 1 >= data.get("pages", 0):
                return
            page += 1

    def get_vacancy_details(self, vacancy_id: str) -> dict:
        """Fetch full vacancy detail (used to get the full description,
        which the search endpoint truncates/omits)."""
        return self._get(f"/vacancies/{vacancy_id}", {})
