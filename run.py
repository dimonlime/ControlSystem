import asyncio

from aiogram import Bot, Dispatcher
import os
import dotenv
import sys
import logging
from app.handlers import router
from app.database.models import async_main
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.time_update import fire_cheques_check
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

dp = Dispatcher()


async def main():
    await async_main()
    dp.include_router(router)
    dotenv.load_dotenv()
    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    scheduler.add_job(fire_cheques_check, "interval", hours=1)
    scheduler.start()
    bot = Bot(token=os.getenv('TOKEN'))
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот выключен")
