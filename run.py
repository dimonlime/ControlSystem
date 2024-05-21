import asyncio

from aiogram import Bot, Dispatcher
import os
import dotenv
import sys
import logging
from app.handlers import (handlers, edit_order, change_status, fact_data, create_fish, checking_cheques, create_order,
                          pay_cheques, view_orders, article_info, change_status_ru, add_product_card, view_product_card,
                          remove_product_card)
from app.database.models import async_main
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.utils.time_update import fire_cheques_check

# asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

dp = Dispatcher()


async def main():
    await async_main()
    dp.include_routers(handlers.router, edit_order.router, change_status.router, fact_data.router,
                       create_fish.router, checking_cheques.router, create_order.router, pay_cheques.router,
                       view_orders.router, article_info.router, change_status_ru.router, add_product_card.router,
                       view_product_card.router, remove_product_card.router)
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
