
from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from api_client import client

router = Router(name="alerts")


@router.message(Command("alerts"))
async def cmd_alerts(message: Message):
    user = await client.get_user_by_chat_id(message.chat.id)
    if user is None:
        await message.answer("Сначала привяжите аккаунт командой /start.")
        return

    alerts = await client.list_alerts(message.chat.id)
    if not alerts:
        await message.answer(
            "У вас пока нет алертов.\n\n"
            "Создать: /newalert <навык> <город> <мин.зарплата>\n"
            "Например: /newalert Python Москва 150000\n"
            "Используйте «-» чтобы пропустить поле."
        )
        return

    lines = ["🔔 Ваши алерты:\n"]
    for a in alerts:
        lines.append(
            f"#{a['id']}: навык={a['skill'] or '-'}, город={a['city'] or '-'}, "
            f"мин. ЗП={a['min_salary'] or '-'}, активен={'да' if a['is_active'] else 'нет'}"
        )
    await message.answer("\n".join(lines))


@router.message(Command("newalert"))
async def cmd_new_alert(message: Message, command: CommandObject):
    user = await client.get_user_by_chat_id(message.chat.id)
    if user is None:
        await message.answer("Сначала привяжите аккаунт командой /start.")
        return

    if not command.args:
        await message.answer("Формат: /newalert <навык> <город> <мин.зарплата>")
        return

    parts = command.args.split()
    skill = parts[0] if len(parts) > 0 and parts[0] != "-" else ""
    city = parts[1] if len(parts) > 1 and parts[1] != "-" else ""
    min_salary = None
    if len(parts) > 2 and parts[2] != "-":
        try:
            min_salary = int(parts[2])
        except ValueError:
            await message.answer("Минимальная зарплата должна быть числом.")
            return

    result = await client.create_alert(message.chat.id, skill=skill, city=city, min_salary=min_salary)
    if result is None:
        await message.answer("Не получилось создать алерт, попробуйте ещё раз.")
        return

    await message.answer(f"Алерт #{result['id']} создан ✅")
