from datetime import datetime, timedelta
from app.database.requests import product_card_request as card_rq
from app.database.requests import order_request as order_rq
from app.database.requests import shipment_request as ship_rq


async def half_year_check(date):
    today_date = datetime.now()
    half_year = today_date - timedelta(days=365 / 2)
    date = datetime.strptime(date, "%d-%m-%Y %H:%M:%S")
    if half_year <= date <= today_date:
        return True
    else:
        return False


async def product_card_exists(internal_article):
    product_cards = await card_rq.get_product_cards()
    for product_card in product_cards:
        if product_card.article == internal_article:
            return True
    return False


async def enough_quantity_order(order_id):
    order = await order_rq.get_order(order_id)
    shipments = await ship_rq.get_shipments(order_id)
    shipment_s = 0
    shipment_m = 0
    shipment_l = 0
    for shipment in shipments:
        shipment_s += shipment.quantity_s
        shipment_m += shipment.quantity_m
        shipment_l += shipment.quantity_l
    if shipment_s >= order.quantity_s and shipment_m >= order.quantity_m and shipment_l >= order.quantity_l:
        return True
    return False


async def shipments_quantity_s(order_id):
    shipments = await ship_rq.get_shipments(order_id)
    shipment_s = 0
    for shipment in shipments:
        shipment_s += shipment.quantity_s
    return shipment_s


async def shipments_quantity_m(order_id):
    shipments = await ship_rq.get_shipments(order_id)
    shipment_m = 0
    for shipment in shipments:
        shipment_m += shipment.quantity_m
    return shipment_m


async def shipments_quantity_l(order_id):
    shipments = await ship_rq.get_shipments(order_id)
    shipment_l = 0
    for shipment in shipments:
        shipment_l += shipment.quantity_l
    return shipment_l


async def shipments_ready(order_id):
    shipments = await ship_rq.get_shipments(order_id)
    if not len(shipments.all()):
        return False
    shipments = await ship_rq.get_shipments(order_id)
    for shipment in shipments:
        if shipment.status != 'Принята на складе WB':
            return False
    return True
