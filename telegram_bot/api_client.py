
import aiohttp

from config import DJANGO_INTERNAL_API_URL, FASTAPI_INTERNAL_URL, INTERNAL_SHARED_SECRET

INTERNAL_HEADERS = {"X-Internal-Secret": INTERNAL_SHARED_SECRET}


class CareerRadarClient:
    def __init__(self):
        self._session: aiohttp.ClientSession | None = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()

    # --- users ---

    async def link_telegram(self, username: str, chat_id: int, telegram_username: str = "") -> dict | None:
        session = await self._get_session()
        url = f"{DJANGO_INTERNAL_API_URL}/users/internal/telegram-link/"
        payload = {"username": username, "telegram_chat_id": chat_id, "telegram_username": telegram_username}
        async with session.post(url, json=payload, headers=INTERNAL_HEADERS) as resp:
            if resp.status != 200:
                return None
            return await resp.json()

    async def get_user_by_chat_id(self, chat_id: int) -> dict | None:
        session = await self._get_session()
        url = f"{DJANGO_INTERNAL_API_URL}/users/internal/by-chat-id/{chat_id}/"
        async with session.get(url, headers=INTERNAL_HEADERS) as resp:
            if resp.status != 200:
                return None
            return await resp.json()

    # --- alerts (identified by telegram chat_id, no per-user token needed) ---

    async def list_alerts(self, chat_id: int) -> list[dict]:
        session = await self._get_session()
        url = f"{DJANGO_INTERNAL_API_URL}/vacancies/internal/telegram-alerts/"
        async with session.get(url, params={"chat_id": chat_id}, headers=INTERNAL_HEADERS) as resp:
            if resp.status != 200:
                return []
            return await resp.json()

    async def create_alert(self, chat_id: int, skill: str = "", city: str = "",
                            min_salary: int | None = None) -> dict | None:
        session = await self._get_session()
        url = f"{DJANGO_INTERNAL_API_URL}/vacancies/internal/telegram-alerts/"
        payload = {"chat_id": chat_id, "skill": skill, "city": city, "min_salary": min_salary}
        async with session.post(url, json=payload, headers=INTERNAL_HEADERS) as resp:
            if resp.status not in (200, 201):
                return None
            return await resp.json()

    # --- analytics (FastAPI) ---

    async def get_salary_stats(self, city: str | None = None, skill: str | None = None) -> dict | None:
        session = await self._get_session()
        url = f"{FASTAPI_INTERNAL_URL}/analytics/salary"
        params = {k: v for k, v in {"city": city, "skill": skill}.items() if v}
        async with session.get(url, params=params) as resp:
            if resp.status != 200:
                return None
            return await resp.json()

    async def get_demand_trend(self, city: str | None = None, skill: str | None = None,
                                weeks: int = 4) -> list[dict]:
        session = await self._get_session()
        url = f"{FASTAPI_INTERNAL_URL}/analytics/demand-trend"
        params = {k: v for k, v in {"city": city, "skill": skill, "weeks": weeks}.items() if v}
        async with session.get(url, params=params) as resp:
            if resp.status != 200:
                return []
            return await resp.json()

    # --- vacancies (Django) ---

    async def get_digest(self, chat_id: int, limit: int = 5) -> list[dict]:
        session = await self._get_session()
        url = f"{DJANGO_INTERNAL_API_URL}/vacancies/internal/telegram-digest/"
        params = {"chat_id": chat_id, "limit": limit}
        async with session.get(url, params=params, headers=INTERNAL_HEADERS) as resp:
            if resp.status != 200:
                return []
            return await resp.json()


client = CareerRadarClient()
