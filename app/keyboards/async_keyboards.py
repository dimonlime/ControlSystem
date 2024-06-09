from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime, timedelta
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app import id_config
from app.database.requests import order_request as order_rq
from app.database.requests import shipment_request as ship_rq
from app.database.requests import product_card_request as card_rq
from app.database.requests import cheque_request as cheque_rq
from app.database.requests import fish_request as fish_rq
from app.utils.utils import half_year_check, enough_quantity_order


async def sending_method():
    keyboard = InlineKeyboardBuilder()
    for method in id_config.sending_method:
        keyboard.add(InlineKeyboardButton(text=method, callback_data=f'method_{method}'))
    return keyboard.adjust(3).as_markup()


async def all_orders():
    keyboard = InlineKeyboardBuilder()
    orders = await order_rq.all_orders()
    for order in orders:
        if await half_year_check(order.create_date) and order.status == 'Заказ не готов':
            keyboard.add(InlineKeyboardButton(
                text=f'АРТ: {order.internal_article} '
                     f'S: {order.quantity_s} '
                     f'M: {order.quantity_m} '
                     f'L: {order.quantity_l}',
                callback_data=f'order_id_{order.id}'))
    return keyboard.adjust(1).as_markup()


async def recipient_orders():
    keyboard = InlineKeyboardBuilder()
    orders = await order_rq.all_orders()
    for order in orders:
        if await half_year_check(order.create_date) and order.status == 'Заказ не готов' and not await enough_quantity_order(order.id):
            keyboard.add(InlineKeyboardButton(
                text=f'АРТ: {order.internal_article} '
                     f'S: {order.quantity_s} '
                     f'M: {order.quantity_m} '
                     f'L: {order.quantity_l}',
                callback_data=f'order_id_{order.id}'))
    return keyboard.adjust(1).as_markup()


async def archive_orders():
    keyboard = InlineKeyboardBuilder()
    orders = await order_rq.all_orders()
    for order in orders:
        if await half_year_check(order.create_date) and order.status == 'Заказ готов':
            keyboard.add(InlineKeyboardButton(
                text=f'АРТ: {order.internal_article} '
                     f'S: {order.quantity_s} '
                     f'M: {order.quantity_m} '
                     f'L: {order.quantity_l}',
                callback_data=f'order_id_{order.id}'))
    return keyboard.adjust(1).as_markup()


async def order_shipments(order_id):
    keyboard = InlineKeyboardBuilder()
    shipments = await ship_rq.get_shipments(order_id)
    for shipment in shipments:
        keyboard.add(InlineKeyboardButton(text=f'S: {shipment.quantity_s} '
                     f'M: {shipment.quantity_m} '
                     f'L: {shipment.quantity_l}', callback_data=f'shipment_id_{shipment.id}'))
    return keyboard.adjust(1).as_markup()


async def change_status_shipments():
    keyboard = InlineKeyboardBuilder()
    shipments = await ship_rq.get_all_shipments()
    for shipment in shipments:
        if shipment.status != 'Принята на складе WB':
            order = await order_rq.get_order(shipment.order_id)
            keyboard.add(InlineKeyboardButton(text=f'Цвет: {order.color} '
                         f'S: {shipment.quantity_s} '
                         f'M: {shipment.quantity_m} '
                         f'L: {shipment.quantity_l}', callback_data=f'shipment_id_{shipment.id}'))
    return keyboard.adjust(1).as_markup()


async def shipment_status():
    keyboard = InlineKeyboardBuilder()
    for status in id_config.shipment_status:
        keyboard.add(InlineKeyboardButton(text=f'{status}', callback_data=f'status_{status}'))
    return keyboard.adjust(1).as_markup()


async def all_product_cards():
    keyboard = InlineKeyboardBuilder()
    articles = await card_rq.get_product_cards()
    for article in articles:
        keyboard.add(InlineKeyboardButton(text=f'Артикул: {article.article}',
                                          callback_data=f'article_{article.article}'))
    return keyboard.adjust(1).as_markup()


