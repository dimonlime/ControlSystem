import asyncio

from aiogram import Bot, Dispatcher
import os
import dotenv
import sys
import logging
from app.handlers import router
from app.database.models import async_main

dp = Dispatcher()


async def main():
    await async_main()
    dp.include_router(router)
    dotenv.load_dotenv()
    bot = Bot(token=os.getenv('TOKEN'))
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот выключен")
