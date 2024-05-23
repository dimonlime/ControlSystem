from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime, timedelta
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app import id_config
from app.database import requests as rq
from app.utils.utils import half_year_check, half_year_check_cheques


async def inline_sending_method():
    keyboard = InlineKeyboardBuilder()
    for method in id_config.sending_method:
        keyboard.add(InlineKeyboardButton(text=method, callback_data=f'method_{method}'))
    return keyboard.adjust(3).as_markup()


async def inline_order_status():
    keyboard = InlineKeyboardBuilder()
    for status in id_config.order_status:
        keyboard.add(InlineKeyboardButton(text=status, callback_data=f'status_{status}'))
    return keyboard.adjust(1).as_markup()


async def inline_all_orders(income_id):
    keyboard = InlineKeyboardBuilder()
    data = await rq.all_orders()
    for order in data:
        if await half_year_check(order.date):
            if (order.delivery_id == income_id and order.order_status != 'Передан в логистику' and
                    order.order_status not in id_config.ru_order_status):
                keyboard.add(InlineKeyboardButton(
                    text=f'Арт: "{order.internal_article}", S: {order.S}, M: {order.M}, L: {order.L}',
                    callback_data=f'edit_status_{order.id}'))
    return keyboard.adjust(1).as_markup()


async def inline_all_cheques():
    keyboard = InlineKeyboardBuilder()
    data = await rq.all_cheques()
    for cheque in data:
        if await half_year_check_cheques(cheque.cheque_date):
            keyboard.add(InlineKeyboardButton(text=f'Номер чека: "{cheque.cheque_number}", Цена: "{cheque.price}"',
                                              callback_data=f'pay_cheque_{cheque.id}'))
    return keyboard.adjust(1).as_markup()


async def inline_delay_cheques():
    keyboard = InlineKeyboardBuilder()
    data = await rq.delay_cheques()
    for cheque in data:
        if await half_year_check_cheques(cheque.cheque_date):
            keyboard.add(InlineKeyboardButton(text=f'Номер чека: "{cheque.cheque_number}", Цена: "{cheque.price}"',
                                              callback_data=f'pay_cheque_{cheque.id}'))
    return keyboard.adjust(1).as_markup()


async def inline_fire_cheques():
    keyboard = InlineKeyboardBuilder()
    data = await rq.all_cheques()
    for cheque in data:
        if await half_year_check_cheques(cheque.cheque_date):
            if cheque.cheque_status == 'Чек не оплачен по истечению 2 недель':
                keyboard.add(InlineKeyboardButton(text=f'Номер чека: "{cheque.cheque_number}", Цена: "{cheque.price}"',
                                                  callback_data=f'pay_cheque_{cheque.id}'))
    return keyboard.adjust(1).as_markup()


async def inline_unpaid_cheques():
    keyboard = InlineKeyboardBuilder()
    data = await rq.all_cheques()
    for cheque in data:
        if await half_year_check_cheques(cheque.cheque_date):
            if cheque.cheque_status == 'По чеку имеется отсрочка' or cheque.cheque_status == 'Чек не оплачен по истечению 2 недель':
                keyboard.add(InlineKeyboardButton(text=f'Номер чека: "{cheque.cheque_number}", Цена: "{cheque.price}"',
                                                  callback_data=f'view_cheque_{cheque.id}'))
    return keyboard.adjust(1).as_markup()


async def inline_paid_cheques():
    keyboard = InlineKeyboardBuilder()
    data = await rq.all_cheques()
    for cheque in data:
        if await half_year_check_cheques(cheque.cheque_date):
            if cheque.cheque_status == 'Чек оплачен':
                keyboard.add(InlineKeyboardButton(text=f'Номер чека: "{cheque.cheque_number}", Цена: "{cheque.price}"',
                                                  callback_data=f'view_cheque_{cheque.id}'))
    return keyboard.adjust(1).as_markup()


async def inline_all_orders_send(income_id):
    keyboard = InlineKeyboardBuilder()
    data = await rq.all_orders()
    for order in data:
        if await half_year_check(order.date):
            if order.delivery_id == income_id:
                keyboard.add(InlineKeyboardButton(
                    text=f'Арт: "{order.internal_article}", S: {order.S}, M: {order.M}, L: {order.L}',
                    callback_data=f'get_info_{order.id}'))
    return keyboard.adjust(1).as_markup()


async def inline_all_orders_by_status(income_id, order_status):
    keyboard = InlineKeyboardBuilder()
    data = await rq.get_orders_by_income_id(income_id)
    for order in data:
        if await half_year_check(order.date):
            if order.delivery_id == income_id and order.order_status == order_status:
                keyboard.add(InlineKeyboardButton(
                    text=f'Арт: "{order.internal_article}", S: {order.S}, M: {order.M}, L: {order.L}',
                    callback_data=f'get_info_{order.id}'))
    return keyboard.adjust(1).as_markup()


