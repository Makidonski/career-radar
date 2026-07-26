
from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from api_client import client

router = Router(name="start")


class LinkAccount(StatesGroup):
    waiting_for_username = State()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    existing = await client.get_user_by_chat_id(message.chat.id)
    if existing:
        await message.answer(
            f"С возвращением, {existing['username']}! 👋\n\n"
            "Доступные команды:\n"
            "/digest — подборка новых подходящих вакансий\n"
            "/stats — недельная сводка по рынку\n"
            "/alerts — настроить кастомные алерты"
        )
        return

    await message.answer(
        "Привет! Я CareerRadar bot 📡\n\n"
        "Чтобы связать Telegram с вашим аккаунтом, отправьте ваш логин "
        "с сайта CareerRadar."
    )
    await state.set_state(LinkAccount.waiting_for_username)


@router.message(LinkAccount.waiting_for_username)
async def process_username(message: Message, state: FSMContext):
    username = message.text.strip()
    result = await client.link_telegram(
        username=username,
        chat_id=message.chat.id,
        telegram_username=message.from_user.username or "",
    )
    if result is None:
        await message.answer(
            "Не нашёл такой аккаунт 😕 Проверьте логин и попробуйте снова, "
            "либо зарегистрируйтесь на сайте CareerRadar."
        )
        return

    await state.clear()
    await message.answer(
        f"Готово! Аккаунт {result['username']} привязан к этому чату ✅\n\n"
        "/digest — подборка новых подходящих вакансий\n"
        "/stats — недельная сводка по рынку\n"
        "/alerts — настроить кастомные алерты"
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "/start — привязать аккаунт\n"
        "/digest — подборка вакансий\n"
        "/stats — сводка по рынку за неделю\n"
        "/alerts — список и создание алертов"
    )