async def fire_cheques():
    keyboard = InlineKeyboardBuilder()
    cheques = await cheque_rq.get_fire_cheques()
    for cheque in cheques:
        shipment = await ship_rq.get_shipment(cheque.shipment_id)
        keyboard.add(InlineKeyboardButton(text=f'Цена: {cheque.price}$ S: {shipment.quantity_s} M: {shipment.quantity_m}'
                                               f' L: {shipment.quantity_l}',
                                          callback_data=f'cheque_id_{cheque.id}'))
    return keyboard.adjust(1).as_markup()


async def delay_cheques():
    keyboard = InlineKeyboardBuilder()
    cheques = await cheque_rq.get_delay_cheques()
    for cheque in cheques:
        shipment = await ship_rq.get_shipment(cheque.shipment_id)
        keyboard.add(InlineKeyboardButton(text=f'Цена: {cheque.price}$ S: {shipment.quantity_s} M: {shipment.quantity_m}'
                                               f' L: {shipment.quantity_l}',
                                          callback_data=f'cheque_id_{cheque.id}'))
    return keyboard.adjust(1).as_markup()


async def paid_cheques():
    keyboard = InlineKeyboardBuilder()
    cheques = await cheque_rq.get_paid_cheques()
    for cheque in cheques:
        shipment = await ship_rq.get_shipment(cheque.shipment_id)
        keyboard.add(InlineKeyboardButton(text=f'Цена: {cheque.price}$ S: {shipment.quantity_s} M: {shipment.quantity_m}'
                                               f' L: {shipment.quantity_l}',
                                          callback_data=f'paid_cheque_id_{cheque.id}'))
    return keyboard.adjust(1).as_markup()


async def all_articles():
    keyboard = InlineKeyboardBuilder()
    data = await order_rq.all_orders()
    articles = []
    for order in data:
        if await half_year_check(order.create_date) and order.status != 'Заказ готов':
            if order.internal_article not in articles:
                articles.append(order.internal_article)
    for article in articles:
        keyboard.add(InlineKeyboardButton(text=f'Артикул: {article}',
                                          callback_data=f'article_{article}'))
    return keyboard.adjust(1).as_markup()


async def all_shipments():
    keyboard = InlineKeyboardBuilder()
    shipments = await ship_rq.get_all_shipments()
    for shipment in shipments:
        if await half_year_check(shipment.create_date) and shipment.status != 'Принята на складе WB':
            date = datetime.strptime(shipment.create_date, '%d-%m-%Y %H:%M:%S')
            str_date = datetime.strftime(date, '%d-%m-%Y')
            keyboard.add(InlineKeyboardButton(text=f'Дата {str_date} '
                                                   f'S: {shipment.quantity_s} '
                                                   f'M: {shipment.quantity_m} '
                                                   f'L: {shipment.quantity_l}',
                                              callback_data=f'shipment_id_{shipment.id}'))
    return keyboard.adjust(1).as_markup()


async def all_cheques():
    keyboard = InlineKeyboardBuilder()
    cheques = await cheque_rq.get_all_cheques()
    for cheque in cheques:
        shipment = await ship_rq.get_shipment(cheque.shipment_id)
        if await half_year_check(cheque.date) and cheque.cheque_status != 'Чек оплачен':
            keyboard.add(InlineKeyboardButton(text=f'Цена: {cheque.price}$ S: {shipment.quantity_s} M: {shipment.quantity_m}'
                                                   f' L: {shipment.quantity_l}',
                                              callback_data=f'cheque_id_{cheque.id}'))
    return keyboard.adjust(1).as_markup()


async def all_fishes():
    keyboard = InlineKeyboardBuilder()
    fishes = await fish_rq.get_all_fishes()
    for fish in fishes:
        shipment = await ship_rq.get_shipment(fish.shipment_id)
        if await half_year_check(fish.fish_date) and shipment.status != 'Принята на складе WB':
            date = datetime.strptime(fish.fish_date, '%d-%m-%Y %H:%M:%S')
            str_date = datetime.strftime(date, '%d-%m-%Y')
            keyboard.add(InlineKeyboardButton(text=f'Дата {str_date} S: {shipment.quantity_s} M: {shipment.quantity_m}'
                                                   f' L: {shipment.quantity_l}',
                                              callback_data=f'fish_id_{fish.id}'))
    return keyboard.adjust(1).as_markup()