from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime, timedelta
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app import id_config
from app.database import requests as rq


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
        today_date = datetime.now()
        half_year = today_date - timedelta(days=365 / 2)
        order_date = datetime.strptime(order.date, "%d-%m-%Y %H:%M:%S")
        if half_year <= order_date <= today_date:
            if order.delivery_id == income_id:
                keyboard.add(InlineKeyboardButton(text=f'Арт: "{order.internal_article}", Дата: "{order.date}"',
                                                  callback_data=f'edit_status_{order.id}'))
    return keyboard.adjust(1).as_markup()


async def inline_all_cheques():
    keyboard = InlineKeyboardBuilder()
    data = await rq.all_cheques()
    for cheque in data:
        today_date = datetime.now()
        half_year = today_date - timedelta(days=365 / 2)
        cheque_date = datetime.strptime(cheque.cheque_date, "%d-%m-%Y %H:%M")
        if half_year <= cheque_date <= today_date:
            keyboard.add(InlineKeyboardButton(text=f'Номер чека: "{cheque.cheque_number}", Цена: "{cheque.price}"',
                                              callback_data=f'pay_cheque_{cheque.id}'))
    return keyboard.adjust(1).as_markup()


async def inline_delay_cheques():
    keyboard = InlineKeyboardBuilder()
    data = await rq.delay_cheques()
    for cheque in data:
        today_date = datetime.now()
        half_year = today_date - timedelta(days=365 / 2)
        cheque_date = datetime.strptime(cheque.cheque_date, "%d-%m-%Y %H:%M")
        if half_year <= cheque_date <= today_date:
            keyboard.add(InlineKeyboardButton(text=f'Номер чека: "{cheque.cheque_number}", Цена: "{cheque.price}"',
                                              callback_data=f'pay_cheque_{cheque.id}'))
    return keyboard.adjust(1).as_markup()


async def inline_fire_cheques():
    keyboard = InlineKeyboardBuilder()
    data = await rq.all_cheques()
    for cheque in data:
        cheque_date = datetime.strptime(cheque.cheque_date, "%d-%m-%Y %H:%M")
        today_date = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        today_date_valid = datetime.strptime(today_date, "%d-%m-%Y %H:%M:%S")
        half_year = today_date_valid - timedelta(days=365 / 2)
        if half_year <= cheque_date <= today_date_valid:
            if cheque.cheque_status == 'Чек не оплачен по истечению 2 недель':
                keyboard.add(InlineKeyboardButton(text=f'Номер чека: "{cheque.cheque_number}", Цена: "{cheque.price}"',
                                                  callback_data=f'pay_cheque_{cheque.id}'))
    return keyboard.adjust(1).as_markup()


async def inline_unpaid_cheques():
    keyboard = InlineKeyboardBuilder()
    data = await rq.all_cheques()
    for cheque in data:
        today_date = datetime.now()
        half_year = today_date - timedelta(days=365 / 2)
        cheque_date = datetime.strptime(cheque.cheque_date, "%d-%m-%Y %H:%M")
        if half_year <= cheque_date <= today_date:
            if cheque.cheque_status == 'По чеку имеется отсрочка' or cheque.cheque_status == 'Чек не оплачен по истечению 2 недель':
                keyboard.add(InlineKeyboardButton(text=f'Номер чека: "{cheque.cheque_number}", Цена: "{cheque.price}"',
                                                  callback_data=f'view_cheque_{cheque.id}'))
    return keyboard.adjust(1).as_markup()


async def inline_paid_cheques():
    keyboard = InlineKeyboardBuilder()
    data = await rq.all_cheques()
    for cheque in data:
        today_date = datetime.now()
        half_year = today_date - timedelta(days=365 / 2)
        cheque_date = datetime.strptime(cheque.cheque_date, "%d-%m-%Y %H:%M")
        if half_year <= cheque_date <= today_date:
            if cheque.cheque_status == 'Чек оплачен':
                keyboard.add(InlineKeyboardButton(text=f'Номер чека: "{cheque.cheque_number}", Цена: "{cheque.price}"',
                                                  callback_data=f'view_cheque_{cheque.id}'))
    return keyboard.adjust(1).as_markup()


async def inline_all_orders_send(income_id):
    keyboard = InlineKeyboardBuilder()
    data = await rq.all_orders()
    for order in data:
        today_date = datetime.now()
        half_year = today_date - timedelta(days=365 / 2)
        order_date = datetime.strptime(order.date, "%d-%m-%Y %H:%M:%S")
        if half_year <= order_date <= today_date:
            if order.delivery_id == income_id:
                keyboard.add(InlineKeyboardButton(text=f'Арт: "{order.internal_article}"; Дата: "{order.date}"',
                                                  callback_data=f'get_info_{order.id}'))
    return keyboard.adjust(1).as_markup()


async def inline_all_orders_by_status(income_id, order_status):
    keyboard = InlineKeyboardBuilder()
    data = await rq.get_orders_by_income_id(income_id)
    for order in data:
        today_date = datetime.now()
        half_year = today_date - timedelta(days=365 / 2)
        order_date = datetime.strptime(order.date, "%d-%m-%Y %H:%M:%S")
        if half_year <= order_date <= today_date:
            if order.delivery_id == income_id and order.order_status == order_status:
                keyboard.add(InlineKeyboardButton(text=f'Арт: "{order.internal_article}"; Дата: "{order.date}"',
                                                  callback_data=f'get_info_{order.id}'))
    return keyboard.adjust(1).as_markup()


async def inline_all_orders_status(income_id):
    keyboard = InlineKeyboardBuilder()
    data = await rq.get_orders_by_income_id(income_id)
    status = []
    keyboard.add(InlineKeyboardButton(text=f'Все заказы',
                                      callback_data=f'orders_all'))
    for order in data:
        today_date = datetime.now()
        half_year = today_date - timedelta(days=365 / 2)
        order_date = datetime.strptime(order.date, "%d-%m-%Y %H:%M:%S")
        if half_year <= order_date <= today_date:
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
        today_date = datetime.now()
        half_year = today_date - timedelta(days=365 / 2)
        order_date = datetime.strptime(order.date, "%d-%m-%Y %H:%M:%S")
        if half_year <= order_date <= today_date:
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
        today_date = datetime.now()
        half_year = today_date - timedelta(days=365 / 2)
        order_date = datetime.strptime(order.date, "%d-%m-%Y %H:%M:%S")
        if half_year <= order_date <= today_date:
            if order.delivery_id not in incomes:
                incomes.append(order.delivery_id)
                keyboard.add(InlineKeyboardButton(text=f'ID: {order.delivery_id} Дата: {order.delivery_date}',
                                                  callback_data=f'income_rec{order.delivery_id}'))
    return keyboard.adjust(1).as_markup()


async def all_articles():
    keyboard = InlineKeyboardBuilder()
    data = await rq.all_orders()
    articles = []
    for order in data:
        today_date = datetime.now()
        half_year = today_date - timedelta(days=365 / 2)
        order_date = datetime.strptime(order.date, "%d-%m-%Y %H:%M:%S")
        if half_year <= order_date <= today_date:
            if order.internal_article not in articles:
                articles.append(order.internal_article)
    for article in articles:
        keyboard.add(InlineKeyboardButton(text=f'Артикул: {article}',
                                          callback_data=f'article_{article}'))
    return keyboard.adjust(1).as_markup()
