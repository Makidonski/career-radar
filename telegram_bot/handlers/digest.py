
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from api_client import client

router = Router(name="digest")


@router.message(Command("digest"))
async def cmd_digest(message: Message):
    user = await client.get_user_by_chat_id(message.chat.id)
    if user is None:
        await message.answer("Сначала привяжите аккаунт командой /start.")
        return

    vacancies = await client.get_digest(message.chat.id, limit=5)
    if not vacancies:
        await message.answer(
            "Пока нет новых вакансий под ваш профиль 🤷\n"
            "Проверьте, что в профиле указаны желаемая должность/город на сайте."
        )
        return

    lines = ["📬 Ваш дайджест вакансий:\n"]
    for v in vacancies:
        salary = ""
        if v.get("salary_from") or v.get("salary_to"):
            salary = f" | {v.get('salary_from') or '?'}–{v.get('salary_to') or '?'} {v.get('salary_currency', '')}"
        lines.append(f"• <a href='{v['url']}'>{v['title']}</a> — {v['company_name']}{salary}")

    await message.answer("\n".join(lines), parse_mode="HTML", disable_web_page_preview=True)
