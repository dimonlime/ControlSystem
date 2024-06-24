import asyncio
import logging
import sys

from aiogram import Dispatcher, Bot
import dotenv
import os

from odds.app.handlers_odds import router

dotenv.load_dotenv()
bot = Bot(token=os.getenv('BOT_TOKEN'))
dp = Dispatcher()


async def main():
    dp.include_router(router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
