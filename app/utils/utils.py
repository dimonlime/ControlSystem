from datetime import datetime, timedelta
from app.database import requests as rq


async def half_year_check(date):
    today_date = datetime.now()
    half_year = today_date - timedelta(days=365 / 2)
    order_date = datetime.strptime(date, "%d-%m-%Y %H:%M:%S")
    if half_year <= order_date <= today_date:
        return True
    else:
        return False


async def half_year_check_cheques(date):
    today_date = datetime.now()
    half_year = today_date - timedelta(days=365 / 2)
    cheque_date = datetime.strptime(date, "%d-%m-%Y %H:%M")
    if half_year <= cheque_date <= today_date:
        return True
    else:
        return False


async def product_card_exists(internal_article):
    product_cards = await rq.get_product_cards()
    for product_card in product_cards:
        if product_card.article == internal_article:
            return True
    return False