async def inline_all_orders_status(income_id):
    keyboard = InlineKeyboardBuilder()
    data = await rq.get_orders_by_income_id(income_id)
    status = []
    keyboard.add(InlineKeyboardButton(text=f'Все заказы',
                                      callback_data=f'orders_all'))
    for order in data:
        if await half_year_check(order.date):
            if order.order_status not in status:
                status.append(order.order_status)
                keyboard.add(InlineKeyboardButton(text=f'{order.order_status}',
                                                  callback_data=f'order_status_{order.order_status}'))
    return keyboard.adjust(1).as_markup()


async def all_incomes():
    keyboard = InlineKeyboardBuilder()
    data = await rq.all_orders()
    incomes = []
    for order in data:
        if await half_year_check(order.date):
            if order.delivery_id not in incomes:
                incomes.append(order.delivery_id)
                keyboard.add(InlineKeyboardButton(text=f'ID: {order.delivery_id} Дата: {order.delivery_date}',
                                                  callback_data=f'income_all_{order.delivery_id}'))
    return keyboard.adjust(1).as_markup()


async def all_incomes_recipients():
    keyboard = InlineKeyboardBuilder()
    data = await rq.all_orders()
    incomes = []
    for order in data:
        if await half_year_check(order.date):
            if (order.delivery_id not in incomes and order.order_status != 'Передан в логистику' and
                    order.order_status not in id_config.ru_order_status):
                incomes.append(order.delivery_id)
                keyboard.add(InlineKeyboardButton(text=f'ID: {order.delivery_id} Дата: {order.delivery_date}',
                                                  callback_data=f'income_rec{order.delivery_id}'))
    return keyboard.adjust(1).as_markup()


async def all_articles():
    keyboard = InlineKeyboardBuilder()
    data = await rq.all_orders()
    articles = []
    for order in data:
        if await half_year_check(order.date):
            if order.internal_article not in articles:
                articles.append(order.internal_article)
    for article in articles:
        keyboard.add(InlineKeyboardButton(text=f'Артикул: {article}',
                                          callback_data=f'article_{article}'))
    return keyboard.adjust(1).as_markup()


async def all_articles_table():
    keyboard = InlineKeyboardBuilder()
    articles = await rq.get_product_cards()
    for article in articles:
        keyboard.add(InlineKeyboardButton(text=f'Артикул: {article.article}',
                                          callback_data=f'article_{article.article}'))
    return keyboard.adjust(1).as_markup()


async def all_incomes_senders():
    keyboard = InlineKeyboardBuilder()
    data = await rq.all_orders()
    incomes = []
    for order in data:
        if await half_year_check(order.date):
            if order.delivery_id not in incomes and (
                    order.order_status == 'Передан в логистику' or order.order_status in id_config.ru_order_status) \
                    and order.order_status != 'Принято на складе WB':
                incomes.append(order.delivery_id)
                keyboard.add(InlineKeyboardButton(text=f'ID: {order.delivery_id} Дата: {order.delivery_date}',
                                                  callback_data=f'income_send_{order.delivery_id}'))
    return keyboard.adjust(1).as_markup()


async def inline_all_orders_ru(income_id):
    keyboard = InlineKeyboardBuilder()
    data = await rq.all_orders()
    for order in data:
        if await half_year_check(order.date):
            if order.delivery_id == income_id and (
                    order.order_status == 'Передан в логистику' or order.order_status in id_config.ru_order_status) \
                    and order.order_status != 'Принято на складе WB':
                keyboard.add(InlineKeyboardButton(
                    text=f'Арт: "{order.internal_article}", S: {order.S}, M: {order.M}, L: {order.L}',
                    callback_data=f'ru_edit_status_{order.id}'))
    return keyboard.adjust(1).as_markup()


async def inline_ru_order_status():
    keyboard = InlineKeyboardBuilder()
    for status in id_config.ru_order_status:
        keyboard.add(InlineKeyboardButton(text=status, callback_data=f'ru_status_{status}'))
    return keyboard.adjust(1).as_markup()


async def all_orders():
    keyboard = InlineKeyboardBuilder()
    orders = await rq.all_orders()
    order_data = {}
    unique_orders = []
    for order in orders:
        if order.internal_article not in order_data.keys():
            order_data[order.internal_article] = {
                'S': order.S,
                'M': order.M,
                'L': order.L,
            }
        else:
            order_data[order.internal_article]['S'] += order.S
            order_data[order.internal_article]['M'] += order.S
            order_data[order.internal_article]['L'] += order.S
    orders = await rq.all_orders()
    for order in orders:
        if order.internal_article not in unique_orders:
            keyboard.add(InlineKeyboardButton(
                text=f'АРТ: {order.internal_article}, S: {str(order_data[order.internal_article]['S'])} '
                     f'M: {str(order_data[order.internal_article]['M'])} '
                     f'L: {str(order_data[order.internal_article]['L'])}', callback_data=f'order_id_{order.id}'))
        unique_orders.append(order.internal_article)
    return keyboard.adjust(1).as_markup()

