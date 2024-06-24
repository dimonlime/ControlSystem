import asyncio

from aiogram import Bot, Dispatcher
import os
import dotenv
import sys
import logging
from app.handlers import (handlers, create_order, view_orders, add_product_card, view_product_card, remove_product_card,
                          create_shipment, create_cheque, create_fish, archive_orders, change_shipment_status, view_shipment,
                          cheques, article_info, edit_data)
from app.database.models import async_main
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.utils.time_update import fire_cheques_check
from odds.app import handlers_odds

# asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

dp = Dispatcher()


async def main():
    await async_main()
    dp.include_routers(handlers.router, create_order.router, view_orders.router, add_product_card.router,
                       view_product_card.router, remove_product_card.router, create_shipment.router, create_cheque.router,
                       create_fish.router, archive_orders.router, change_shipment_status.router, view_shipment.router,
                       cheques.router, article_info.router, edit_data.router, handlers_odds.router)
    dotenv.load_dotenv()
    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    scheduler.add_job(fire_cheques_check, "interval", days=1)
    scheduler.start()
    bot = Bot(token=os.getenv('TOKEN'))
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот выключен")
