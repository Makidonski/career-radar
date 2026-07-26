
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from api_client import client

router = Router(name="stats")


@router.message(Command("stats"))
async def cmd_stats(message: Message):
    user = await client.get_user_by_chat_id(message.chat.id)
    if user is None:
        await message.answer("Сначала привяжите аккаунт командой /start.")
        return

    city = user.get("city") or None
    skill = (user.get("skills") or [None])[0] if user.get("skills") else None

    salary = await client.get_salary_stats(city=city, skill=skill)
    trend = await client.get_demand_trend(city=city, skill=skill, weeks=4)

    lines = ["📊 Сводка за последние недели:\n"]

    if salary and salary.get("sample_size"):
        lines.append(
            f"Медианная ЗП{f' ({skill})' if skill else ''}"
            f"{f', {city}' if city else ''}: {salary['median_salary']:.0f} ₽"
            f" (по {salary['sample_size']} вакансиям)"
        )
    else:
        lines.append("Недостаточно данных по зарплатам для вашего профиля.")

    if len(trend) >= 2:
        first, last = trend[0]["vacancy_count"], trend[-1]["vacancy_count"]
        delta = last - first
        arrow = "📈" if delta > 0 else "📉" if delta < 0 else "➡️"
        lines.append(f"Число вакансий за период: {first} → {last} {arrow}")
    else:
        lines.append("Недостаточно данных для тренда спроса.")

    await message.answer("\n".join(lines))
