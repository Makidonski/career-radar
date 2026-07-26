"""CareerRadar Telegram bot entrypoint (aiogram, long polling)."""
import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from api_client import client
from config import TELEGRAM_BOT_TOKEN
from handlers import alerts, digest, start, stats

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    if not TELEGRAM_BOT_TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not set")

    bot = Bot(token=TELEGRAM_BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    dp.include_router(start.router)
    dp.include_router(digest.router)
    dp.include_router(stats.router)
    dp.include_router(alerts.router)

    try:
        logger.info("Starting CareerRadar bot polling...")
        await dp.start_polling(bot)
    finally:
        await client.close()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
